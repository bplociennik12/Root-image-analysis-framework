# Maintenance Notes

Before each commit, run:

python -m pytest -q
git status

Do not commit:

- .venv/
- outputs/
- data/raw/
- cache files
- private laboratory data
- large raw images

Project rule:

No silent transformations.
No silent exclusions.
No silent measurements.

Every cleaning decision should be traceable in audit_log.csv.
Every image-processing step should be traceable in processing_log.csv.
