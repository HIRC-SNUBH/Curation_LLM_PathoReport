<div align="center">    
 
# Extracting lung cancer staging descriptors from pathology reports: a generative language model approach     

[![DOI](https://img.shields.io/badge/UnderReview-red)](https://google.com)
[![Pages](https://img.shields.io/badge/UnderReview-blue)](https://google.com)
[![Volume](https://img.shields.io/badge/UnderReview-green)](https://google.com)
[![Journal](https://img.shields.io/badge/UnderReview-purple)](https://google.com)

   
</div>

This repository provides *Training/Evaluation code* and *Trained model* presented in our paper
"Extracting lung cancer staging descriptors from pathology reports: a generative language model approach"

You can see our paper at 
[Not determined]().


## Requirements
> - transformer >= 4.34.0
> - torch >= 2.0.1
> - peft >= 0.4.0
> - vllm >= 0.2.1.post1

## Getting Started
ToDo.

## Model
You can download the LoRA Adaptor of trained models.

| Trained Model                                                                                                                       | Base Model                                                                                      | Size   |
|-------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------|--------|
| [<div align="center"> PathoIE-Llama-2-7B <br> (Llama-2-7B) </div>](https://huggingface.co/Lowenzahn/PathoIE-Llama-2-7B)             | [Llama-2-7B](https://huggingface.co/meta-llama/Llama-2-7b-hf)                                   | 1.4 GB |
| [<div align="center"> PathoIE-Mistral-7B <br> (Mistral-7B) </div>](https://huggingface.co/Lowenzahn/PathoIE-Mistral-7B)             | [Mistral-7B](https://huggingface.co/mistralai/Mistral-7B-v0.1)                                  | 1.4 GB |
| [<div align="center"> PathoIE-Orca-2-7B <br> (Deductive Llama-2-7B) </div>](https://huggingface.co/Lowenzahn/PathoIE-Orca-2-7B)     | [Orca-2-7B](https://huggingface.co/microsoft/Orca-2-7b)                                         | 0.4 GB |
| [<div align="center"> * PathoIE-Dolphin-7B <br> (Deductive Mistral-7B) </div>](https://huggingface.co/Lowenzahn/PathoIE-Dolphin-7B) | [Dolphin-2.1-Mistral-7B](https://huggingface.co/cognitivecomputations/dolphin-2.1-mistral-7b)   | 0.4 GB |


## Abstract

> This paper ~


### Citation
```
@article{cho2024ie,
    title={Extracting lung cancer staging descriptors from pathology reports: a generative language model approach},
    author={Hyeongmin Cho and Sooyoung Yoo and Borham Kim and Sowon Jang and Leonard Sunwoo and Sanghwan Kim and Donghyoung Lee and Seok Kim and Sejin Nam and Jin-Haeng Chung},
    journal={},
    volume={},
    pages={},
    year={},
    publisher={},
    issn={},
    doi={},
    url={}
}
```