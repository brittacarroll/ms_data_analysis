import pandas as pd
import sys
import getopt
import pdb
import numpy as np
import argparse
from scipy.spatial import distance

MAX_LESION_SIZE = 6

DEFAULT_WEIGHTS = [0, 5, 5, 3, 3, 0]


#TODO: 
# allow for two excel files to be accepted into script
# fix double for loop below

# --help not working-fix
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
parser.add_argument('-file', '-f', type=str,
                    help='Excel file to be analyzed')

command_line_args = vars(parser.parse_args())


# even though can pass in as '-f', argparse takes first argument name in
# add_argument as name of arg
excel_file = command_line_args['file']
data_file = pd.read_excel(excel_file)

WEIGHTS = [
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


def validate_excel_column_names(data_file):
    column_names = data_file.columns
    possible_patient_column_names = ['PATIENT', 'patient', 'Patient', 'Num', 'Patient Num', 'patient num', 'Patient num']
    possible_age_column_names = ['AGE', 'age', 'Age']
    possible_sex_column_names = ['SEX', 'sex', 'Sex']
    possible_iq_column_names = ['IQ', 'iq']
    possible_edu_level_column_names = ['Edu level', 'EDU_LEVEL', 'Education Level', 'Education', 'EDUCATION', 'Edu lev', 'Edu_lev']

    list_column_names = data_file.columns.tolist()
    if not set(possible_patient_column_names).intersection(list_column_names):
        raise Exception(f"Patient column name must be spelled {possible_patient_column_names}.")

    if not set(possible_age_column_names).intersection(list_column_names):
        raise Exception(f"Age column name must be spelled: {possible_age_column_names}.")

    if not set(possible_sex_column_names).intersection(list_column_names):
        raise Exception(f"Sex column name must be spelled: {possible_sex_column_names}.")

    if not set(possible_iq_column_names).intersection(list_column_names):
        raise Exception(f"IQ column name must be spelled: {possible_iq_column_names}.")

    if not set(possible_edu_level_column_names).intersection(list_column_names):
        raise Exception(f"Edu level column name must be spelled: {possible_edu_level_column_names}.")


# creates list with patients within range of min and max age, <6ml lesion size
def create_subject_list():
    subject_list = []
    max_age = data_file['AGE'].max()
    min_age = data_file['AGE'].min()

    data_row = data_file.loc
    validate_excel_column_names(data_file)
    for subject_num in (range(0, data_file.index[-1] + 1)):
        #TODO: change PATIENT here to factor in possible patient column names
        if not isinstance(data_row[subject_num, 'PATIENT'].item(), int):
            continue

        age = data_row[subject_num, 'AGE']
        if not age or age <= min_age or age >= max_age:
            continue

        lesion_size = data_row[subject_num, 'Total_LL']
        if not lesion_size < MAX_LESION_SIZE:
            continue

        num = data_row[subject_num, 'PATIENT']
        sex = data_row[subject_num, 'SEX']
        iq = data_row[subject_num, 'IQ']
        edu_level = data_row[subject_num, 'Edu_lev']

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
    # patient_healthy_control_data = np.empty((0,6))
    patient_healthy_control_data = []

    for control in control_list:
        weights = create_minkowski_weights()

        # NOTE: have to use cdist scipy function here to pass in collections of arrays.
        # Looked into using distance.minkowski func but can only pass in 1-D
        # arrays. Could maybe refactor in future.
        patient_closest_matches = patient_list[np.argsort(distance.cdist(np.atleast_2d(
            control), np.atleast_2d(patient_list), 'wminkowski', w=weights))][0]

        matches = patient_closest_matches.tolist()
        # match_not_already_in_patient_hc_data = (patient_closest_matches - patient_healthy_control_data)[0]
        # concatenated_array = np.concatenate((match_not_already_in_patient_hc_data,control),axis=0)
        # np.append(patient_healthy_control_data, concatenated_array, axis=0)

        # matches[0].append(patient_healthy_control_data)
        # TODO: get rid of second for loop, with commented-out code above
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

    format_data = pd.DataFrame(
        patient_healthy_control_data,
        columns=[
            'PATIENT',
            'AGE',
            'SEX',
            'IQ',
            'Edu_lev',
            'TOTAL LL',
            'HC',
            'HC-AGE',
            'HC-SEX',
            'HC-IQ',
            'HC-Edu_lev',
            'HC-TOTAL LL'])

    format_data.index += 1
    format_data.to_excel("minkowski_analysis_results.xlsx")


def main():
    subject_list = create_subject_list()
    ms_patients, healthy_controls = create_patient_and_healthy_control_lists(
        subject_list)
    patient_controls_matching_data = match_controls_with_patients(
        ms_patients, healthy_controls)
    create_excel_file(patient_controls_matching_data)


if __name__ == "__main__":
    main()
