<div align="center">    
 
# Codes to evaluate a fine-tuned model

</div>

Example of evaluation codes

## Example
You can evaluate the model by modifying the shell script below.

``` shell
python3 eval.py --result_path 'PATH_TO_GENERATION_RESULTS' \
--output_dir 'SAVE_PATH'
```
- result_path
  - The file path where the generated results from the model are stored
- output_dir
  - Used for setting the save path

## Saving results
You should save the generated results as follows.

``` python
from utils import save_data

results = ... # List[str] type, ['generation1', 'generation2']
save_data(results, 'my_data.pkl')
```


