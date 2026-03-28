import random
import time

import pytest

from pages.tasks_page import TasksPage


# Просмотр и фильтрация | Откройте список задач...
@pytest.mark.step_7_viewBoard
def test_view_tasks(auth_driver):
    # Авторизация и переход на страницу
    page = TasksPage(auth_driver)
    page.open_tasks()

    # Проверка видимости и названий фильтров
    assert page.verify_filters_visible(), (
        "Фильтры на странице Tasks не загрузились"
    )

    # Проверка наличия задач на доске
    count = page.get_tasks_count()
    assert count > 0, "Задачи не отображаются на канбан-доске"

    print(f"\nУспех! Канбан-доска загружена. Найдено задач: {count}")


@pytest.mark.step_7_filtersTasks
def test_filter_tasks(auth_driver):
    page = TasksPage(auth_driver)
    page.open_tasks()

    initial_count = page.get_tasks_count()
    
    assert initial_count > 0, "На доске нет задач до фильтрации"

    # Выбор фильтров
    page.select_filter("assignee_id", "john@google.com")
    page.select_filter("status_id", "Published")
    page.select_filter("label_id", "critical")
    time.sleep(1)

    filtered_count = page.get_tasks_count()
    assert filtered_count > 0, "После фильтрации не найдено задач"
    assert filtered_count < initial_count, "Фильтры не сузили список задач"

    # Проверка выбора фильтров
    page_context = page.get_page_context().lower()
    assert "john@google.com" in page_context
    assert "published" in page_context
    assert "critical" in page_context
    
    # Проверка загрузки задач
    count = page.get_tasks_count()

    print(f"\nУспех! Фильтры работают. Найдено задач: {count}")


# Создание задачи | Проверьте, что форма создания отображается корректно...
@pytest.mark.step_7_createTasks
def test_create_new_task(auth_driver):
    page = TasksPage(auth_driver)
    page.open_tasks()
    
    # Создание переменных для проверки количества задач
    initial_count = page.get_tasks_count()
    next_num = page.get_next_task_number()

    # Создание переменных для генерации данных
    test_title = f"Task {next_num}"
    test_content = f"Description of task {next_num}"

    # Данные для задачи:
    page.create_task(
        assignee="emily@example.com",
        title=test_title,
        content=test_content,
        status="Draft",
        labels=["task", "feature"]
    )

    # Пауза для проверки
    time.sleep(3)

    # Переход с success экрана на страницу Tasks
    page.open_tasks()

    # Проверка появления новой задачи в списке
    assert test_title in page.get_page_context(), (
        f"Задача {test_title} не найдена!"
    )

    # Подсчет количества задач
    final_count = page.get_tasks_count()
    assert final_count == initial_count + 1, (
        f"Ожидали {initial_count + 1} задач, но нашли {final_count}"
    )

    print(
        f"\nУспех! Было задач: {initial_count}, стало: {final_count}. "
        f"Карточка '{test_title}' появилась на доске."
    )


# Редактирование | Обновите данные существующей задачи...
@pytest.mark.step_7_editTasks
def test_edit_task(auth_driver):
    page = TasksPage(auth_driver)
    page.open_tasks()

    # Выбор существующей задачи
    task_id = 2
    page.open_task_edit(task_id)

    # Данные для обновления
    new_assignee = "peter@outlook.com"
    new_title = "Task 2 (updated)"
    new_content = "Description of task 2 (updated)"
    new_status = "Draft"
    old_labels = ["bug", "feature"]
    new_labels = ["task", "enhancement"] 

    # Редактирование
    page.update_task_fields(
        title=new_title,
        content=new_content,
        assignee=new_assignee,
        status=new_status,
        old_labels=old_labels,
        new_labels=new_labels
    )

    # Проверка обновления данных
    new_label_random = random.choice(new_labels)
    context = page.get_page_context()
    
    assert new_title in context, f"Новый заголовок '{new_title}' не найден!"
    assert new_content in context, f"Новое описание '{new_content}' не найдено!"

    # Проверка через фильтрацию
    page.select_filter("assignee_id", new_assignee)
    page.select_filter("status_id", new_status)
    page.select_filter("label_id", new_label_random)
    
    # Получение обновленного контекста
    page_context = page.get_page_context()
    
    assert new_assignee in page_context.lower()
    assert new_status in page_context
    assert new_label_random in page_context.lower()

    print(
        f"\nУспех! Задача с ID = {task_id} успешно обновлена. "
        "Новые данные подтверждены."
    )


# Перемещение между колонками | Перетащите карточку в другой статус...
@pytest.mark.step_7_dragAndDropTasks
def test_drag_and_drop_between_columns(auth_driver):
    page = TasksPage(auth_driver)
    page.open_tasks()

    task_id = 2
    start_status = "To Review"
    target_status = "Draft"

    # Проверка стартового статуса задачи
    assert page.is_task_in_column(task_id, start_status), (
        f"Ошибка: Задача {task_id} должна быть в {start_status} "
        "перед началом теста!"
    )

    # Перемещение
    page.move_task_to_status(task_id, target_status)

    # Проверка перемещения в целевой статус
    assert page.is_task_in_column(task_id, target_status), \
        f"Задача {task_id} не перемещена в статус {target_status}!"

    print(f"\nУспех! Задача с ID = {task_id} "
        f"перемещена из статуса '{start_status}' в '{target_status}'."
    )


# Удаление | Удалите задачу и убедитесь...
@pytest.mark.step_7_deleteTasks
def test_delete_task_by_show(auth_driver):
    page = TasksPage(auth_driver)
    page.open_tasks()

    # Создание переменных для проверки количества задач
    initial_count = page.get_tasks_count()

    # Выбор существующей задачи
    task_id = 2
    page.open_task_delete(task_id)   

    # Удаление
    page.delete_task()

    # Подсчет количества задач
    final_count = page.get_tasks_count()

    assert final_count == initial_count - 1, (
        f"Ожидали {initial_count - 1} задач, но нашли {final_count}")

    print(
        f"\nУспех! Было задач: {initial_count}, стало: {final_count}. "
        f"Карточка с ID = '{task_id}' удалена с доски."
    )