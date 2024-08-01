python3 finetune_llm.py --dataset_path "PATH_TO_JSONL_FILE" \
--model_path "PATH_TO_PRETRAINED_MODEL" \
--project "PROJECT_NAME" \
--base_model_name "BASE_MODEL_NAME" \
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
