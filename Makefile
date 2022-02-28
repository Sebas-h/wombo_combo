test:
	python \
		-m green \
		--verbose --verbose \
		--failfast \
		tests/test*.py
		#tests.test_event_up.TestKeySingleEvents.test_target_up_key_in_multiple_targets_some_down


		# tests.test_event_up.TestKeySingleEvents.test_wip
mypy:
	python -m mypy main.py
