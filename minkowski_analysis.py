import pandas as pd
import sys
import getopt
import pdb
import numpy as np
import argparse
from scipy.spatial import distance

MAX_LESION_SIZE = 6

DEFAULT_WEIGHTS = [0, 0, 5, 5, 3, 3, 0]


parser = argparse.ArgumentParser(
    description='Runs Excel data and returns new Excel file with patient control matches.')

parser.add_argument('--age', '-a', type=int, default=0,
                    help='age weight')
parser.add_argument('--sex', '-s', type=int, default=0,
                    help='sex weight')
parser.add_argument('--IQ', '-IQ', type=int, default=0,
                    help='IQ weight')
parser.add_argument('--edu_level', '-el', type=int, default=0,
                    help='Education level weight')
parser.add_argument('-file', '-f', type=str, required=True,
                    help='Excel file to be analyzed')

command_line_args = vars(parser.parse_args())


# even though can pass in as '-f', argparse takes first argument name in
# add_argument as name of arg
excel_file = command_line_args['file']
data_file = pd.read_excel(excel_file)

# 1: data_set_num, 2: patient num, 3: age, 4: sex, 5: iq, 6: edu_level, 7: lesion_load
WEIGHTS = [
    0,
    0,
    command_line_args['age'],
    command_line_args['sex'],
    command_line_args['IQ'],
    command_line_args['edu_level'],
    0
]

data_file = pd.read_excel(excel_file)

def create_minkowski_weights():
    if all(value == 0 for value in WEIGHTS):
        weights = DEFAULT_WEIGHTS
    else:
        weights = WEIGHTS

    return weights

def validate_excel_column_names():
    column_names = data_file.columns
    possible_patient_column_names = ['PATIENT', 'patient', 'Patient', 'Num', 'Patient Num', 'patient num', 'Patient num']
    possible_age_column_names = ['AGE', 'age', 'Age']
    possible_sex_column_names = ['SEX', 'sex', 'Sex']
    possible_iq_column_names = ['IQ', 'iq']
    possible_edu_level_column_names = ['Edu level', 'EDU_LEVEL', 'Education Level', 'Education', 'EDUCATION', 'Edu lev', 'Edu_lev']
    possible_lesion_load_column_names = ['Total_LL', 'lesion load', 'Lesion Load', 'Total LL']
    possible_set_number_names = ['Set', 'set', 'Data set num', 'Data Set', 'Data set', 'data set', 'data set num']

    list_column_names = data_file.columns.tolist()
    if not set(possible_patient_column_names).intersection(list_column_names):
        raise Exception(f"Patient column name must be spelled {possible_patient_column_names}.")

    
    patient_col_name = set(possible_patient_column_names).intersection(list_column_names)
    global patient_glob
    for item in patient_col_name:
        patient_glob = item

    if not set(possible_age_column_names).intersection(list_column_names):
        raise Exception(f"Age column name must be spelled: {possible_age_column_names}.")
    
    age_col_name = set(possible_age_column_names).intersection(list_column_names)
    global age_glob
    for item in age_col_name:
        age_glob = item

    if not set(possible_sex_column_names).intersection(list_column_names):
        raise Exception(f"Sex column name must be spelled: {possible_sex_column_names}.")
    
    sex_col_name = set(possible_sex_column_names).intersection(list_column_names)
    global sex_glob
    for item in sex_col_name:
        sex_glob = item

    if not set(possible_iq_column_names).intersection(list_column_names):
        raise Exception(f"IQ column name must be spelled: {possible_iq_column_names}.")
    
    iq_col_name = set(possible_iq_column_names).intersection(list_column_names)
    global iq_glob
    for item in iq_col_name:
        iq_glob = item

    if not set(possible_edu_level_column_names).intersection(list_column_names):
        raise Exception(f"Edu level column name must be spelled: {possible_edu_level_column_names}.")
    
    edu_level_col_name = set(possible_edu_level_column_names).intersection(list_column_names)
    global edu_level_glob
    for item in edu_level_col_name:
        edu_level_glob = item

    if not set(possible_lesion_load_column_names).intersection(list_column_names):
        raise Exception(f"Lesion load column name must be spelled: {possible_lesion_load_column_names}.")

    lesion_load_col_name = set(possible_lesion_load_column_names).intersection(list_column_names)
    global lesion_load_glob
    for item in lesion_load_col_name:
        lesion_load_glob = item

    if not set(possible_set_number_names).intersection(list_column_names):
        raise Exception(f"Data set nunber (1 or 2) not indicated.")
    data_set_col_name = set(possible_set_number_names).intersection(list_column_names)
    global data_set_num_glob
    for item in data_set_col_name:
        data_set_num_glob = item

