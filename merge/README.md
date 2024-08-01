<div align="center">    
 
# Code for merging a fine-tuned LoRA adapter with a Pre-trained model

</div>

Example of merging code

## Example
You can merge the fine-tuned LoRA adapter with a Pre-trained model by modifying the shell script below.

```{shell}
python3 merge.py --model_path '/Llama-2-7b-hf' \
--adapter_path '../train/adapters/project/checkpoint-1000' \
--output_dir './models/PathoIE-1000step' \
--is_chatlm
```

- model_path
  - Directory path where the downloaded pre-trained model is stored
- adapter_path
  - Directory path where the fine-tuned LoRA adapter is stored
- output_dir
  - Used for setting the save path


