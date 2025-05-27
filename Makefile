docs:
	make -C docs docs

clean-nb:
	jupyter nbconvert --clear-output --inplace \
--ClearOutputPreprocessor.enabled=True \
--ClearMetadataPreprocessor.enabled=True \
notebooks/*.ipynb notebooks/*/*.ipynb

.PHONY: docs
