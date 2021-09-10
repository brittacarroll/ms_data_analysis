# Install Homebrew (Mac)
/bin / bash - c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"

# Install Python - 3.7.7
brew install python3

# Create virtual environment - VENV
Run on command line, inside of project folder:
1. python3 - m venv NAME_OF_VENV
2. source venv / bin / activate

More on virtual envs: [here](https: // towardsdatascience.com / virtual - environments - 104c62d48c54)

# Create requirements.txt
pip freeze > requirements.txt

# The Excel file that is passed into this script must contain the
# following column names:

possible_patient_column_names = [
    'SUBJECT',
    'Subject',
    'subject',
    'PATIENT',
    'patient',
    'Patient',
    'Num',
    'Patient Num',
    'patient num',
    'Patient num']

possible_age_column_names = ['AGE', 'age', 'Age']

possible_sex_column_names = ['SEX', 'sex', 'Sex']

possible_iq_column_names = ['IQ', 'iq']

possible_edu_level_column_names = [
    'Edu level',
    'EDU_LEVEL',
    'Education Level',
    'Education',
    'EDUCATION',
    'Edu lev',
    'Edu_lev']

possible_lesion_load_column_names = [
    'Total_LL',
    'lesion load',
    'Lesion Load',
    'Total LL']

possible_set_number_names = [
    'Set',
    'set',
    'Data set num',
    'Data Set',
    'Data set',
    'data set',
    'data set num']

# Run code

python3 run minkowski_analysis.py -f NAME_OF_EXCEL_FILE

*Command line arguments *:

-file or -f:
1. Type: Required
2. Usage: Input Excel file that contains all of data to be analyzed.
Example: python3 minkowski_analysis.py - file 'Excel_file.xlsx'

NOTE: use the arguments below if you would like to input your own weights per each variable.
If you input just one weight for a certain variable, all other variable weights will be set to 0. This means that only the variable weights that you input will be used in the analysis.

If no optional arguments are inputed, the default weights are 5, 5, 3, 3 for age, sex, IQ, and education level respectively.

*Optional command line arguments *:

--age or -a:
1. Usage: Use this argument if you would like to use the age variable to compare patients and controls. This will set an 'age weight'. Higher number = heavier weight in Minkowski analysis.

Example: --age 4:
(4 if the weight in this case)

--sex or -s:
1. Usage: Use this is want to use sex variable to compare patients and controls. Same as --age argument above, the number following this variable will be the weight attached to it during analysis.

Example: --sex 3

--IQ or -IQ:
1. Usage: IQ weight(same as age and sex above).
Example: --IQ 3

--edu_level or -el:
1. Usage: Education level weight(same as other args above).
Example: --edu_level 2
