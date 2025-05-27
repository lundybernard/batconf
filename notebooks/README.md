# Notebooks

This directory contains several example notebooks,
which demonstrate how to use BatConf with your notebooks.

## Clean Notebooks before committing changes

Dirty notebooks will cause your PR to fail.

To clean all notebooks run:
`make clean-nb`

or

`jupyter nbconvert --clear-output --inplace \
--ClearOutputPreprocessor.enabled=True \
--ClearMetadataPreprocessor.enabled=True \
notebooks/*.ipynb`
