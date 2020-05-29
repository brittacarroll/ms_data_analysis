
import pandas as pd
import sys, getopt
import pdb
import math
from more_itertools import flatten

MAX_LESION_SIZE = 6
MIN_AGE = 22
MAX_AGE = 46

short_arg_options = "f:"
long_arg_options = ["file"]

try:
    arguments, values = getopt.getopt(sys.argv, short_arg_options, long_arg_options)
except getopt.error as err:
    print("Please enter valid file name like so: -f {file_name}")
    sys.exit(2)

data_file = pd.read_excel(f'{sys.argv[-1]}')

# creates list with patients within range of min and max age, <6ml lesion size
def create_subject_list():
    subject_list = []
    for subject_num in range(0, data_file.index[-1]):
        person_data = {}

        if not isinstance(data_file.loc[subject_num, 'Patient'].item(), int):
            continue

        age = data_file.loc[subject_num, 'AGE']
        if not age or age <=MIN_AGE or age >= MAX_AGE:
            continue

        lesion_size = data_file.loc[subject_num,'Total_LL']
        if not lesion_size < MAX_LESION_SIZE:
            continue

        person_data['num'] = data_file.loc[subject_num, 'Patient'] 
        person_data['age'] = age
        person_data['sex'] = data_file.loc[subject_num, 'SEX']
        person_data['iq'] = data_file.loc[subject_num, 'IQ']
        person_data['edu_lev'] = data_file.loc[subject_num, 'Edu_lev']
        person_data['lesion_size'] = lesion_size

        subject_list.append(person_data)


    return subject_list

# divides subjects into MS patients and healthy controls
def create_ms_and_hc_lists(subject_list):
    ms_patients = []
    healthy_controls = []

    for subject in subject_list:
        if subject['num'] >= 1000:
            healthy_controls.append(subject)
        else:
            ms_patients.append(subject)

    return ms_patients, healthy_controls


def find_matching_healthy_controls(control, patient):
    match_age = math.isclose(control.get('age'), patient['age'], rel_tol=0.18)
    match_sex = math.isclose(control.get('sex'), patient['sex'], rel_tol=0.18)
    match_iq = math.isclose(control.get('iq'), patient['iq'], rel_tol=0.18)
    match_edu_level = math.isclose(control.get('edu_lev'), patient['edu_lev'], rel_tol=0.18)

    return match_age and match_sex and match_iq and match_edu_level


def create_list_healthy_control_nums(matching_hc):
    matching_hc_numbers = []
    for healthy_control in matching_hc:
        matching_hc_numbers.append(healthy_control['num'])
    
    return matching_hc_numbers


# matches MS patients with healthy controls by age and sex
def match_ms_and_healthy_controls(ms_patients, healthy_controls):
    matching_ms_patients = []
    matching_healthy_controls = []

    for patient in ms_patients:

        matching_hc = list(filter(lambda control: find_matching_healthy_controls(control, patient), healthy_controls))
        if not matching_hc:
            continue

        matching_hc_numbers = create_list_healthy_control_nums(matching_hc)
        patient['healthy_control_nums'] = matching_hc_numbers

        if patient not in matching_ms_patients:
            matching_ms_patients.append(patient)

        if matching_hc not in matching_healthy_controls:
            matching_healthy_controls.append(matching_hc)
    
    # Some MS patients match to the same healthy controls. If this is the case, and two or more MS patients
    # match to the exact same healthy controls, the code below picks the patient with the smallest lesion size.
    new_ms_patients_list = []
    for subject in matching_ms_patients:
        get_other_patients = list(filter(lambda n: n.get('healthy_control_nums') == subject['healthy_control_nums'], matching_ms_patients))
        if get_other_patients:
            seq = [x['lesion_size'] for x in get_other_patients]
            patient_with_smallest_lesion = list(filter(lambda control: control['lesion_size'] == min(seq), get_other_patients))

            if patient_with_smallest_lesion not in new_ms_patients_list:
                new_ms_patients_list.append(patient_with_smallest_lesion)
        
        else:
            new_ms_patients_list.append(subject)

    flattened_ms_patients_list = list(flatten(new_ms_patients_list))
    flattened_healthy_controls = list(flatten(matching_healthy_controls))
    return flattened_ms_patients_list, flattened_healthy_controls


# creates excel file with matching MS and HC data
def create_excel_file(matching_ms_patients, matching_healthy_controls):
    row_data = []
    already_added_control_nums = []
    for patient in matching_ms_patients:

        ignored_keys = ['healthy_control_nums']
        row_values = [value for key, value in patient.items() if key not in ignored_keys]

        # Sometimes MS patients will have overlapping matching controls. For example, 
        # 1 MS patient could match with [1002, 1008], whereas another patient could
        # match with [1002, 1004]. Code below keeps track of HC nums that have been 
        # included in the Excel sheet. If one is already added, will go on to find other HC.
        control_nums = patient['healthy_control_nums']
        for num in control_nums:
            if num in already_added_control_nums:
                continue
            else:
                patient_hc_matches = list(filter(lambda control: control['num'] == num, matching_healthy_controls))

                hc_matches = list(patient_hc_matches[0].values())
                joined_list = row_values + hc_matches
                row_data.append(joined_list)
                already_added_control_nums.append(num)
                break


    format_data = pd.DataFrame(row_data,
                   columns=['PATIENT', 'AGE', 'SEX', 'IQ', 'Edu_lev', 'TOTAL LL', 
                   'HC', 'HC-AGE', 'HC-SEX', 'HC-IQ', 'HC-Edu_lev', 'HC-TOTAL LL'])

    format_data.index += 1
    format_data.to_excel("iq_change.xlsx")  


def main():
    subject_list = create_subject_list()
    ms_patients, healthy_controls = create_ms_and_hc_lists(subject_list)
    matching_ms_patients, matching_healthy_controls = match_ms_and_healthy_controls(ms_patients, healthy_controls)
    create_excel_file(matching_ms_patients, matching_healthy_controls)

if __name__ == "__main__":
    main()












