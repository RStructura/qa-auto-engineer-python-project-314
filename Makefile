lint:
	uv run ruff check

install:
	uv sync

start:
	docker run --rm -p 5174:5173 hexletprojects/qa_auto_python_testing_kanban_board_project_ru_app

export APP_BASE_URL=http://localhost:5173

smoke_test:
	uv run pytest -k smoke

test:
	uv run pytest -k "not smoke"