# creates list with patients within range of min and max age, <6ml lesion size
def create_subject_list():
    subject_list = []
    max_age = data_file[age_glob].max()
    min_age = data_file[age_glob].min()

    data_row = data_file.loc
    for subject_num in (range(0, data_file.index[-1] + 1)):
        if not isinstance(data_row[subject_num, patient_glob].item(), int):
            continue

        age = data_row[subject_num, age_glob]
        if not age or age <= min_age or age >= max_age:
            continue

        lesion_size = data_row[subject_num, lesion_load_glob]
        if not lesion_size < MAX_LESION_SIZE:
            continue

        num = data_row[subject_num, patient_glob]
        sex = data_row[subject_num, sex_glob]
        iq = data_row[subject_num, iq_glob]
        edu_level = data_row[subject_num, edu_level_glob]
        data_set_number = data_row[subject_num, data_set_num_glob]

        subject_data = [data_set_number, num, age, sex, iq, edu_level, lesion_size]

        subject_list.append(subject_data)

    return subject_list


# divides subjects into MS patients and healthy controls
def create_patient_and_healthy_control_lists(subject_list):
    ms_patients = []
    healthy_controls = []

    # subject is an array with zeroth index being data set num.
    for subject in subject_list:
        if subject[0] == 2:
            healthy_controls.append(subject)
        else:
            ms_patients.append(subject)

    numpy_ms_patients = np.array(ms_patients)
    numpy_healthy_controls = np.array(healthy_controls)

    return numpy_ms_patients, numpy_healthy_controls


def match_controls_with_patients(patient_list, control_list):
    # patient_healthy_control_data = np.empty((0,6))
    patient_healthy_control_data = []

    for patient in patient_list:
        weights = create_minkowski_weights()

        #controls and patients:
        #minkowski distance so get cross product of all of them
        #sort by total distance
        #control index, patient index, 
        #sort by distance--smallest distance between patient and control
        #for each control, compare to each of patients
        #end up with list of 2500--every single pair combo and distance
        #sort by distance--these are all pairs with smallest distance
        #for each control, find where they are in sorted list

        # one list all distances sorted
        # then find patient per control

        # break this up into variables
        control_closest_matches = control_list[np.argsort(distance.cdist(np.atleast_2d(
            control), np.atleast_2d(patient_list), 'wminkowski', w=weights))][0]

        matches = control_closest_matches.tolist()
 
        for control in matches:
            if control in patient_healthy_control_data:
                continue
            else:
                patient_array = patient.tolist()
                patient_control_row = patient_array + control
                patient_healthy_control_data.append(patient_control_row)
                break

    return patient_healthy_control_data


def create_excel_file(patient_healthy_control_data):
    format_data = pd.DataFrame(
        patient_healthy_control_data,
        columns=[
            'DATA SET NUM',
            'PATIENT',
            'AGE',
            'SEX',
            'IQ',
            'Edu_lev',
            'TOTAL LL',
            'DATA SET NUM',
            'HC',
            'HC-AGE',
            'HC-SEX',
            'HC-IQ',
            'HC-Edu_lev',
            'HC-TOTAL LL'])

    format_data.index += 1
    format_data.to_excel("minkowski_analysis_results.xlsx")


def main():
    validate_excel_column_names()
    subject_list = create_subject_list()
    ms_patients, healthy_controls = create_patient_and_healthy_control_lists(
        subject_list)
    patient_controls_matching_data = match_controls_with_patients(
        ms_patients, healthy_controls)
    create_excel_file(patient_controls_matching_data)


if __name__ == "__main__":
    main()
