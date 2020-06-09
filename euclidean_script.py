import pandas as pd
import sys, getopt
import pdb
import numpy as np
from scipy.spatial import distance

MAX_LESION_SIZE = 6
MIN_AGE = 22
MAX_AGE = 46

short_arg_options = "f:"
long_arg_options = ["file"]

data_file = pd.read_excel(f'{sys.argv[-1]}')

#creates list with patients within range of min and max age, <6ml lesion size
def create_subject_list():
    subject_list = []
    for subject_num in (range(0, data_file.index[-1] + 1)):

        if not isinstance(data_file.loc[subject_num, 'Patient'].item(), int):
            continue

        age = data_file.loc[subject_num, 'AGE']
        if not age or age <=MIN_AGE or age >= MAX_AGE:
            continue

        lesion_size = data_file.loc[subject_num,'Total_LL']
        if not lesion_size < MAX_LESION_SIZE:
            continue

        num = data_file.loc[subject_num, 'Patient'] 
        sex = data_file.loc[subject_num, 'SEX']
        iq = data_file.loc[subject_num, 'IQ']
        edu_level = data_file.loc[subject_num, 'Edu_lev']

        subject_data = [num, age, sex, iq, edu_level, lesion_size]

        subject_list.append(subject_data)

    return subject_list


# divides subjects into MS patients and healthy controls
def create_patient_and_healthy_control_lists(subject_list):
    ms_patients = []
    healthy_controls = []

    # subject is an array with zeroth index being subject_num.
    for subject in subject_list:
        if subject[0] >= 1000:
            healthy_controls.append(subject)
        else:
            ms_patients.append(subject)
    
    numpy_ms_patients = np.array(ms_patients)
    numpy_healthy_controls = np.array(healthy_controls)

    return numpy_ms_patients, numpy_healthy_controls

def match_controls_with_patients(patient_list, control_list):
    print('in match_controls')
    patient_healthy_control_data = []

    for control in control_list:

        patient_closest_matches = patient_list[np.argsort(distance.cdist(np.atleast_2d(control), np.atleast_2d(patient_list), 'wminkowski', w=[0,5,1,5,1,0]))][0]

        matches = patient_closest_matches.tolist()
        for patient in matches:
            if patient in patient_healthy_control_data:
                continue
            else:
                control_array = control.tolist()
                patient_control_row = patient + control_array
                patient_healthy_control_data.append(patient_control_row)
                break


    return patient_healthy_control_data

def create_excel_file(patient_healthy_control_data):
    

    format_data = pd.DataFrame(patient_healthy_control_data,
                   columns=['PATIENT', 'AGE', 'SEX', 'IQ', 'Edu_lev', 'TOTAL LL', 
                   'HC', 'HC-AGE', 'HC-SEX', 'HC-IQ', 'HC-Edu_lev', 'HC-TOTAL LL'])

    format_data.index += 1
    format_data.to_excel("data_analysis_script_results.xlsx")  

def main():
    subject_list = create_subject_list()
    ms_patients, healthy_controls = create_patient_and_healthy_control_lists(subject_list)
    patient_controls_matching_data = match_controls_with_patients(ms_patients, healthy_controls)
    create_excel_file(patient_controls_matching_data)

if __name__ == "__main__":
    main()



