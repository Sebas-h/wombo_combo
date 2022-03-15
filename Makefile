test:
	python \
		-m green \
		--verbose --verbose \
		--failfast \
		tests/test*.py
#tests.test_event_up.TestKeySingleEvents.test_target_up_key_in_multiple_targets_some_down
# tests.test_event_up.TestKeySingleEvents.test_wip

full-test:
	python \
		-m green \
		--verbose --verbose \
		tests/test*.py

mypy:
	python -m mypy --exclude '.*misc/.*' .

black:
	python -m black -l 80 .

isort:
	python -m isort --profile black .
