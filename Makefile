APP_BASE_URL ?= http://localhost:5173
export APP_BASE_URL

PYTEST_DEBUG_FLAGS = -vv -ra -s \
	--tb=long --showlocals --durations=10 --maxfail=1

DOCKER_IMAGE = hexletprojects/qa_auto_python_testing_kanban_board_project_ru_app
DOCKER_CONTAINER = kanban-app

.PHONY: \
	install start stop restart lint lint_fix check test_all test-coverage \
	debug_all debug_auth debug_users debug_statuses debug_labels debug_tasks \
	smoke_test auth_test \
	test_step4_users test_step4_view test_step4_create test_step4_edit \
	test_step4_deleteOne test_step4_deleteAll \
	test_step5_statuses test_step5_view test_step5_create test_step5_edit \
	test_step5_deleteOne test_step5_deleteAll \
	test_step6_labels test_step6_view test_step6_create test_step6_edit \
	test_step6_deleteOne test_step6_deleteAll \
	test_step7_tasks test_step7_view test_step7_filter test_step7_create \
	test_step7_edit test_step7_dnd test_step7_delete

install:
	uv sync

start:
	docker run --rm -d \
		--name $(DOCKER_CONTAINER) \
		-p 5173:5173 \
		$(DOCKER_IMAGE)

stop:
	-docker stop $(DOCKER_CONTAINER)

restart:
	$(MAKE) stop
	$(MAKE) start

check:
	$(MAKE) lint
	$(MAKE) test_all

lint:
	uv run ruff check .

lint_fix:
	uv run ruff check . --fix

test_all:
	uv run pytest tests/ -sv --tb=short

test-coverage:
	uv run pytest \
		--cov=tests \
		--cov=conftest \
		--cov-report=xml \
		tests/

# HEADLESS=0 — браузер с окном / 1 — браузер без окна
# SLOWMO=0 — обычная скорость / 1 — медленные клики и ввод

debug_all:
	HEADLESS=0 SLOWMO=1 uv run pytest tests/ $(PYTEST_DEBUG_FLAGS)

debug_auth:
	HEADLESS=0 SLOWMO=1 uv run pytest tests/test_auth_flow.py \
		$(PYTEST_DEBUG_FLAGS)

debug_users:
	HEADLESS=0 SLOWMO=1 uv run pytest tests/test_users.py \
		$(PYTEST_DEBUG_FLAGS)

debug_statuses:
	HEADLESS=0 SLOWMO=1 uv run pytest tests/test_statuses.py \
		$(PYTEST_DEBUG_FLAGS)

debug_labels:
	HEADLESS=0 SLOWMO=1 uv run pytest tests/test_labels.py \
		$(PYTEST_DEBUG_FLAGS)

debug_tasks:
	HEADLESS=0 SLOWMO=1 uv run pytest tests/test_tasks.py \
		$(PYTEST_DEBUG_FLAGS)

smoke_test:
	uv run pytest -k smoke -sv --tb=short

auth_test:
	uv run pytest -k step_3 -sv --tb=short

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
