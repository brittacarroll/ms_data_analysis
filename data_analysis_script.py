
import pandas as pd
import sys, getopt
import pdb
import math

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

        print('appending person data')
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
    match_age = control.get('age') == patient['age']
    match_sex = control.get('sex') == patient['sex']
    match_iq = math.isclose(control.get('iq'), patient['iq'], rel_tol=0.20)
    match_edu_level = math.isclose(control.get('edu_lev'), patient['edu_lev'], rel_tol=0.20)

    if match_age and match_sex and match_iq and match_edu_level:
        return True
    else:
        return False

# matches MS patients with healthy controls by age and sex
def match_ms_and_healthy_controls(ms_patients, healthy_controls):
    matching_ms_patients = []
    matching_healthy_controls = {}

    for patient in ms_patients:
        # find in hc_controls where age and sex match those of MS patient
        matching_hc = list(filter(lambda control: find_matching_healthy_controls(control, patient), healthy_controls))

        if matching_hc:
            matching_healthy_controls[patient['num']] = matching_hc
            matching_ms_patients.append(patient)

    return matching_ms_patients, matching_healthy_controls


# creates excel file with matching MS and HC data
def create_excel_file(matching_ms_patients, matching_healthy_controls):
    row_data = []
    for patient in matching_ms_patients:

        row_values = list(patient.values())
        patient_hc_matches = matching_healthy_controls.get(patient['num'], None)

        if patient_hc_matches:
            hc_matches = list(patient_hc_matches[0].values())
            joined_list = row_values + hc_matches
            row_data.append(joined_list)
        else:
            row_data.append(row_values)

    format_data = pd.DataFrame(row_data,
                   columns=['PATIENT', 'AGE', 'SEX', 'IQ', 'Edu_lev', 'TOTAL LL', 
                   'HC', 'HC-AGE', 'HC-SEX', 'HC-IQ', 'HC-Edu_lev', 'HC-TOTAL LL'])

    format_data.index += 1
    format_data.to_excel("filtered_data_output.xlsx")  


def main():
    subject_list = create_subject_list()
    ms_patients, healthy_controls = create_ms_and_hc_lists(subject_list)
    matching_ms_patients, matching_healthy_controls = match_ms_and_healthy_controls(ms_patients, healthy_controls)
    create_excel_file(matching_ms_patients, matching_healthy_controls)

if __name__ == "__main__":
    main()












