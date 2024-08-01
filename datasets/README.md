<div align="center">    
 
# Example of dataset

</div>

Training & Inference dataset format

## Dataset Example
For training, the dataset should be structured in JSONL.
```
{'input': ..., 'output': ...}
{'input': ..., 'output': ...}
...
```

## Prompt Example
For training & inference, the prompt should be structured as follows.
```
<|im_start|> system
    You are a pathologist who specialized in lung cancer.
    Your task is extracting informations requested by the user from the lung cancer pathology report and formatting extracted informations into JSON.
    The information to be extracted is clearly specified in the report, so one must avoid from inferring information that is not present.
    Remember, you MUST answer in JSON only. Avoid any additional explanations.
<|im_end|>
<|im_start|> user
    Extract the following informations (value-set) from the report I provide.
    If the required information to extract each value in the value-set is not present in the pathology report, consider it as 'not submitted'.
    <value-set>
    - MORPHOLOGY_DIAGNOSIS
    - SUBTYPE_DOMINANT
    - MAX_SIZE_OF_TUMOR(invasive component only)
    - MAX_SIZE_OF_TUMOR(including CIS=AIS)
    - INVASION_TO_VISCERAL_PLEURAL
    - MAIN_BRONCHUS
    - INVASION_TO_CHEST_WALL
    - INVASION_TO_PARIETAL_PLEURA
    - INVASION_TO_PERICARDIUM
    - INVASION_TO_PHRENIC_NERVE
    - TUMOR_SIZE_CNT
    - LUNG_TO_LUNG_METASTASIS
    - INTRAPULMONARY_METASTASIS
    - SATELLITE_TUMOR_LOCATION
    - SEPARATE_TUMOR_LOCATION
    - INVASION_TO_MEDIASTINUM
    - INVASION_TO_DIAPHRAGM
    - INVASION_TO_HEART
    - INVASION_TO_RECURRENT_LARYNGEAL_NERVE
    - INVASION_TO_TRACHEA
    - INVASION_TO_ESOPHAGUS
    - INVASION_TO_SPINE
    - METASTATIC_RIGHT_UPPER_LOBE
    - METASTATIC_RIGHT_MIDDLE_LOBE
    - METASTATIC_RIGHT_LOWER_LOBE
    - METASTATIC_LEFT_UPPER_LOBE
    - METASTATIC_LEFT_LOWER_LOBE
    - INVASION_TO_AORTA
    - INVASION_TO_SVC
    - INVASION_TO_IVC
    - INVASION_TO_PULMONARY_ARTERY
    - INVASION_TO_PULMONARY_VEIN
    - INVASION_TO_CARINA
    - PRIMARY_CANCER_LOCATION_RIGHT_UPPER_LOBE
    - PRIMARY_CANCER_LOCATION_RIGHT_MIDDLE_LOBE
    - PRIMARY_CANCER_LOCATION_RIGHT_LOWER_LOBE
    - PRIMARY_CANCER_LOCATION_LEFT_UPPER_LOBE
    - PRIMARY_CANCER_LOCATION_LEFT_LOWER_LOBE
    - RELATED_TO_ATELECTASIS_OR_OBSTRUCTIVE_PNEUMONITIS
    - PRIMARY_SITE_LATERALITY
    - LYMPH_METASTASIS_SITES
    - NUMER_OF_LYMPH_NODE_META_CASES
---
<report>
[A] Lung, left lower lobe, lobectomy
1. ADENOSQUAMOUS CARCINOMA, acinar predominant [by 2015 WHO classification]
- other subtype: lepidic (30%)
    1) Pre-operative / Previous treatment: not done
    2) Histologic grade: moderately differentiated
    3) Size of tumor:
        a. Invasive component only: 3.5 x 2.5 x 1.3 cm
        b. Including CIS component: 3.9 x 2.6 x 1.3 cm
    ...
<|im_end|>
<|im_start|> pathologist

```




