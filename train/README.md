<div align="center">    
 
# Fine-tuning codes with PEFT

</div>

Example of fine-tuning code

# Example
You can fine-tune the pre-trained model by modifying the shell script below.

```{shell}
python3 finetune_llm.py --dataset_path "./train_dataset.jsonl" \
--model_path "/Llama-2-7b-hf" \
--project "fine-tune-ie" \
--base_model_name "my-llama" \
--device_map "auto" \
--is_chatlm \
--seed 0 \
--val_ratio 0.2 \
--lora_alpha 32 \
--lora_gamma 32 \
--max_steps 4000 \
--accumulation_step 4 \
--per_device_train_batch 2 \
--per_device_eval_batch 2 \
--save_steps 100 \
--eval_steps 100 \
--log_steps 10 \
--bf16 \
--learning_rate 0.000015
```
- dataset_path
  - Path to the prepared training dataset in JSONL format
  - > format: {'input': ..., 'output': ...}
- model_path
  - Directory path where the downloaded pre-trained model is stored
- project
  - Used for setting the save path
- base_model_name
  - Used for setting the save path


