build: test_requirements test

clean:
	-find . -type f -name "*.pyc" -delete
	-find . -type d -name "__pycache__" -delete

test_requirements:
	pip install -e .[test]

flake8:
	flake8 . --exclude=.venv --max-line-length=120

pytest:
	pytest . --capture=no

pytest_codecov:
	pytest \
		--junitxml=test-reports/junit.xml \
		--cov-config=.coveragerc \
		--cov-report=term \
		--cov=. \
		--codecov \
		$(ARGUMENTS)


test: flake8 pytest_codecov

publish:
	rm -rf build dist; \
	python setup.py bdist_wheel; \
	twine upload --username $$DIRECTORY_PYPI_USERNAME --password $$DIRECTORY_PYPI_PASSWORD dist/*

.PHONY: build clean test_requirements flake8 pytest test publish

