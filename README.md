<div align="center">    
 
# Extracting lung cancer staging descriptors from pathology reports: a generative language model approach     

[![DOI](https://img.shields.io/badge/DOI-10.1016/j.jbi.2024.104720-red)](https://doi.org/10.1016/j.jbi.2024.104720)
[![Volume](https://img.shields.io/badge/Volume-157-blue)](https://www.sciencedirect.com/science/article/pii/S1532046424001382)
[![Journal](https://img.shields.io/badge/Journal-JBI-purple)](https://www.sciencedirect.com/journal/journal-of-biomedical-informatics)
[![ISSN](https://img.shields.io/badge/ISSN-1532_0464-green)](https://www.sciencedirect.com/science/article/pii/S1532046424001382)

   
</div>

This repository provides *Training/Evaluation code* and *Trained model* presented in our paper
"Extracting lung cancer staging descriptors from pathology reports: a generative language model approach"


## Requirements
> - transformer >= 4.34.0
> - torch >= 2.0.1
> - peft >= 0.4.0
> - vllm >= 0.2.1.post1

## Getting Started
``` python
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

# Load base model
base_model = AutoModelForCausalLM.from_pretrained(
    'cognitivecomputations/dolphin-2.1-mistral-7b',
    trust_remote_code=True,
    device_map="auto",
    torch_dtype=torch.bfloat16,   # Optional, if you have insufficient VRAM, lower the precision.
)

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained('cognitivecomputations/dolphin-2.1-mistral-7b')

# Load PEFT
model = PeftModel.from_pretrained(base_model, 'Lowenzahn/PathoIE-Dolphin-7B')
model = model.merge_and_unload()
model = model.eval()

# Inference
prompts = ["Machine learning is"]
inputs = tokenizer(prompts, return_tensors="pt")
gen_kwargs = {"max_new_tokens": 1024, "top_p": 0.8, "temperature": 0.0, "do_sample": False, "repetition_penalty": 1.0}
output = model.generate(inputs['input_ids'], **gen_kwargs)
output = tokenizer.decode(output[0].tolist(), skip_special_tokens=True)
print(output)
```

## Model
You can download the LoRA Adaptor of trained models.

| Trained Model                                                                                                                       | Base Model                                                                                      |
|-------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------|
| [<div align="center"> PathoIE-Llama-2-7B <br> (Llama-2-7B) </div>](https://huggingface.co/Lowenzahn/PathoIE-Llama-2-7B)             | [Llama-2-7B](https://huggingface.co/meta-llama/Llama-2-7b-hf)                                   |
| [<div align="center"> PathoIE-Mistral-7B <br> (Mistral-7B) </div>](https://huggingface.co/Lowenzahn/PathoIE-Mistral-7B)             | [Mistral-7B](https://huggingface.co/mistralai/Mistral-7B-v0.1)                                  |
| [<div align="center"> PathoIE-Orca-2-7B <br> (Deductive Llama-2-7B) </div>](https://huggingface.co/Lowenzahn/PathoIE-Orca-2-7B)     | [Orca-2-7B](https://huggingface.co/microsoft/Orca-2-7b)                                         |
| [<div align="center"> * PathoIE-Dolphin-7B <br> (Deductive Mistral-7B) </div>](https://huggingface.co/Lowenzahn/PathoIE-Dolphin-7B) | [Dolphin-2.1-Mistral-7B](https://huggingface.co/cognitivecomputations/dolphin-2.1-mistral-7b)   |


### Citation
```
@article{cho2024ie,
    title={Extracting lung cancer staging descriptors from pathology reports: a generative language model approach},
    author={Hyeongmin Cho, Sooyoung Yoo, Borham Kim, Sowon Jang, Leonard Sunwoo, Sanghwan Kim, Donghyoung Lee, Seok Kim, Sejin Nam, Jin-Haeng Chung},
    journal={Journal of Biomedical Informatics},
    volume={157},
    year={2024},
    publisher={Elsevier},
    issn={1532-0464},
    doi={10.1016/j.jbi.2024.104720},
    url={https://doi.org/10.1016/j.jbi.2024.104720}
}
```