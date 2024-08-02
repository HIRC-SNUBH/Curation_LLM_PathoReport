import os
import pandas as pd
import re
from tn_classifier import StageClassifier
from utils import load_data
import ast
from tqdm import tqdm
import argparse

def ie_result_to_df(result, columns, regexes):
    df = pd.DataFrame(columns=columns)
    
    for idx, test_text in tqdm(enumerate(result)):
        result_dict = {}
        
        text_list = test_text.split('\n')
        for text in text_list:
            for reg in regexes:
                if reg == r"invasive\s*component\s*only":
                    col_name = 'MAX_SIZE_OF_TUMOR(invasive component only)'
                elif reg == r"including\s*CIS":
                    col_name = 'MAX_SIZE_OF_TUMOR(including CIS=AIS)'
                elif reg == r"LYMPH_METASTASIS_SITES":
                    col_name = 'SITE_OF_LYMPH_NODE_'
                else:
                    col_name = str(reg)
                    
                if re.search(reg, text, flags=re.I):
                    if ':' in text:
                        value = text.split(':')[-1].lower().strip()
                    else:
                        value = text.split('\t')[-1].lower().strip()
                    value = re.sub(r'\#', '', value)
                    value = re.sub(r'\"', '', value).rstrip(',')
                    if value == 'not submitted': continue

                    if reg == r"LYMPH_METASTASIS_SITES":
                        try:
                            lymph_list = ast.literal_eval(value)
                            result_dict['LYMPH_METASTASIS_SITES'] = sorted(list(set(lymph_list)))
                        except:
                            lymph_list = []

                        for lymph in lymph_list:
                            lymph_col_name = col_name+str(lymph).upper().lstrip('#').strip()
                            result_dict[lymph_col_name] = 'true'
                    else:    
                        result_dict[col_name] = value
                    break

        df.loc[idx] = result_dict
    return df


def tn_classification(dataframe):
    tn_llm_df = dataframe.copy()
    tn_llm_df = tn_llm_df.fillna('')
    
    llm_stageclassifier = StageClassifier()
    
    tn_results = pd.DataFrame(columns=['LLM_T_CLASSIFICATION', 'LLM_N_CLASSIFICATION'])

    for i in range(len(tn_llm_df)):
        llm_tn_data = tn_llm_df.iloc[i].to_dict()
    
        llm_stageclassifier.getTstage(llm_tn_data)
        llm_t_stage = llm_stageclassifier.t_stage.lower()
        
        llm_stageclassifier.getNStage(llm_tn_data)
        llm_n_stage = llm_stageclassifier.n_stage.lower()
        
        tn_results.loc[i] = [llm_t_stage, llm_n_stage]
    
    
    return tn_results


