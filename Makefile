
lint:
	uv run ruff check

lint_fix:
	uv run ruff check --fix

start:
	docker run --rm -p 5173:5173 hexletprojects/qa_auto_python_testing_kanban_board_project_ru_app

export APP_BASE_URL=http://localhost:5173

smoke_test:
	uv run pytest -k smoke -sv

auth_test:
	uv run pytest -k step_3 -sv

test_step4:
	uv run pytest tests/test_users.py -sv

test_step4_view:
	uv run pytest -k step_4_viewList -sv

test_step4_create:
	uv run pytest -k step_4_createUser -sv

test_step4_edit:
	uv run pytest -k step_4_editUser -sv

test_step4_deleteOne:
	uv run pytest -k step_4_deleteOne -sv

test_step4_deleteAll:
	uv run pytest -k step_4_deleteAll -sv

test_step5:
	uv run pytest tests/test_statuses.py -sv

test_step5_view:
	uv run pytest -k step_5_viewList -sv

test_step5_create:
	uv run pytest -k step_5_createStatus -sv

test_step5_edit:
	uv run pytest -k step_5_editStatus -sv

test_step5_deleteOne:
	uv run pytest -k step_5_deleteOne -sv

test_step5_deleteAll:
	uv run pytest -k step_5_deleteAll -sv

tasks_test:
	uv run pytest -k step_tasks -sv
