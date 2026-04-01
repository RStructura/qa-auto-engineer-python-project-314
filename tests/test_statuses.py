import time

import pytest
from selenium.webdriver.common.by import By

from pages.statuses_page import StatusesPage


def build_unique_status_payload(prefix="Status"):
    """
    Генерация уникальных name/slug.
    time.time_ns() надежнее, чем int(time.time()).
    """
    unique_value = time.time_ns()
    name = f"{prefix}_{unique_value}"
    slug = f"slug_{unique_value}"
    return name, slug


def create_status_and_get_state(page, prefix="Status"):
    """
    Создает status и возвращает:
    new_name, new_slug, count_before_create, count_after_create
    """
    page.open_statuses()
    count_before_create = page.get_statuses_count()

    new_name, new_slug = build_unique_status_payload(prefix)

    page.click_create()
    page.fill_status_form(name=new_name, slug=new_slug)
    page.click_save()

    page.open_statuses()
    page.wait_for_status_present(new_name)

    count_after_create = page.get_statuses_count()

    assert count_after_create == count_before_create + 1, (
        f"Ожидали {count_before_create + 1} statuses, "
        f"но нашли {count_after_create}"
    )
    assert page.is_status_present(new_name), (
        f"Status '{new_name}' не найден в списке"
    )

    return new_name, new_slug, count_before_create, count_after_create


@pytest.mark.step_5_viewList
def test_view_statuses_list(auth_driver):
    # Проверка открытия списка и загрузки страницы
    page = StatusesPage(auth_driver)
    page.open_statuses()

    # Проверка наличия элементов и списка
    header_text = auth_driver.find_element(
        By.CSS_SELECTOR,
        "table thead",
    ).text
    assert "Name" in header_text
    assert "Slug" in header_text
    assert page.get_statuses_count() > 0, "Список statuses пуст"

    first_name = auth_driver.find_element(
        By.CSS_SELECTOR,
        "tbody tr:first-child td.column-name",
    ).text.strip()
    first_slug = auth_driver.find_element(
        By.CSS_SELECTOR,
        "tbody tr:first-child td.column-slug",
    ).text.strip()

    assert first_name, "Name в первой строке пустой"
    assert first_slug, "Slug в первой строке пустой"

    print("\nУспех! Список и колонки отображаются.")


@pytest.mark.step_5_createStatus
def test_create_status(auth_driver):
    page = StatusesPage(auth_driver)

    new_name, new_slug, count_before, count_after = create_status_and_get_state(
        page,
        prefix="CreateStatus",
    )

    row_text = page.get_status_row_text(new_name)
    assert new_name in row_text
    assert new_slug in row_text

    print(
        f"\nУспех! Статус {new_name} появился в списке. "
        f"Было: {count_before}, стало: {count_after}"
    )


@pytest.mark.step_5_editStatus
def test_edit_status(auth_driver):
    page = StatusesPage(auth_driver)

    old_name, old_slug, _, _ = create_status_and_get_state(
        page,
        prefix="EditStatusOld",
    )

    page.open_statuses()
    page.open_status_by_name(old_name)

    # Проверка валидации пустых полей
    page.force_clear_input("name")
    page.force_clear_input("slug")
    page.click_save()
    assert "required" in page.get_error_message().lower()

    # Обновление значений и сохранение
    new_name, new_slug = build_unique_status_payload("EditStatusNew")
    page.fill_status_form(name=new_name, slug=new_slug)
    page.click_save()

    page.open_statuses()
    page.wait_for_status_present(new_name)

    # Проверяем появление нового и исчезновение старого
    assert page.is_status_present(new_name)
    assert not page.is_status_present(old_name)

    row_text = page.get_status_row_text(new_name)
    assert new_name in row_text
    assert new_slug in row_text
    assert old_name not in row_text
    assert old_slug not in row_text

    print("\nУспех! Редактирование и валидация проверены.")


@pytest.mark.step_5_deleteOne
def test_delete_status_via_checkbox(auth_driver):
    page = StatusesPage(auth_driver)

    (
        target_name, _target_slug, _, count_before_delete
    ) = create_status_and_get_state(
        page,
        prefix="DeleteStatusCheckbox",
    )

    page.open_statuses()
    page.select_checkbox_by_name(target_name)
    page.click_delete_button()

    page.open_statuses()
    page.wait_for_status_absent(target_name)

    count_after_delete = page.get_statuses_count()

    assert not page.is_status_present(target_name)
    assert count_after_delete == count_before_delete - 1

    print(
        f"\nУспех! Статус {target_name} удален через чекбокс. "
        f"Было: {count_before_delete}, стало: {count_after_delete}"
    )


@pytest.mark.step_5_deleteOne
def test_delete_status_via_edit(auth_driver):
    page = StatusesPage(auth_driver)

    (
        target_name, _target_slug, _, count_before_delete
    ) = create_status_and_get_state(
        page,
        prefix="DeleteStatusEdit",
    )

    page.open_statuses()
    page.open_status_by_name(target_name)
    page.click_delete_button()

    page.open_statuses()
    page.wait_for_status_absent(target_name)

    count_after_delete = page.get_statuses_count()

    assert not page.is_status_present(target_name)
    assert count_after_delete == count_before_delete - 1

    print(
        f"\nУспех! Статус {target_name} удален через редактирование. "
        f"Было: {count_before_delete}, стало: {count_after_delete}"
    )


@pytest.mark.step_5_deleteAll
def test_delete_all_statuses(auth_driver):
    page = StatusesPage(auth_driver)
    page.open_statuses()

    initial_count = page.get_statuses_count()
    assert initial_count > 0, "Список пуст"

    page.select_all_checkbox()
    page.click_delete_button()

    assert page.get_statuses_count() == 0
    assert page.is_empty_message_visible()

    print(
        f"\nУспех! Список статусов полностью очищен. "
        f"Было: {initial_count}, стало: {page.get_statuses_count()}"
    )