install:
	pip install poetry pre-commit
	export PYTHON_KEYRING_BACKEND=keyring.backends.fail.Keyring & poetry install

mimic:
	wget -r -N -c -np --user simonellershawucl --ask-password https://physionet.org/files/mimiciii/1.4/NOTEEVENTS.csv.gz -P ./data
	gzip -d data/physionet.org/files/mimiciii/1.4/NOTEEVENTS.csv.gz
