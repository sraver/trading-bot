
install:
	pip install -r requirements.txt

update-req:
	pip-compile --output-file=- > requirements.txt