def main(args):
    TARGET_COLUMNS = ['MORPHOLOGY_DIAGNOSIS', 'SUBTYPE_DOMINANT','MAX_SIZE_OF_TUMOR(invasive component only)', 'MAX_SIZE_OF_TUMOR(including CIS=AIS)', \
                 'INVASION_TO_VISCERAL_PLEURAL', 'MAIN_BRONCHUS', 'INVASION_TO_CHEST_WALL', 'INVASION_TO_PARIETAL_PLEURA', 'INVASION_TO_PERICARDIUM', \
                 'INVASION_TO_PHRENIC_NERVE', 'TUMOR_SIZE_CNT', 'LUNG_TO_LUNG_METASTASIS', 'INTRAPULMONARY_METASTASIS', 'SATELLITE_TUMOR_LOCATION', \
                  'SEPARATE_TUMOR_LOCATION', 'INVASION_TO_MEDIASTINUM', 'INVASION_TO_DIAPHRAGM', 'INVASION_TO_HEART', 'INVASION_TO_RECURRENT_LARYNGEAL_NERVE', \
                  'INVASION_TO_TRACHEA', 'INVASION_TO_ESOPHAGUS', 'INVASION_TO_SPINE', 'METASTATIC_RIGHT_UPPER_LOBE', 'METASTATIC_RIGHT_MIDDLE_LOBE', \
                 'METASTATIC_RIGHT_LOWER_LOBE', 'METASTATIC_LEFT_UPPER_LOBE', 'METASTATIC_LEFT_LOWER_LOBE', 'INVASION_TO_AORTA', 'INVASION_TO_SVC', \
                  'INVASION_TO_IVC', 'INVASION_TO_PULMONARY_ARTERY', 'INVASION_TO_PULMONARY_VEIN', 'INVASION_TO_CARINA', \
                 'PRIMARY_CANCER_LOCATION_RIGHT_UPPER_LOBE', 'PRIMARY_CANCER_LOCATION_RIGHT_MIDDLE_LOBE', 'PRIMARY_CANCER_LOCATION_RIGHT_LOWER_LOBE', \
                 'PRIMARY_CANCER_LOCATION_LEFT_UPPER_LOBE', 'PRIMARY_CANCER_LOCATION_LEFT_LOWER_LOBE','RELATED_TO_ATELECTASIS_OR_OBSTRUCTIVE_PNEUMONITIS', \
                 'PRIMARY_SITE_LATERALITY', 'LYMPH_METASTASIS_SITES', 'NUMER_OF_LYMPH_NODE_META_CASES']

    LYMPH_VALUE_LIST =  ['1', '2', '2L', '2R', '3', '3P', '4', '4L', '4R', '5', '6', '7', '8', '9', '9L', '9R', '10', '10L', '10R', \
                 '11', '11L', '11R', '12', '12L', '12R', '13', '13L', '13R', '14', '14L', '14R', 'PRETRACHEAL', 'PARATRACHEAL', \
                 'INTRAPULMONARY', 'LATERALCERVICAL', 'MEDIALCERVICAL', 'CAROTID', 'CARDIOPHRENIC', 'IMA', 'NECK LEVEL I', 'NECK LEVEL II', \
                 'NECK LEVEL III', 'NECK LEVEL IV', 'STRUCTURE OF PREVERTEBRAL LYMPH NODE', 'STRUCTURE OF DIAPHRAGMATIC LYMPH NODE', 'SUPERIOR VENA CAVA STRUCTURE', \
                 'PARIETAL PLEURA STRUCTURE', 'STRUCTURE OF RECURRENT LARYNGEAL NERVE']
    
    TARGET_COLUMNS.extend(['SITE_OF_LYMPH_NODE_'+lymph_value for lymph_value in LYMPH_VALUE_LIST])

    
    REGEX_LIST = [r"MORPHOLOGY_DIAGNOSIS", r"SUBTYPE_DOMINANT", r"invasive\s*component\s*only", r"including\s*CIS",\
                r"INVASION_TO_VISCERAL_PLEURAL", r"MAIN_BRONCHUS", r"INVASION_TO_CHEST_WALL", r"INVASION_TO_PARIETAL_PLEURA", r"INVASION_TO_PERICARDIUM",\
                r"INVASION_TO_PHRENIC_NERVE", r"TUMOR_SIZE_CNT", r"LUNG_TO_LUNG_METASTASIS", r"INTRAPULMONARY_METASTASIS", r"SATELLITE_TUMOR_LOCATION",\
                r"SEPARATE_TUMOR_LOCATION", r"INVASION_TO_MEDIASTINUM", r"INVASION_TO_DIAPHRAGM", r"INVASION_TO_HEART", r"INVASION_TO_RECURRENT_LARYNGEAL_NERVE",\
                r"INVASION_TO_TRACHEA", r"INVASION_TO_ESOPHAGUS", r"INVASION_TO_SPINE", r"METASTATIC_RIGHT_UPPER_LOBE", r"METASTATIC_RIGHT_MIDDLE_LOBE", \
                r"METASTATIC_RIGHT_LOWER_LOBE", r"METASTATIC_LEFT_UPPER_LOBE", r"METASTATIC_LEFT_LOWER_LOBE", r"INVASION_TO_AORTA", r"INVASION_TO_SVC",\
                r"INVASION_TO_IVC", r"INVASION_TO_PULMONARY_ARTERY", r"INVASION_TO_PULMONARY_VEIN", r"INVASION_TO_CARINA", r"PRIMARY_CANCER_LOCATION_RIGHT_UPPER_LOBE",\
                r"PRIMARY_CANCER_LOCATION_RIGHT_MIDDLE_LOBE", r"PRIMARY_CANCER_LOCATION_RIGHT_LOWER_LOBE", r"PRIMARY_CANCER_LOCATION_LEFT_UPPER_LOBE",\
                r"PRIMARY_CANCER_LOCATION_LEFT_LOWER_LOBE", r"PRIMARY_SITE_LATERALITY", r"LYMPH_METASTASIS_SITES", r"NUMER_OF_LYMPH_NODE_META_CASES",
    ]

    RENAME_DICT = {'MAX_SIZE_OF_TUMOR(invasive component only)':'SIZE_OF_TUMOR',\
                   'MAX_SIZE_OF_TUMOR(including CIS=AIS)':'SIZE_OF_TUMOR_AIS',\
                   'SATELLITE_TUMOR_LOCATION':'SATELLITE',\
                   'SEPARATE_TUMOR_LOCATION':'SEPARATE_TUMOR',\
                   'PRIMARY_SITE_LATERALITY':'LATERALITY',\
                  'NUMER_OF_LYMPH_NODE_META_CASES':'LYMPH_NODE_META_CASES'}

    
    print('TN staging start...')
    preds = load_data(args.result_path)

    print('Converting results to DataFrame...')
    llm_df = ie_result_to_df(preds, TARGET_COLUMNS, REGEX_LIST)
    llm_df = llm_df.rename(columns=RENAME_DICT)

    print('Starting TN Classification')
    tn_results = tn_classification(llm_df)
    print(tn_results)
    
    output_path = os.path.join(args.output_dir, "tn_results.xlsx")
    tn_results.to_excel(output_path ,index=False)
    print('\nClassification results saved in:', output_path)
   


if __name__=='__main__':
    parser = argparse.ArgumentParser(description="Arguments")
    parser.add_argument('--result_path', '-mpath', type=str, help='Generated results file path')
    parser.add_argument('--output_dir', '-output', type=str, help='Save directory path')
    
    args = parser.parse_args()
    
    os.makedirs(args.output_dir, exist_ok=True)

    main(args)