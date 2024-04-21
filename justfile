_project := "src"

lint:
    poetry run mypy {{ _project }}
    poetry run ruff check {{ _project }}

lint-fix:
    poetry run ruff check {{ _project }} --fix

format:
    poetry run ruff format {{ _project }}

run:
    poetry run python "{{ _project }}/main.py"
