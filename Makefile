docs:
	make -C docs docs

clean-nb:
	jupyter nbconvert --clear-output --inplace \
--ClearOutputPreprocessor.enabled=True \
--ClearMetadataPreprocessor.enabled=True \
notebooks/*.ipynb notebooks/*/*.ipynb

scorecard:
	@if [ -z "$$GITHUB_AUTH_TOKEN" ]; then \
		echo "Error: GITHUB_AUTH_TOKEN is not set."; \
		exit 1; \
	fi
	docker run -e GITHUB_AUTH_TOKEN=$$GITHUB_AUTH_TOKEN \
		-v $(shell pwd):/src \
		gcr.io/openssf/scorecard:stable \
		--local /src \
		--ignore-paths ".ruff_cache/*,.pytest_cache/*,*.pyc,__pycache__/*,dist/*"

.PHONY: docs, scorecard
