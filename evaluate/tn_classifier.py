import re

class StageClassifier:
    def __init__(self):
        # T4 stage condition
        self.MUCINOUS_REGEX = r'(?<!non-)\bmucinous\b'  # lookbehind
        self.INSITU_REGEX = r'(in situ)'
        self.SEPARATE_NODULE_REGEX = r'()'
        self.ADENOCARCINOMA_REGEX = r'(adenocarcinoma)'

        self.t_stage = ''
        self.n_stage = ''
        self.tumor_size = ''

        self.T4_OVER_SIZE = 7
        self.t4_trigger = False

        self.T1C_BELOW_SIZE = 3
        self.T1C_OVER_SIZE = 2
        self.T1B_BELOW_SIZE = 2
        self.T1B_OVER_SIZE = 1
        self.T1A_BELOW_SIZE = 1

        self.T2B_BELOW_SIZE = 5
        self.T2B_OVER_SIZE = 4
        self.T2A_BELOW_SIZE = 4
        self.T2A_OVER_SIZE = 3
        self.T2_OVER_SIZE = 3
        self.T2_BELOW_SIZE = 5
        self.ls_visceral = False
        self.ls_main_bronchus = False

        self.T3_BELOW_SIZE = 7
        self.T3_OVER_SIZE = 5

        self.T_decisivePart = ''
        self.N_decisivePart = ''

        self.T_decisivePartList = []
        self.N_decisivePartList = []

    def ls_T4stage(self, row: dict) -> bool:
        # T4 Stage 조건식
        iv_mediastinum = row['INVASION_TO_MEDIASTINUM'] == 'present'
        iv_diaphragm = row['INVASION_TO_DIAPHRAGM'] == 'present'
        iv_heart = row['INVASION_TO_HEART'] == 'present'
        # iv_great_vessels = row['INVASION_TO_GREAT_VESSELS'] == 'present'
        iv_rln = row['INVASION_TO_RECURRENT_LARYNGEAL_NERVE'] == 'present'
        iv_trachea = row['INVASION_TO_TRACHEA'] == 'present'
        iv_esophagus = row['INVASION_TO_ESOPHAGUS'] == 'present'
        iv_spine = row['INVASION_TO_SPINE'] == 'present'
        ls_m_rul = row['METASTATIC_RIGHT_UPPER_LOBE'] == 'true'
        ls_m_rml = row['METASTATIC_RIGHT_MIDDLE_LOBE'] == 'true'
        ls_m_rll = row['METASTATIC_RIGHT_LOWER_LOBE'] == 'true'
        ls_m_lul = row['METASTATIC_LEFT_UPPER_LOBE'] == 'true'
        ls_m_lll = row['METASTATIC_LEFT_LOWER_LOBE'] == 'true'
        iv_aoa = row['INVASION_TO_AORTA'] == 'present'
        iv_svc = row['INVASION_TO_SVC'] == 'present'
        iv_ivc = row['INVASION_TO_IVC'] == 'present'
        iv_pa = row['INVASION_TO_PULMONARY_ARTERY'] == 'present'
        iv_pv = row['INVASION_TO_PULMONARY_VEIN'] == 'present'
        iv_car = row['INVASION_TO_CARINA'] == 'present'
        ls_ltl_meta = row['LUNG_TO_LUNG_METASTASIS'] == 'true'

        # Logic
        # Retrieve locations where primary cancer is True; there may be multiple.
        primary_lobe = []  # Store the location of the primary cancer that is True in the primary_cancer_list.
        if row['PRIMARY_CANCER_LOCATION_RIGHT_UPPER_LOBE'] == 'true': primary_lobe.append('RUL')
        if row['PRIMARY_CANCER_LOCATION_RIGHT_MIDDLE_LOBE'] == 'true': primary_lobe.append('RML')
        if row['PRIMARY_CANCER_LOCATION_RIGHT_LOWER_LOBE'] == 'true': primary_lobe.append('RLL')
        if row['PRIMARY_CANCER_LOCATION_LEFT_UPPER_LOBE'] == 'true': primary_lobe.append('LUL')
        if row['PRIMARY_CANCER_LOCATION_LEFT_LOWER_LOBE'] == 'true': primary_lobe.append('LLL')

        satellite_lobe = []
        if row['SATELLITE'] == 'in the same lobe': satellite_lobe.append('ISL')
        if row['SATELLITE'] == 'right upper lobe': satellite_lobe.append('RUL')
        if row['SATELLITE'] == 'right middle lobe': satellite_lobe.append('RML')
        if row['SATELLITE'] == 'right lower lobe': satellite_lobe.append('RLL')
        if row['SATELLITE'] == 'left upper lobe': satellite_lobe.append('LUL')
        if row['SATELLITE'] == 'left lower lobe': satellite_lobe.append('LLL')

        separate_lobe = []
        if row['SEPARATE_TUMOR'] == 'in the same lobe': separate_lobe.append('ISL')
        if row['SEPARATE_TUMOR'] == 'right upper lobe': separate_lobe.append('RUL')
        if row['SEPARATE_TUMOR'] == 'right middle lobe': separate_lobe.append('RML')
        if row['SEPARATE_TUMOR'] == 'right lower lobe': separate_lobe.append('RLL')
        if row['SEPARATE_TUMOR'] == 'left upper lobe': separate_lobe.append('LUL')
        if row['SEPARATE_TUMOR'] == 'left lower lobe': separate_lobe.append('LLL')

        ipsilateral_lobe_satellite = set()
        ipsilateral_lobe_separate = set()

        # Check if it's the same side lobe -> ipsilateral
        # Check Satellite tumor
        for lobe in primary_lobe:
            if 'R' in lobe:  # In case of the right lung lobe
                for satellite in satellite_lobe:
                    if satellite in ['RUL', 'RML', 'RLL']:
                        ipsilateral_lobe_satellite.add(satellite)
            elif 'L' in lobe:  # In case of the left lung lobe
                for satellite in satellite_lobe:
                    if satellite in ['LUL', 'LLL']:
                        ipsilateral_lobe_satellite.add(satellite)

        # Check Separate tumor
        for lobe in primary_lobe:
            if 'R' in lobe:  # In case of the right lung lobe
                for separate in separate_lobe:
                    if separate in ['RUL', 'RML', 'RLL']:
                        ipsilateral_lobe_separate.add(separate)
            elif 'L' in lobe:  # In case of the left lung lobe
                for separate in separate_lobe:
                    if separate in ['LUL', 'LLL']:
                        ipsilateral_lobe_separate.add(separate)

        if ipsilateral_lobe_satellite:
            self.t4_trigger = True
            self.T_decisivePartList.append('Ipsilateral lobe satellite')
        if ipsilateral_lobe_separate:
            self.t4_trigger = True
            self.T_decisivePartList.append('Ipsilateral lobe separate')
        if ls_ltl_meta and (ipsilateral_lobe_satellite or ipsilateral_lobe_separate):
            self.t4_trigger = True
            self.T_decisivePartList.append('Lung to lung metastasis and ipsilateral lobe')


        # Consider as T4 if any condition is true.
        if iv_mediastinum or iv_diaphragm or iv_heart or iv_rln or iv_trachea or iv_esophagus or iv_spine or ls_m_rul or ls_m_rml or ls_m_rll or ls_m_lul or ls_m_lll or iv_aoa or iv_svc or iv_ivc or iv_pa or iv_pv or iv_car or (self.tumor_size > self.T4_OVER_SIZE) or self.t4_trigger:
            if iv_mediastinum:
                self.T_decisivePart = 'pt4 : INVASION_TO_MEDIASTINUM'
                self.T_decisivePartList.append('Invasion to mediastinum')
            if iv_diaphragm:
                self.T_decisivePart = 'pt4 : INVASION_TO_DIAPHRAGM'
                self.T_decisivePartList.append('Invasion to diaphragm')
            if iv_heart:
                self.T_decisivePart = 'pt4 : INVASION_TO_HEART'
                self.T_decisivePartList.append('Invasion to heart')
            if iv_rln:
                self.T_decisivePart = 'pt4 : INVASION_TO_RECURRENT_LARYNGEAL_NERVE'
                self.T_decisivePartList.append('Invasion to recurrent laryngeal nerve')
            if iv_trachea:
                self.T_decisivePart = 'pt4 : INVASION_TO_TRACHEA'
                self.T_decisivePartList.append('Invasion to trachea')
            if iv_esophagus:
                self.T_decisivePart = 'pt4 : INVASION_TO_ESOPHAGUS'
                self.T_decisivePartList.append('Invasion to esophagus')
            if iv_spine:
                self.T_decisivePart = 'pt4 : INVASION_TO_SPINE'
                self.T_decisivePartList.append('Invasion to vertebral body(spines)')
            if ls_m_rul:
                self.T_decisivePart = 'pt4 : METASTATIC_RIGHT_UPPER_LOBE'
                self.T_decisivePartList.append('Metastatic right upper lobe')
            if ls_m_rml:
                self.T_decisivePart = 'pt4 : METASTATIC_RIGHT_MIDDLE_LOBE'
                self.T_decisivePartList.append('Metastatic right middle lobe')
            if ls_m_rll:
                self.T_decisivePart = 'pt4 : METASTATIC_RIGHT_LOWER_LOBE'
                self.T_decisivePartList.append('Metastatic right lower lobe')
            if ls_m_lul:
                self.T_decisivePart = 'pt4 : METASTATIC_LEFT_UPPER_LOBE'
                self.T_decisivePartList.append('Metastatic left upper lobe')
            if ls_m_lll:
                self.T_decisivePart = 'pt4 : METASTATIC_LEFT_LOWER_LOBE'
                self.T_decisivePartList.append('Metastatic left lower lobe')
            if iv_aoa:
                self.T_decisivePart = 'pt4 : INVASION_TO_AORTA'
                self.T_decisivePartList.append('Invasion to aorta')
            if iv_svc:
                self.T_decisivePart = 'pt4 : INVASION_TO_SVC'
                self.T_decisivePartList.append('Invasion to SVC(Superior vena cava)')
            if iv_ivc:
                self.T_decisivePart = 'pt4 : INVASION_TO_IVC'
                self.T_decisivePartList.append('Invasion to IVC(Inferior vena cava)')
            if iv_pa:
                self.T_decisivePart = 'pt4 : INVASION_TO_PULMONARY_ARTERY'
                self.T_decisivePartList.append('Invasion to pulmonary artery')
            if iv_pv:
                self.T_decisivePart = 'pt4 : INVASION_TO_PULMONARY_VEIN'
                self.T_decisivePartList.append('Invasion to pulmonary vein')
            if iv_car:
                self.T_decisivePart = 'pt4 : INVASION_TO_CARINA'
                self.T_decisivePartList.append('Invasion to carina')
            if (self.tumor_size > self.T4_OVER_SIZE):
                self.T_decisivePart = 'pt4 : pt4 size'
                self.T_decisivePartList.append('Max tumor size is greater than 7cm')
            return True

        return False

    def ls_T3stage(self, row: dict) -> bool:
        # T3 stage condition
        iv_chest_wall = row['INVASION_TO_CHEST_WALL'] == 'present'
        iv_parietal_pleura = row['INVASION_TO_PARIETAL_PLEURA'] in ['present(p3)', 'present']
        iv_pericardium = row['INVASION_TO_PERICARDIUM'] == 'present'
        iv_phrenic_nerve = row['INVASION_TO_PHRENIC_NERVE'] == 'present'
        tumor_size_cnt_over = False
        ls_ltl_meta = row['LUNG_TO_LUNG_METASTASIS'] == 'true'
        ls_intra_meta = row['INTRAPULMONARY_METASTASIS'] == 'true'
        ls_satellite = False
        ls_separate_tumor = False

        if row['TUMOR_SIZE_CNT']:
            try:
                tumor_size_cnt = int(row['TUMOR_SIZE_CNT'])
                if tumor_size_cnt >= 2:
                    tumor_size_cnt_over = True
            except:
                pass

        # Logic
        # Retrieve locations where primary cancer is True; multiple locations possible.
        primary_lobe = [] # Store True primary cancer locations in primary_cancer_list.
        if row['PRIMARY_CANCER_LOCATION_RIGHT_UPPER_LOBE'] == 'true' : primary_lobe.append('RUL')
        if row['PRIMARY_CANCER_LOCATION_RIGHT_MIDDLE_LOBE'] == 'true': primary_lobe.append('RML')
        if row['PRIMARY_CANCER_LOCATION_RIGHT_LOWER_LOBE'] == 'true': primary_lobe.append('RLL')
        if row['PRIMARY_CANCER_LOCATION_LEFT_UPPER_LOBE'] == 'true': primary_lobe.append('LUL')
        if row['PRIMARY_CANCER_LOCATION_LEFT_LOWER_LOBE'] == 'true': primary_lobe.append('LLL')

        satellite_lobe = []
        if row['SATELLITE'] == 'in the same lobe': satellite_lobe.append('ISL')
        if row['SATELLITE'] == 'right upper lobe': satellite_lobe.append('RUL')
        if row['SATELLITE'] == 'right middle lobe': satellite_lobe.append('RML')
        if row['SATELLITE'] == 'right lower lobe': satellite_lobe.append('RLL')
        if row['SATELLITE'] == 'left upper lobe': satellite_lobe.append('LUL')
        if row['SATELLITE'] == 'left lower lobe': satellite_lobe.append('LLL')

        separate_lobe = []
        if row['SEPARATE_TUMOR'] == 'in the same lobe': separate_lobe.append('ISL')
        if row['SEPARATE_TUMOR'] == 'right upper lobe': separate_lobe.append('RUL')
        if row['SEPARATE_TUMOR'] == 'right middle lobe': separate_lobe.append('RML')
        if row['SEPARATE_TUMOR'] == 'right lower lobe': separate_lobe.append('RLL')
        if row['SEPARATE_TUMOR'] == 'left upper lobe': separate_lobe.append('LUL')
        if row['SEPARATE_TUMOR'] == 'left lower lobe': separate_lobe.append('LLL')

        if 'ISL' in satellite_lobe: ls_satellite = True
        if 'ISL' in separate_lobe: ls_separate_tumor = True

        # Check if in the same lung lobe.
        same_lobe_as_primary_satellite = set(primary_lobe).intersection(set(satellite_lobe))
        same_lobe_as_primary_separate = set(primary_lobe).intersection(set(separate_lobe))

        if same_lobe_as_primary_satellite:
            ls_satellite = True
        if same_lobe_as_primary_separate:
            ls_separate_tumor = True

        # Consider as T3 if any condition is true.
        if iv_chest_wall or iv_parietal_pleura or iv_pericardium or iv_phrenic_nerve or tumor_size_cnt_over or ls_ltl_meta or ls_intra_meta or ls_satellite or ls_separate_tumor or ((self.tumor_size > self.T3_OVER_SIZE) and (self.tumor_size <= self.T3_BELOW_SIZE)):
            if iv_chest_wall:
                self.T_decisivePart = 'pt3 : INVASION_TO_CHEST_WALL'
                self.T_decisivePartList.append('Invasion to chest wall')
            if iv_parietal_pleura:
                self.T_decisivePart = 'pt3 : INVASION_TO_PARIETAL_PLEURA'
                self.T_decisivePartList.append('Invasion to parietal pleura')
            if iv_pericardium:
                self.T_decisivePart = 'pt3 : INVASION_TO_PERICARDIUM'
                self.T_decisivePartList.append('Invasion to pericardium')
            if iv_phrenic_nerve:
                self.T_decisivePart = 'pt3 : INVASION_TO_PHRENIC_NERVE'
                self.T_decisivePartList.append('Invasion to phrenic nerve')
            if tumor_size_cnt_over:
                self.T_decisivePart = 'pt3 : TUMOR_SIZE_CNT_OVER'
                self.T_decisivePartList.append('Two or more separate tumor nodules in the same lobe as the primary tumor.')
            if ls_ltl_meta:
                self.T_decisivePart = 'pt3 : LUNG_TO_LUNG_METASTASIS'
                self.T_decisivePartList.append('Lung to lung metastasis')
            if ls_intra_meta:
                self.T_decisivePart = 'pt3 : INTRAPULMONARY_METASTASIS'
                self.T_decisivePartList.append('Intrapulmonary metastasis')
            if ls_satellite:
                self.T_decisivePart = 'pt3 : SAME_LOBE_AS_PRIMARY_SATELLITE'
                self.T_decisivePartList.append('Same lobe as primary satellite')
            if ls_separate_tumor:
                self.T_decisivePart = 'pt3 : SAME_LOBE_AS_PRIMARY_SEPARATE'
                self.T_decisivePartList.append('Same lobe as primary separate')
            if ((self.tumor_size > self.T3_OVER_SIZE) and (self.tumor_size <= self.T3_BELOW_SIZE)):
                self.T_decisivePart = 'pt3 : pt3 size'
                self.T_decisivePartList.append('Max tumor size is greater than 5cm and less than or equal to 7cm')
            return True

        return False

    def ls_T2stage(self, row: dict) -> bool:
        ls_visceral = row['INVASION_TO_VISCERAL_PLEURAL'] in ['p1', 'p2', 'present']
        ls_main_bronchus = 'involved by' in row['MAIN_BRONCHUS']
        ls_associated_findings = True if row['RELATED_TO_ATELECTASIS_OR_OBSTRUCTIVE_PNEUMONITIS'] == 'true' else False

        if ls_visceral or ls_main_bronchus or ls_associated_findings:
            if ls_visceral:
                self.T_decisivePart = 'pt2 : INVASION_TO_VISCERAL_PLEURAL'
                self.T_decisivePartList.append('Invasion to visceral pleural')
            if ls_main_bronchus:
                self.T_decisivePart = 'pt2 : INVOLVED_BY_MAIN_BRONCHUS'
                self.T_decisivePartList.append('Involves the main bronchus regardless of distance to the carina, but with out involvement of the carina.')
            if ls_associated_findings:
                self.T_decisivePartList.append('Associated with atelectasis or obstructive pneumonitis that extends to the hilar region, involving part or all of the lung.')
            return True

        return False

    def ls_T1mistage(self, row: dict,  diagnosis: str) -> bool:
        adenocarcinoma_match = re.findall(self.ADENOCARCINOMA_REGEX, diagnosis, flags=re.I)
        mucinous_match2 = re.findall(self.MUCINOUS_REGEX, diagnosis, flags=re.I)
        if not mucinous_match2: # non-mucinos type
            invasive_component_only_tumor_size = float(row['SIZE_OF_TUMOR'].replace(' cm', '')) if row['SIZE_OF_TUMOR'] != '' else None
            if invasive_component_only_tumor_size == None : return False
            if (invasive_component_only_tumor_size <= 0.5) and (self.tumor_size <= 3) and adenocarcinoma_match and (row['SUBTYPE_DOMINANT'] == 'lepidic'):
                self.T_decisivePartList.append('The diagnosis is adenocarcinoma, the invasive component only, the max tumor size is less than 0.5 mm, the tumor size (including CIS or AIS) is less than 3 cm, and the dominant condition is lepidic.')
                return True

        return False

    def getTstage(self, row: dict):
        """
        T staging logic
        :param row: Row loaded from IE results (in dict form)
        :return: T stage value (str)
        """
        # Initialize
        self.t4_trigger = False
        self.t_stage = ''
        self.tumor_size = ''
        self.T_decisivePart = ''
        self.T_decisivePartList = []

        diagnosis = row['MORPHOLOGY_DIAGNOSIS']
        # [T stage conditions]
        mucinous_match = re.findall(self.MUCINOUS_REGEX, diagnosis, flags=re.I)
        insitu_match = re.findall(self.INSITU_REGEX, diagnosis, flags=re.I)

        try:
            if mucinous_match: # In case of mucinous type
                self.tumor_size = float(row['SIZE_OF_TUMOR_AIS'].replace(' cm', '')) if row['SIZE_OF_TUMOR_AIS'] != '' else None
                if self.tumor_size == None and row['SIZE_OF_TUMOR'] != '':
                    self.tumor_size = float(row['SIZE_OF_TUMOR'].replace(' cm', ''))
            else: # In case of non-mucinous type
                self.tumor_size = float(row['SIZE_OF_TUMOR'].replace(' cm', '')) if row['SIZE_OF_TUMOR'] != '' else None
                if self.tumor_size == None and row['SIZE_OF_TUMOR_AIS'] != '':
                    self.tumor_size = float(row['SIZE_OF_TUMOR_AIS'].replace(' cm', ''))
        except:
            self.tumor_size = None


        # T staging
        if self.tumor_size != None:
            # T4
            if self.ls_T4stage(row):
                self.t_stage = 'pT4'
                return
            # T3
            elif self.ls_T3stage(row):
                self.t_stage = 'pT3'
                return
            # T2
            if self.ls_T2stage(row) or (self.tumor_size <= self.T2B_BELOW_SIZE and self.tumor_size > self.T2A_OVER_SIZE):
                if (self.tumor_size > self.T2B_OVER_SIZE and self.tumor_size <= self.T2B_BELOW_SIZE):
                    self.t_stage = 'pT2b'
                    self.T_decisivePart = 'pt2b : pt2b size'
                    self.T_decisivePartList.append('Max tumor size is greater than 4cm and less than or equal to 5cm')
                    return
                else:
                    self.t_stage = 'pT2a'
                    self.T_decisivePart = 'pt2a : pt2a size'
                    if (self.tumor_size > self.T2A_OVER_SIZE and self.tumor_size <= self.T2A_BELOW_SIZE): self.T_decisivePartList.append('Max tumor size is greater than 3cm and less than or equal to 4cm')
                    return

            # Tis
            elif insitu_match:
                self.t_stage = 'pTis'
                self.T_decisivePart = 'ptis : INSITU_MATCH'
                self.T_decisivePartList.append('It is one of three types: carcinoma in situ, squamous cell carcinoma in situ (SCIS), or adenocarcinoma in situ (AIS).')
                return
            # T1
            else:
                if 'minimally invasive adenocarcinoma' in diagnosis:
                    self.t_stage = 'pT1mi'
                    self.T_decisivePart = 'pt1mi : MINIMALLY_INVASIVE_ADENOCARCINOMA'
                    self.T_decisivePartList.append('minimally invasive adenocarcinoma')
                elif self.ls_T1mistage(row, diagnosis):
                    self.t_stage = 'pT1mi'
                    self.T_decisivePart = 'pt1mi : MINIMALLY_INVASIVE_ADENOCARCINOMA'
                elif self.tumor_size <= self.T1C_BELOW_SIZE and self.tumor_size > self.T1C_OVER_SIZE:
                    self.t_stage = 'pT1c'
                    self.T_decisivePart = 'pt1c : pt1c size'
                    self.T_decisivePartList.append('Max tumor size is less than or equal to 3 cm and larger than 2 cm.')
                    return
                elif self.tumor_size <= self.T1B_BELOW_SIZE and self.tumor_size > self.T1B_OVER_SIZE:
                    self.t_stage = 'pT1b'
                    self.T_decisivePart = 'pt1b : pt1b size'
                    self.T_decisivePartList.append('Max tumor size is less than or equal to 2 cm and larger than 1 cm.')
                    return
                elif self.tumor_size <= self.T1A_BELOW_SIZE:
                    self.t_stage = 'pT1a'
                    self.T_decisivePart = 'pt1a : pt1a size'
                    self.T_decisivePartList.append('Max tumor size is less than or equal to 1cm.')
                    return
        # Tis, T0, Tx
        else:
            self.t_stage = 'pTx'
            self.T_decisivePart = 'ptx : ptx'
            self.T_decisivePartList.append('primary tumor canot be assessed')
            return

    def has_intersection(self, set1: set, set2: set) -> bool:
        """
        Checks if there is an intersection. Returns True if present, otherwise False.
        :param set1: Set
        :param set2: Set
        :return: True or False
        """
        return True if len(set1.intersection(set2)) else False

    def getNStage(self, row: dict):
        """
        N staging logic
        :param row: Row loaded from IE results (in dict form)
        :return: N stage value (str)
        """
        # Initialize
        self.n_stage = ''
        self.N_decisivePart = ''

        no_metastasis = True if row['LYMPH_NODE_META_CASES'] == '0' else False
        site_laterality = row['LATERALITY']

        LYMPH_VALUE_SET = set(
            ['1', '2', '2L', '2R', '3', '3P', '4', '4L', '4R', '5', '6', '7', '8', '9', '9L', '9R', '10', '10L', '10R', \
             '11', '11L', '11R', '12', '12L', '12R', '13', '13L', '13R', '14', '14L', '14R', 'PRETRACHEAL', 'PARATRACHEAL',
             'INTRAPULMONARY'])

        # Variables like LEFT_LEFT indicating the same side: For ipsilateral check.
        # Variables like LEFT_RIGHT indicating opposite sides: For contralateral check.
        HILAR_VALUE_SET = set(['10', '10L', '10R', '11', '11L', '11R', '12', '12L', '12R', '13', '13L', '13R', '14', '14L', '14R'])
        LEFT_RIGHT_HILAR_VALUE_SET = set(['10R', '11R', '12R', '13R', '14R'])
        RIGHT_RIGHT_HILAR_VALUE_SET = set(['10', '10R', '11', '11R', '12', '12R', '13', '13R', '14', '14R'])
        RIGHT_LEFT_HILAR_VALUE_SET = set(['10L', '11L', '12L', '13L', '14L'])
        LEFT_LEFT_HILAR_VALUE_SET = set(['10', '10L', '11', '11L', '12', '12L', '13', '13L', '14', '14L'])

        MEDIASTINAL_VALUE_SET = set(['2', '2L', '2R', '3', '3P', '4', '4L', '4R', '5', '6', '8', '9', '9L', '9R'])
        LEFT_RIGHT_MEDIASTINAL_VALUE_SET = set(['2R', '4R', '9R'])
        RIGHT_RIGHT_MEDIASTINAL_VALUE_SET = set(['2', '2R', '3', '3P', '4', '4R', '5', '6', '8', '9', '9R'])
        RIGHT_LEFT_MEDIASTINAL_VALUE_SET = set(['2L', '4L', '9L'])
        LEFT_LEFT_MEDIASTINAL_VALUE_SET = set(['2', '2L', '3', '3P', '4', '4L', '5', '6', '8', '9', '9L'])

        SUPRACLAVICULAR_VALUE_SET = set(['1'])
        INTRAPULMONARY_VALUE_SET = set(['INTRAPULMONARY'])
        SUBCARINAL_VALUE_SET = set(['7'])

        meta_lymph_set = set()
        for val in LYMPH_VALUE_SET:
            col_name = 'SITE_OF_LYMPH_NODE_' + val
            if row[col_name] == 'true':
                meta_lymph_set.add(val)

        # Determine N-Stage based on priority: N3, N2, N1.
        if no_metastasis:
            self.n_stage = 'pN0'
            self.N_decisivePart = 'pN0 : NO_METASTASIS'
            return
        elif row['LYMPH_NODE_META_CASES'] == '':
            self.n_stage = 'pNx'
            self.N_decisivePart = 'pNx : pNx'
            return
        elif site_laterality == 'right and left':
            if self.has_intersection(meta_lymph_set, SUPRACLAVICULAR_VALUE_SET):
                self.n_stage = 'pN3'
                self.N_decisivePart = 'pn3 : RIGHT_AND_LEFT SUPRACLAVICULAR'
                return
            elif self.has_intersection(meta_lymph_set, MEDIASTINAL_VALUE_SET):
                self.n_stage = 'pN3'
                self.N_decisivePart = 'pn3 : RIGHT_AND_LEFT MEDIASTINAL'
                return
            elif self.has_intersection(meta_lymph_set, HILAR_VALUE_SET):
                self.n_stage = 'pN3'
                self.N_decisivePart = 'pn3 : RIGHT_AND_LEFT HILAR'
                return
            elif self.has_intersection(meta_lymph_set, INTRAPULMONARY_VALUE_SET):
                self.n_stage = 'pN3'
                self.N_decisivePart = 'pn3 : RIGHT_AND_LEFT INTRAPULMONARY'
                return
            elif self.has_intersection(meta_lymph_set, SUBCARINAL_VALUE_SET):
                self.n_stage = 'pN3'
                self.N_decisivePart = 'pn3 : RIGHT_AND_LEFT SUBCARINAL'
                return
            else:
                self.n_stage = 'pN0'
                self.N_decisivePart = 'pN0'
                return
        elif site_laterality == 'right':
            if self.has_intersection(meta_lymph_set, SUPRACLAVICULAR_VALUE_SET):
                self.n_stage = 'pN3'
                self.N_decisivePart = 'pn3 : RIGHT_SUPRACLAVICULAR'
                return
            elif self.has_intersection(meta_lymph_set, RIGHT_LEFT_MEDIASTINAL_VALUE_SET):
                self.n_stage = 'pN3'
                self.N_decisivePart = 'pn3 : RIGHT_LEFT_MEDIASTINAL '
                return
            elif self.has_intersection(meta_lymph_set, RIGHT_LEFT_HILAR_VALUE_SET):
                self.n_stage = 'pN3'
                self.N_decisivePart = 'pn3 : RIGHT_LEFT_HILAR'
                return
            elif self.has_intersection(meta_lymph_set, SUBCARINAL_VALUE_SET):
                self.n_stage = 'pN2'
                self.N_decisivePart = 'pn2 : RIGHT_SUBCARINAL'
                return
            elif self.has_intersection(meta_lymph_set, RIGHT_RIGHT_MEDIASTINAL_VALUE_SET):
                self.n_stage = 'pN2'
                self.N_decisivePart = 'pn2 : RIGHT_RIGHT_MEDIASTINAL'
                return
            elif self.has_intersection(meta_lymph_set, INTRAPULMONARY_VALUE_SET):
                self.n_stage = 'pN1'
                self.N_decisivePart = 'pn1 : RIGHT_INTRAPULMONARY'
                return
            elif self.has_intersection(meta_lymph_set, RIGHT_RIGHT_HILAR_VALUE_SET):
                self.n_stage = 'pN1'
                self.N_decisivePart = 'pn1 : RIGHT_RIGHT_HILAR'
                return
            else:
                self.n_stage = 'pN0'
                self.N_decisivePart = 'pN0 : pN0'
                return
        elif site_laterality == 'left':
            if self.has_intersection(meta_lymph_set, SUPRACLAVICULAR_VALUE_SET):
                self.n_stage = 'pN3'
                self.N_decisivePart = 'pn3 : LEFT_SUPRACLAVICULAR'
                return
            elif self.has_intersection(meta_lymph_set, LEFT_RIGHT_MEDIASTINAL_VALUE_SET):
                self.n_stage = 'pN3'
                self.N_decisivePart = 'pn3 : LEFT_RIGHT_MEDIASTINAL'
                return
            elif self.has_intersection(meta_lymph_set, LEFT_RIGHT_HILAR_VALUE_SET):
                self.n_stage = 'pN3'
                self.N_decisivePart = 'pn3 : LEFT_RIGHT_HILAR'
                return
            elif self.has_intersection(meta_lymph_set, SUBCARINAL_VALUE_SET):
                self.n_stage = 'pN2'
                self.N_decisivePart = 'pn2 : LEFT_SUBCARINAL'
                return
            elif self.has_intersection(meta_lymph_set, LEFT_LEFT_MEDIASTINAL_VALUE_SET):
                self.n_stage = 'pN2'
                self.N_decisivePart = 'pn2 : LEFT_LEFT_MEDIASTINAL'
                return
            elif self.has_intersection(meta_lymph_set, INTRAPULMONARY_VALUE_SET):
                self.n_stage = 'pN1'
                self.N_decisivePart = 'pn1 : LEFT_INTRAPULMONARY'
                return
            elif self.has_intersection(meta_lymph_set, LEFT_LEFT_HILAR_VALUE_SET):
                self.n_stage = 'pN1'
                self.N_decisivePart = 'pn1 : LEFT_LEFT_HILAR'
                return
            else:
                self.n_stage = 'pN0'
                self.N_decisivePart = 'pN0 : pN0'
                return


    def getAJCCEdition(self, note_text: str) -> int:
        """
        Checks which edition of TNM staging criteria is used.
        :param note_text: Small segmented pathology report
        :return: int or None
        """
        regexes = [r'pathologic\s*stage\s*:\s*.*(\d{1,2})\s*th\s*AJCC',
                   r'pathologic\s*stage\s*:\s*.*AJCC\s*(\d{1,2})\s*th']
        for regex in regexes:
            match = re.findall(regex, note_text, flags=re.I)
            if match:
                return int(match[0])
        return None