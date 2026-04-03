import time

import pytest
from selenium.webdriver.common.by import By

from pages.statuses_page import StatusesPage


def build_unique_status_payload(prefix="Status"):
    unique_value = time.time_ns()
    name = f"{prefix}_{unique_value}"
    slug = f"slug_{unique_value}"
    return name, slug


def create_status_and_get_state(page, prefix="Status"):
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
    assert page.is_status_present(new_name)

    return new_name, new_slug, count_before_create, count_after_create


@pytest.mark.step_5_viewList
def test_view_statuses_list(auth_driver):
    page = StatusesPage(auth_driver)
    page.open_statuses()

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

    new_name, new_slug, count_before, count_after = (
        create_status_and_get_state(
            page,
            prefix="CreateStatus",
        )
    )

    row_values = page.get_status_row_values(new_name)
    assert row_values["name"] == new_name
    assert row_values["slug"] == new_slug

    print(
        f"\nУспех! Статус {new_name} появился в списке. "
        f"Было: {count_before}, стало: {count_after}"
    )


@pytest.mark.step_5_editStatus
def test_edit_status(auth_driver):
    page = StatusesPage(auth_driver)

    old_name, old_slug, _, count_before_edit = create_status_and_get_state(
        page,
        prefix="EditStatusOld",
    )

    page.open_statuses()
    page.open_status_by_name(old_name)

    page.force_clear_input("name")
    page.force_clear_input("slug")
    assert page.get_input_value("name") == "", "Поле name не очистилось"
    assert page.get_input_value("slug") == "", "Поле slug не очистилось"

    page.click_save()
    assert "required" in page.get_error_message().lower()

    new_name, new_slug = build_unique_status_payload("EditStatusNew")
    page.fill_status_form(name=new_name, slug=new_slug)
    page.click_save()

    page.open_statuses()
    page.wait_for_status_present(new_name)

    count_after_edit = page.get_statuses_count()
    assert count_after_edit == count_before_edit, (
        "После редактирования количество statuses не должно меняться"
    )
    assert page.is_status_present(new_name)
    assert not page.is_status_present(old_name)

    row_values = page.get_status_row_values(new_name)
    assert row_values["name"] == new_name
    assert row_values["slug"] == new_slug
    assert row_values["name"] != old_name
    assert row_values["slug"] != old_slug

    print("\nУспех! Редактирование и валидация проверены.")


@pytest.mark.step_5_deleteOne
def test_delete_status_via_checkbox(auth_driver):
    page = StatusesPage(auth_driver)

    target_name, _target_slug, _, count_before_delete = (
        create_status_and_get_state(
            page,
            prefix="DeleteStatusCheckbox",
        )
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

    target_name, _target_slug, _, count_before_delete = (
        create_status_and_get_state(
            page,
            prefix="DeleteStatusEdit",
        )
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

    created_names = []
    for prefix in ("DeleteAllStatusA", "DeleteAllStatusB"):
        created_name, _, _, _ = create_status_and_get_state(
            page,
            prefix=prefix,
        )
        created_names.append(created_name)

    page.open_statuses()
    initial_names = page.get_all_status_names()
    initial_count = len(initial_names)

    assert initial_count > 0, "Список пуст"
    for created_name in created_names:
        assert created_name in initial_names, (
            f"Контрольный статус '{created_name}' "
            "не найден перед delete all"
        )

    page.select_all_checkbox()
    page.click_delete_button()

    page.open_statuses()
    page.wait_for_empty_state()

    assert page.is_empty_message_visible(), (
        "После delete all не появился empty state"
    )
    assert page.get_statuses_count() == 0, (
        "После delete all на странице остались строки statuses"
    )

    for created_name in created_names:
        assert not page.is_status_present(created_name), (
            f"Контрольный статус '{created_name}' "
            "остался после delete all"
        )

    print(
        f"\nУспех! Список статусов полностью очищен. "
        f"Было: {initial_count}, стало: {page.get_statuses_count()}"
    )
