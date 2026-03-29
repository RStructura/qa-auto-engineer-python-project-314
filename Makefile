install:
	uv sync

start:
	docker run --rm -p 5173:5173 hexletprojects/qa_auto_python_testing_kanban_board_project_ru_app

APP_BASE_URL ?= http://localhost:5173
export APP_BASE_URL

check:
	$(MAKE) lint
	$(MAKE) test_all

lint:
	uv run ruff check

lint_fix:
	uv run ruff check --fix

test_all:
	uv run pytest tests/ -sv --tb=short

test-coverage:
	uv run pytest --cov=pages --cov-report=xml tests/

# ---------------------------------------

debug_all:
	uv run pytest tests/ -vv -ra -s \
	    --tb=long --showlocals --durations=10 --maxfail=1

debug_users:
	uv run pytest tests/test_users.py -vv -ra -s \
	    --tb=long --showlocals --durations=10 --maxfail=1

debug_statuses:
	uv run pytest tests/test_statuses.py -vv -ra -s \
	    --tb=long --showlocals --durations=10 --maxfail=1

debug_labels:
	uv run pytest tests/test_labels.py -vv -ra -s \
	    --tb=long --showlocals --durations=10 --maxfail=1

debug_tasks:
	uv run pytest tests/test_tasks.py -vv -ra -s \
	    --tb=long --showlocals --durations=10 --maxfail=1

# ---------------------------------------

smoke_test:
	uv run pytest -k smoke -sv --tb=short

# ---------------------------------------

auth_test:
	uv run pytest -k step_3 -sv --tb=short

# ---------------------------------------

test_step4_users:
	uv run pytest tests/test_users.py -sv --tb=short

test_step4_view:
	uv run pytest -k step_4_viewList -sv --tb=short

test_step4_create:
	uv run pytest -k step_4_createUser -sv --tb=short

test_step4_edit:
	uv run pytest -k step_4_editUser -sv --tb=short

test_step4_deleteOne:
	uv run pytest -k step_4_deleteOne -sv --tb=short

test_step4_deleteAll:
	uv run pytest -k step_4_deleteAll -sv --tb=short

# ---------------------------------------

test_step5_statuses:
	uv run pytest tests/test_statuses.py -sv --tb=short

test_step5_view:
	uv run pytest -k step_5_viewList -sv --tb=short

test_step5_create:
	uv run pytest -k step_5_createStatus -sv --tb=short

test_step5_edit:
	uv run pytest -k step_5_editStatus -sv --tb=short

test_step5_deleteOne:
	uv run pytest -k step_5_deleteOne -sv --tb=short

test_step5_deleteAll:
	uv run pytest -k step_5_deleteAll -sv --tb=short

# ---------------------------------------

test_step6_labels:
	uv run pytest tests/test_labels.py -sv --tb=short

test_step6_view:
	uv run pytest -k step_6_viewList -sv --tb=short

test_step6_create:
	uv run pytest -k step_6_createLabel -sv --tb=short

test_step6_edit:
	uv run pytest -k step_6_editLabel -sv --tb=short

test_step6_deleteOne:
	uv run pytest -k step_6_deleteOne -sv --tb=short

test_step6_deleteAll:
	uv run pytest -k step_6_deleteAll -sv --tb=short

# ---------------------------------------

test_step7_tasks:
	uv run pytest tests/test_tasks.py -sv --tb=short

test_step7_view:
	uv run pytest -k step_7_viewBoard -sv --tb=short

test_step7_filter:
	uv run pytest -k step_7_filtersTasks -sv --tb=short

test_step7_create:
	uv run pytest -k step_7_createTasks -sv --tb=short

test_step7_edit:
	uv run pytest -k step_7_editTasks -sv --tb=short

test_step7_dnd:
	uv run pytest -k step_7_dragAndDropTasks -sv --tb=short

test_step7_delete:
	uv run pytest -k step_7_deleteTasks -sv --tb=short

