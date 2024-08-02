import warnings
warnings.filterwarnings("ignore")

import os
import argparse
import torch
import transformers
from transformers import AutoTokenizer, AutoModelForCausalLM, AddedToken
from datasets import load_dataset, Dataset
from peft import prepare_model_for_int8_training, LoraConfig, get_peft_model
from accelerate import FullyShardedDataParallelPlugin, Accelerator
from torch.distributed.fsdp.fully_sharded_data_parallel import FullOptimStateDictConfig, FullStateDictConfig

def formatting_func(example) -> str:
    text = f"{example['input']}{example['output']}"
    return text

def print_trainable_parameters(model) -> None:
    """
    Prints the number of trainable parameters in the model.
    """
    trainable_params = 0
    all_param = 0
    for _, param in model.named_parameters():
        all_param += param.numel()
        if param.requires_grad:
            trainable_params += param.numel()
    print(
        f"trainable params: {trainable_params} || all params: {all_param} || trainable%: {100 * trainable_params / all_param}"
    )


def get_datasets(dataset_path:str, tokenizer, val_ratio=0.2, seed=0):
    dataset = Dataset.from_json(dataset_path)
    dataset = dataset.train_test_split(test_size=val_ratio, seed=seed)
    train_dataset = dataset['train']
    eval_dataset = dataset['test']

    def generate_and_tokenize_prompt(prompt):
        return tokenizer(formatting_func(prompt), padding='longest')
    
    tokenized_train_dataset = train_dataset.map(generate_and_tokenize_prompt)
    tokenized_val_dataset = eval_dataset.map(generate_and_tokenize_prompt)
    
    return tokenized_train_dataset, tokenized_val_dataset


def get_tokenizer(model_path:str, is_ChatLM=False):
    tokenizer = AutoTokenizer.from_pretrained(model_path, padding_side="left", add_eos_token=True, add_bos_token=True)

    if is_ChatLM:
        print('Loading ChatLM format tokenizer...')
        tokenizer.pad_token = '</s>'
    else:
        print('Loading None-ChatLM format tokenizer...')
        tokenizer.add_special_tokens(dict(
            eos_token=AddedToken("<|im_end|>", single_word=False, lstrip=False, rstrip=False, normalized=True, special=True),
            unk_token=AddedToken("<unk>", single_word=False, lstrip=False, rstrip=False, normalized=True, special=True),
            bos_token=AddedToken("<s>", single_word=False, lstrip=False, rstrip=False, normalized=True, special=True),
            pad_token=AddedToken("</s>", single_word=False, lstrip=False, rstrip=False, normalized=False, special=True),
        ))
        tokenizer.add_tokens([AddedToken("<|im_start|>", single_word=False, lstrip=True, rstrip=True, normalized=False)], special_tokens=True)
        tokenizer.additional_special_tokens = ['<unk>', '<s>', '</s>', '<|im_end|>', '<|im_start|>']

    return tokenizer


def get_lora_config(alpha, gamma, dropout, task_type, is_ChatLM):
    if is_ChatLM:
        return LoraConfig(
                    r=gamma,
                    lora_alpha=alpha,
                    target_modules=[
                        "q_proj",
                        "k_proj",
                        "v_proj",
                        "o_proj",
                        "gate_proj",
                        "up_proj",
                        "down_proj",
                        "lm_head",
                    ],
                    bias="none",
                    lora_dropout=dropout,
                    task_type=task_type,
                )
    else:
        return LoraConfig(
                    r=gamma,
                    lora_alpha=alpha,
                    target_modules=[
                        "q_proj",
                        "k_proj",
                        "v_proj",
                        "o_proj",
                        "gate_proj",
                        "up_proj",
                        "down_proj",
                    ],
                    bias="none",
                    modules_to_save = ["lm_head", "embed_tokens"], # for added tokens
                    lora_dropout=dropout,
                    task_type=task_type,
                )


