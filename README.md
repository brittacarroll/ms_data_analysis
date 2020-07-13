# Install Homebrew (Mac)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"

# Install Python - 3.7.7
brew install python3

# Create virtual environment - VENV
https://towardsdatascience.com/virtual-environments-104c62d48c54

# Install requirements.txt
pip freeze > requirements.txt

# Run code
python3 data_analysis_script.py -f {file_name}

