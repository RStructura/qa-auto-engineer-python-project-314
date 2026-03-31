import time

import pytest

from pages.tasks_page import TasksPage


def build_unique_task_payload(prefix):
    """Генерация уникальных title/content"""
    unique_value = time.time_ns()
    title = f"{prefix} {unique_value}"
    content = f"Description {unique_value}"
    return title, content


def create_task_and_get_id(
    page,
    *,
    assignee,
    status,
    labels,
    prefix,
):
    """
    Создание задачи и проверка:
    task_id, title, content, count_before_create, count_after_create
    """
    page.open_tasks()
    count_before_create = page.get_tasks_count()

    title, content = build_unique_task_payload(prefix)

    page.create_task(
        assignee=assignee,
        title=title,
        content=content,
        status=status,
        labels=labels,
    )

    time.sleep(2)
    page.open_tasks()

    count_after_create = page.get_tasks_count()
    assert count_after_create == count_before_create + 1, (
        f"Ожидали {count_before_create + 1} задач, "
        f"но нашли {count_after_create}"
    )

    task_id = page.find_task_id_by_title(title)
    assert task_id is not None, f"Задача {title} не найдена"

    return (
        task_id,
        title,
        content,
        count_before_create,
        count_after_create,
    )


def apply_default_filters(page):
    """Все фильтры"""
    page.select_filter("assignee_id", "john@google.com")
    page.select_filter("status_id", "Published")
    page.select_filter("label_id", "critical")
    time.sleep(1)


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
    apply_default_filters(page)
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

    # Проверка фильтра по статусу Published
    published_ids = set(page.get_task_ids_in_column("Published"))
    assert filtered_ids == published_ids, (
        "После фильтра по статусу видны не только Published"
    )

    # Доп. проверка каждой видимой задачи
    for task_id in sorted(filtered_ids):
        page.open_task_show(task_id)
        details = page.get_current_page_text()

        assert "john@google.com" in details, (
            f"Задача {task_id} не соответствует фильтру assignee"
        )
        assert "critical" in details, (
            f"Задача {task_id} не соответствует фильтру label"
        )

        # Возврат на доску и повторная проверка через фильтры
        page.open_tasks()
        apply_default_filters(page)

    print(
        f"\nУспех! Фильтры работают. "
        f"Было задач: {initial_count}, стало: {filtered_count}"
    )


@pytest.mark.step_7_createTasks
def test_create_new_task(auth_driver):
    # Авторизация и переход на страницу tasks
    page = TasksPage(auth_driver)

    (
        task_id,
        test_title,
        test_content,
        initial_count,
        final_count,
    ) = create_task_and_get_id(
        page,
        assignee="emily@example.com",
        status="Draft",
        labels=["task", "feature"],
        prefix="Create Task",
    )

    # Проверка статуса через положение задачи в колонке
    assert page.is_task_in_column(task_id, "Draft"), (
        "Новая задача не попала в колонку Draft"
    )

    # Проверка через доску: title + content
    assert page.get_task_title(task_id).lower() == test_title.lower()
    assert page.get_task_content(task_id).lower() == test_content.lower()

    # Проверка через show-страницу: assignee + labels + title/content
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

    # Создание собственной задачи и продолжение работы с ней
    (
        task_id,
        old_title,
        old_content,
        _count_before_create,
        _count_after_create,
    ) = create_task_and_get_id(
        page,
        assignee="john@google.com",
        status="Draft",
        labels=["task"],
        prefix="Edit Task",
    )

    page.open_task_edit(task_id)

    # Новые данные
    new_title, new_content = build_unique_task_payload("Edited Task")

    # Обновление
    page.update_task_fields(
        title=new_title,
        content=new_content,
    )

    # Возвращение на доску
    page.open_tasks()
    page.wait_for_task_title(task_id, new_title)

    # Проверка наличия задачи на доске
    assert page.is_task_present(task_id), (
        f"После редактирования задача {task_id} пропала с доски"
    )

    current_title = page.get_task_title(task_id)
    current_content = page.get_task_content(task_id)

    # Проверка обновления на новые значения
    assert current_title.lower() == new_title.lower()
    assert current_content.lower() == new_content.lower()

    # Проверка исчезновения старых значений
    assert current_title.lower() != old_title.lower()
    assert current_content.lower() != old_content.lower()

    print(
        f"\nУспех! Задача с ID = {task_id} успешно обновлена."
    )


@pytest.mark.step_7_dragAndDropTasks
def test_drag_and_drop_between_columns(auth_driver):
    # Авторизация и переход на страницу tasks
    page = TasksPage(auth_driver)

    # Создание задачи
    (
        task_id,
        title,
        content,
        _count_before_create,
        _count_after_create,
    ) = create_task_and_get_id(
        page,
        assignee="john@google.com",
        status="To Review",
        labels=["bug"],
        prefix="DnD Task",
    )

    start_status = "To Review"
    target_status = "Draft"

    # Проверка наличия задачи в нужной колонке
    assert page.is_task_in_column(task_id, start_status), (
        f"Задача {task_id} должна быть в {start_status} перед началом теста"
    )

    # Днд карточки
    page.move_task_to_status(task_id, target_status)

    # Проверка смены статуса задачи
    assert not page.is_task_in_column(task_id, start_status), (
        f"Задача {task_id} осталась в {start_status}"
    )
    assert page.is_task_in_column(task_id, target_status), (
        f"Задача {task_id} не перемещена в {target_status}"
    )

    assert page.get_task_title(task_id).lower() == title.lower()
    assert page.get_task_content(task_id).lower() == content.lower()

    print(
        f"\nУспех! Задача с ID = {task_id} "
        f"перемещена из '{start_status}' в '{target_status}'."
    )


@pytest.mark.step_7_deleteTasks
def test_delete_task_by_show(auth_driver):
    # Авторизация и переход на страницу tasks
    page = TasksPage(auth_driver)

    # Создание и удаление задачи
    (
        task_id,
        title,
        _content,
        _count_before_create,
        count_before_delete,
    ) = create_task_and_get_id(
        page,
        assignee="john@google.com",
        status="Draft",
        labels=["task"],
        prefix="Delete Task",
    )

    assert page.is_task_present(task_id), f"Задача {task_id} не найдена"

    page.open_task_delete(task_id)

    # Удаление
    page.delete_task()
    time.sleep(1)

    # Обновление страницы
    page.open_tasks()
    page.wait_for_task_absence(task_id)

    # Проверка количества и отсутствие задачи
    final_count = page.get_tasks_count()
    assert final_count == count_before_delete - 1, (
        f"Ожидали {count_before_delete - 1} задач, но нашли {final_count}"
    )
    assert not page.is_task_present(task_id), (
        f"Карточка с ID = {task_id} не была удалена"
    )

    # Доп. проверка на отсутствие созданной задачи через title
    page_context = page.get_page_context().lower()
    assert title.lower() not in page_context, (
        f"Удаленная задача '{title}' все еще видна на странице"
    )
    
    print(
        f"\nУспех! Было задач: {count_before_delete}, стало: {final_count}. "
        f"Карточка с ID = {task_id} удалена."
    )