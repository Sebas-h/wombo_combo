test:
	python \
		-m green \
		--verbose --verbose \
		--failfast \
		tests/test*.py


		# tests.test_event_up.TestKeySingleEvents.test_wip
mypy:
	python -m mypy main.py
