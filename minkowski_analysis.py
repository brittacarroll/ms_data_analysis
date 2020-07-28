import pandas as pd
import sys
import getopt
import pdb
import numpy as np
import argparse
from scipy.spatial import distance

MAX_LESION_SIZE = 6
MIN_AGE = 20
MAX_AGE = 50

short_arg_options = "f:"
long_arg_options = ["file"]

DEFAULT_WEIGHTS = [0, 5, 5, 3, 3, 0]

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

# TODO: read two excel files, and concatenate data
# data_file_2 = pd.read_excel

# creates list with patients within range of min and max age, <6ml lesion size


def create_subject_list():
    subject_list = []
    for subject_num in (range(0, data_file.index[-1] + 1)):

        if not isinstance(data_file.loc[subject_num, 'PATIENT'].item(), int):
            continue

        age = data_file.loc[subject_num, 'AGE']
        if not age or age <= MIN_AGE or age >= MAX_AGE:
            continue

        lesion_size = data_file.loc[subject_num, 'Total_LL']
        if not lesion_size < MAX_LESION_SIZE:
            continue

        num = data_file.loc[subject_num, 'PATIENT']
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
