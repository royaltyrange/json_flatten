# HOW TO RUN ###

## 1) Download JSON files from google cloud storage
1) Download Files Via Gsutil:
```
gsutil -m cp -r -n dir gs://butcket/folder/path/*.json .
```
or
```
gsutil -m rsync -r gs://butcket/folder/path/ .
```
## 2) Prepare python environment (Install Dependencies)
1) Install poetry:
```
pip install poetry
```
2) Install dependencies:
```
poetry install
```
## 3) Run script
```
poetry run python -m app.main
```

Path examples:
- ``/path_to_files/**/`` read files recursively where ** folders name.
- ``/path_to_files/2022*`` read files where name starts 2022