def main(args):
    print('='*150)
    print(f'Run Name:', args.run_name)
    print('='*150)
    print(f'is_ChatLM:{args.is_chatlm}')
    print(f'bf16:{args.bf16}')
    print('='*150)

    tokenizer = get_tokenizer(args.model_path, args.is_chatlm)
    
    model = AutoModelForCausalLM.from_pretrained(
        args.model_path,
        device_map=args.device_map
    )

    if not args.is_chatlm:
        model.resize_token_embeddings(len(tokenizer))
        model.config.eos_token_id = tokenizer.eos_token_id

    model.config.use_cache = False
    model.config.pretraining_tp = 1

    model.gradient_checkpointing_enable()
    model = prepare_model_for_int8_training(model)

    tokenized_train_dataset, tokenized_val_dataset = get_datasets(args.dataset_path, tokenizer, args.val_ratio, args.seed)
    print('Train, validation size:', len(tokenized_train_dataset), len(tokenized_val_dataset))
    print('='*150)
    

    print('Loading PEFT model...')
    lora_config = get_lora_config(args.lora_alpha, args.lora_gamma, args.lora_dropout, args.task_type, args.is_chatlm)
    model = get_peft_model(model, lora_config)
    print_trainable_parameters(model)

    # Prepare distributed training
    fsdp_plugin = FullyShardedDataParallelPlugin(
        state_dict_config=FullStateDictConfig(offload_to_cpu=True, rank0_only=False),
        optim_state_dict_config=FullOptimStateDictConfig(offload_to_cpu=True, rank0_only=False),
    )
    
    accelerator = Accelerator(fsdp_plugin=fsdp_plugin)

    model = accelerator.prepare_model(model)

    if torch.cuda.device_count() > 1: # If more than 1 GPU
        model.is_parallelizable = True
        model.model_parallel = True

    trainer = transformers.Trainer(
        model=model,
        train_dataset=tokenized_train_dataset,
        eval_dataset=tokenized_val_dataset,
        args=transformers.TrainingArguments(
            output_dir=args.output_dir,
            warmup_steps=args.warmup_steps,
            per_device_train_batch_size=args.per_device_train_batch,
            per_device_eval_batch_size=args.per_device_eval_batch,
            gradient_accumulation_steps=args.accumulation_step,
            eval_accumulation_steps=1,
            max_steps=args.max_steps,
            learning_rate=args.learning_rate,   # low lr for fine-tuning
            max_grad_norm = args.max_grad_norm,
            bf16=args.bf16,
            optim=args.optim,
            logging_steps=args.log_steps,
            logging_dir="./logs",
            save_strategy='steps',
            save_steps=args.save_steps,
            evaluation_strategy='steps',
            eval_steps=args.eval_steps,
            report_to='none',
            do_eval=True,
        ),
        data_collator=transformers.DataCollatorForLanguageModeling(tokenizer, mlm=False),
    )
    
    model.config.use_cache = False

    print('Trianing Start...')
    trainer.train()
    

if __name__== '__main__':
    parser = argparse.ArgumentParser(description="Arguments")
    parser.add_argument('--dataset_path', '-dpath', type=str, help='Dataset path')
    parser.add_argument('--model_path', '-mpath', type=str, help='Model path')
    parser.add_argument('--project', '-p', type=str, help='Current Project name')
    parser.add_argument('--base_model_name', '-n', type=str, help='Base model name')
    parser.add_argument('--device_map', '-dmap', type=str, default='auto', help='Device map')
    parser.add_argument('--is_chatlm', '-clm', action='store_true', help='Check True if your model pre-trained on ChatLM format')
    parser.add_argument('--seed', '-seed', type=int, default=0, help='Set seed')
    parser.add_argument('--val_ratio', '-vratio', type=float, default=0.2, help='Validation Ratio')
    parser.add_argument('--lora_alpha', '-la', type=int, default=32, help='LoRA Alpha')
    parser.add_argument('--lora_gamma', '-lg', type=int, default=32, help='LoRA Gamma')
    parser.add_argument('--lora_dropout', '-ld', type=float, default=0.05, help='LoRA dropout')
    parser.add_argument('--task_type', '-tt', type=str, default='CAUSAL_LM', help='Task Type')
    parser.add_argument('--save_steps', '-sstep', type=int, default=100, help='Save Steps')
    parser.add_argument('--eval_steps', '-estep', type=int, default=100, help='Evaluation Steps')
    parser.add_argument('--log_steps', '-lstep', type=int, default=10, help='Logging Step')
    parser.add_argument('--optim', '-opt', type=str, default='paged_adamw_32bit', help='Optimizer')
    parser.add_argument('--bf16', '-bf16', action='store_true', help='Weight type')
    parser.add_argument('--max_grad_norm', '-mgm', type=float, default=0.3, help='Maximum Gradient Norm')
    parser.add_argument('--learning_rate', '-lr', type=float, default=0.000015, help='Learning Rate')
    parser.add_argument('--max_steps', '-mstep', type=int, default=4000, help='Maximum Training Steps')
    parser.add_argument('--accumulation_step', '-accum_step', type=int, default=4, help='Accumulation Step')
    parser.add_argument('--per_device_eval_batch', '-pdeb', type=int, default=2, help='Per Device Eval Batch')
    parser.add_argument('--per_device_train_batch', '-pdtb', type=int, default=2, help='Per Device Train Batch')
    parser.add_argument('--warmup_steps', '-wstep', type=int, default=1, help='Warmup Steps')

    args = parser.parse_args()
    args.run_name = args.base_model_name + "-" + args.project
    args.output_dir = "./adapters/" + args.run_name
    
    if not os.path.isdir("./adapters"):
        os.mkdir("./adapters")

    main(args)