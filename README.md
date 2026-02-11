# Student ML — Django + ML demo

Lightweight project demonstrating a small ML workflow (data loading, validation, training) alongside helper scripts and a Django app skeleton.

This repository contains:
- dataset.csv — dataset used for experiments
- add_normal_column.py — script that validates rows and adds a `normal` column
- performance/ — app containing data loading and training helpers
- student_ml/ — Django settings & project files (skeleton)
- model artifacts (e.g. performance/model.pkl) and tests

## Purpose

Provide reproducible scripts for:
- Validating student records and flagging rows as "normal" or "no"
- Training a simple model from the dataset
- Serving or integrating the model in a Django app (demo code included)

## The `normal` rules (implemented by add_normal_column.py)

For each CSV row the `normal` column is set to `yes` only when all these rules hold:
- `study_hours` is numeric and in range [0, 11]
- `sleep_hours` is numeric and in range [3, 10]
- `study_hours + sleep_hours` does not exceed 24
- If the student has extracurricular activities (column `extracurricular`), then `study_hours + sleep_hours` must be strictly less than 24 (cannot equal 24)

Rows failing any validation are marked `no`. The script also treats missing / non-numeric / ambiguous values as invalid.

## Quick start (Windows)

1. Create and activate a virtual environment
   - PowerShell:
     . .venv\Scripts\Activate.ps1
   - cmd:
     .venv\Scripts\activate.bat

2. Install recommended packages
   python -m pip install --upgrade pip
   pip install pandas scikit-learn django joblib

3. Validate dataset and produce new CSV
   python add_normal_column.py dataset.csv dataset_with_normal.csv

   Example output: dataset_with_normal.csv will include the new `normal` column with values `yes`/`no`.

## Running and testing (Django part)

- Apply migrations:
  python manage.py migrate

- Run tests:
  python manage.py test

- Start dev server:
  python manage.py runserver

Review files in `performance/` (load_data.py, train_model.py) before running training to understand dependencies and preprocessing expectations.

## Other validations and notes

- The validation script auto-detects columns named like `study_hours`, `sleep_hours`, and `extracurricular` case-insensitively. If headers differ, rename or modify the script.
- Ambiguous extracurricular values (not in typical truthy/falsy lists) are treated as invalid and will cause the row to be marked `no`.
- The script is written to be portable (uses csv.DictReader) and safe to run on large CSVs. Consider using pandas if you need higher performance or more complex preprocessing.

## Contributing

- Open an issue or submit a PR.
- Keep changes small and include tests for new validation rules or preprocessing changes.