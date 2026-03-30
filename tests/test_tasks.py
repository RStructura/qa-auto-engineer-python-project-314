import time

import pytest

from pages.tasks_page import TasksPage


@pytest.mark.step_7_viewBoard
def test_view_tasks(auth_driver):
    # Авторизация и переход на страницу tasks
    page = TasksPage(auth_driver)
    page.open_tasks()

    # Проверка наличия фильтров на странице
    assert page.verify_filters_visible(), (
        "Фильтры на странице Tasks не загрузились"
    )

    # Проверка наличия задач на доске
    count = page.get_tasks_count()
    assert count > 0, "Задачи не отображаются на канбан-доске"

    print(f"\nУспех! Канбан-доска загружена. Найдено задач: {count}")


@pytest.mark.step_7_filtersTasks
def test_filter_tasks(auth_driver):
    # Авторизация и переход на страницу tasks
    page = TasksPage(auth_driver)
    page.open_tasks()

    # Фиксация исходного набора id задач до фильтрации
    initial_ids = set(page.get_all_task_ids())
    initial_count = len(initial_ids)

    assert initial_count > 0, "На доске нет задач до фильтрации"

    # Применение 3 фильтров
    page.select_filter("assignee_id", "john@google.com")
    page.select_filter("status_id", "Published")
    page.select_filter("label_id", "critical")
    time.sleep(1)

    # Сбор набора id после фильтрации
    filtered_ids = set(page.get_all_task_ids())
    filtered_count = len(filtered_ids)

    # Проверка, что после фильтрации:
    # 1) задачи остались
    # 2) набор задач изменился
    # 3) количество стало меньше
    assert filtered_count > 0, "После фильтрации задач нет"
    assert filtered_ids != initial_ids, "Фильтрация не изменила набор задач"
    assert filtered_count < initial_count, "Фильтры не сузили выборку"

    # Проверка фильтра по статусу:
    # после фильтрации все видимые задачи должны лежать только в Published
    published_ids = set(page.get_task_ids_in_column("Published"))
    assert filtered_ids == published_ids, (
        "После фильтра по статусу видны не только Published"
    )

    # Доп. проверка одной из отфильтрованных задач через Show + assignee, label
    first_task_id = next(iter(filtered_ids))
    page.open_task_show(first_task_id)

    details = page.get_current_page_text()
    assert "john@google.com" in details
    assert "critical" in details

    print(
        f"\nУспех! Фильтры работают. "
        f"Было задач: {initial_count}, стало: {filtered_count}"
    )


@pytest.mark.step_7_createTasks
def test_create_new_task(auth_driver):
    # Авторизация и переход на страницу tasks
    page = TasksPage(auth_driver)
    page.open_tasks()

    # Сохранение исходного количества задач
    initial_count = page.get_tasks_count()

    # Генерация уникальных данных новой задачи
    next_num = page.get_next_task_number()
    test_title = f"Task {next_num}"
    test_content = f"Description of task {next_num}"

    # Создание задачи
    page.create_task(
        assignee="emily@example.com",
        title=test_title,
        content=test_content,
        status="Draft",
        labels=["task", "feature"],
    )

    # Пауза для обработки UI
    time.sleep(2)

    # Возвращение на доску
    page.open_tasks()

    # Проверка количества задач
    final_count = page.get_tasks_count()
    assert final_count == initial_count + 1, (
        f"Ожидали {initial_count + 1} задач, но нашли {final_count}"
    )

    # Поиск новой задачи по title
    task_id = page.find_task_id_by_title(test_title)
    assert task_id is not None, f"Задача {test_title} не найдена"

    # Проверка статуса через положение задачи в колонке
    assert page.is_task_in_column(task_id, "Draft"), (
        "Новая задача не попала в колонку Draft"
    )

    # Проверка через доску: title + content
    card_text = page.get_task_text(task_id)
    assert test_title.lower() in card_text
    assert test_content.lower() in card_text

    # Проверка через show-страницу: assignee + labels
    page.open_task_show(task_id)
    details = page.get_current_page_text()

    assert "emily@example.com" in details
    assert test_title.lower() in details
    assert test_content.lower() in details
    assert "task" in details
    assert "feature" in details

    print(
        f"\nУспех! Было задач: {initial_count}, стало: {final_count}. "
        f"Задача '{test_title}' создана корректно."
    )


@pytest.mark.step_7_editTasks
def test_edit_task(auth_driver):
    # Авторизация и переход на страницу tasks
    page = TasksPage(auth_driver)
    page.open_tasks()

    # Данные существующей задачи
    task_id = 2
    page.open_task_edit(task_id)

    # Новые данные
    new_title = "Task 2 (updated)"
    new_content = "Description of task 2 (updated)"

    # Обновление
    page.update_task_fields(
        title=new_title,
        content=new_content,
    )

    # Возвращение на доску
    page.open_tasks()

    # Ожидание появления title в задаче
    page.wait_for_task_text(task_id, new_title)
    # Проверка, что задача все еще существует
    assert page.is_task_present(task_id), (
        f"После редактирования задача {task_id} пропала с доски"
    )

    # Проверка через доску: title + content
    card_text = page.get_task_text(task_id)
    assert new_title.lower() in card_text
    assert new_content.lower() in card_text

    print(
        f"\nУспех! Задача с ID = {task_id} успешно обновлена."
    )


@pytest.mark.step_7_dragAndDropTasks
def test_drag_and_drop_between_columns(auth_driver):
    # Авторизация и переход на страницу tasks
    page = TasksPage(auth_driver)
    page.open_tasks()

    task_id = 2
    start_status = "To Review"
    target_status = "Draft"

    # Проверка наличия задачи в нужной колонке
    assert page.is_task_in_column(task_id, start_status), (
        f"Ошибка: задача {task_id} должна быть в {start_status} "
        "перед началом теста"
    )

    # Днд карточки
    page.move_task_to_status(task_id, target_status)

    # Проверка смены статуса задачи
    assert page.is_task_in_column(task_id, target_status), (
        f"Задача {task_id} не перемещена в статус {target_status}"
    )

    print(
        f"\nУспех! Задача с ID = {task_id} "
        f"перемещена из '{start_status}' в '{target_status}'."
    )


@pytest.mark.step_7_deleteTasks
def test_delete_task_by_show(auth_driver):
    # Авторизация и переход на страницу tasks
    page = TasksPage(auth_driver)
    page.open_tasks()

    # Сохранение исходного количества задач
    initial_count = page.get_tasks_count()

    # Открытие существующей задачи через show
    task_id = 2
    assert page.is_task_present(task_id), f"Задача {task_id} не найдена"

    page.open_task_delete(task_id)

    # Удаление
    page.delete_task()
    time.sleep(1)

    # Обновление страницы на всякий случай
    page.open_tasks()

    # Проверка количества и отсутствие задачи
    final_count = page.get_tasks_count()
    assert final_count == initial_count - 1, (
        f"Ожидали {initial_count - 1} задач, но нашли {final_count}"
    )
    assert not page.is_task_present(task_id), (
        f"Карточка с ID = {task_id} не была удалена"
    )

    print(
        f"\nУспех! Было задач: {initial_count}, стало: {final_count}. "
        f"Карточка с ID = {task_id} удалена."
    )