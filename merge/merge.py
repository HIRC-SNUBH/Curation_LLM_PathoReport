import os
import torch
from transformers import AutoTokenizer, AutoConfig, AutoModelForCausalLM, AddedToken
from peft import PeftModel
import argparse
from time import time


def main(args):
    print('Loading Pretrained Model...')
    stime = time()
    model = AutoModelForCausalLM.from_pretrained(
        args.model_path,
        device_map=args.device_map  
    )
    print(f'Pretrained Model loaded: {time()-stime}')
    print('='*150)
    
    tokenizer = AutoTokenizer.from_pretrained(args.model_path, add_bos_token=True, trust_remote_code=True)

    if not args.is_chatlm:
        print('Args is_chatlm:', args.is_chatlm)
        print('Setting Tokenizer and Model...')
        print('='*150)
        tokenizer.add_special_tokens(dict(
            eos_token=AddedToken("<|im_end|>", single_word=False, lstrip=False, rstrip=False, normalized=True, special=True),
            unk_token=AddedToken("<unk>", single_word=False, lstrip=False, rstrip=False, normalized=True, special=True),
            bos_token=AddedToken("<s>", single_word=False, lstrip=False, rstrip=False, normalized=True, special=True),
            pad_token=AddedToken("</s>", single_word=False, lstrip=False, rstrip=False, normalized=False, special=True),
        ))
        
        tokenizer.add_tokens([AddedToken("<|im_start|>", single_word=False, lstrip=True, rstrip=True, normalized=False)], special_tokens=True)
        tokenizer.additional_special_tokens = ['<unk>', '<s>', '</s>', '<|im_end|>', '<|im_start|>']
        
        model.resize_token_embeddings(len(tokenizer))
        model.config.eos_token_id = tokenizer.eos_token_id


    print('Loading PEFT Model...')
    stime = time()
    model = PeftModel.from_pretrained(model, args.adapter_path)
    model.eval()
    print(f'PEFT Model loaded: {time()-stime}')
    print('='*150)


    print('Merging Pretrained Model and Adapter...')
    stime = time()
    model = model.merge_and_unload() # To speed up inference, revert to the original structure as vllm doesn't support PEFT.
    print(f'Merging Finished: {time()-stime}')
    print('='*150)

    
    print('Saving Model and Tokenizer...')
    stime = time()
    model.save_pretrained(
        args.output_dir,
        dtype=torch.bfloat16,
    )
    tokenizer.save_pretrained(
        args.output_dir,
        dtype=torch.bfloat16,
    )
    print(f'Saving Finished: {time()-stime}')
    print('='*150)


if __name__=='__main__':
    parser = argparse.ArgumentParser(description="Arguments")
    parser.add_argument('--model_path', '-mpath', type=str, help='Model path')
    parser.add_argument('--adapter_path', '-apath', type=str, help='Adapter path')
    parser.add_argument('--output_dir', '-output', type=str, help='Save directory path')
    parser.add_argument('--device_map', '-dmap', type=str, default='auto', help='HuggingFace Device map')
    parser.add_argument('--is_chatlm', '-clm', action='store_true', help='Does Model supports ChatLM Format?')
    
    args = parser.parse_args()
    os.makedirs(args.output_dir, exist_ok=True)

    main(args)