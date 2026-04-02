import time

import pytest
from selenium.webdriver.common.by import By

from pages.labels_page import LabelsPage


def build_unique_label_name(prefix="Label"):
    """Генерация уникального niput"""
    return f"{prefix}_{time.time_ns()}"


def create_label_and_get_state(page, prefix="Label"):
    """
    Создание label и проверка:
    new_name, count_before_create, count_after_create
    """
    page.open_labels()
    count_before_create = page.get_labels_count()

    new_name = build_unique_label_name(prefix)

    page.click_create()
    page.fill_label_form(name=new_name)
    page.click_save()

    page.open_labels()
    page.wait_for_label_present(new_name)

    count_after_create = page.get_labels_count()

    assert count_after_create == count_before_create + 1, (
        f"Ожидали {count_before_create + 1} labels, "
        f"но нашли {count_after_create}"
    )
    assert page.is_label_present(new_name)

    return new_name, count_before_create, count_after_create


@pytest.mark.step_6_viewList
def test_view_labels_list(auth_driver):
    # Проверка открытия списка и загрузки страницы
    page = LabelsPage(auth_driver)
    page.open_labels()

    # Проверка наличия элементов и списка
    header_text = auth_driver.find_element(
        By.CSS_SELECTOR,
        "table thead",
    ).text
    assert "Name" in header_text
    assert page.get_labels_count() > 0, "Список labels пуст"

    first_name = auth_driver.find_element(
        By.CSS_SELECTOR,
        "tbody tr:first-child td.column-name",
    ).text.strip()
    assert first_name, "Name в первой строке пустой"

    print("\nУспех! Список и колонки отображаются.")


@pytest.mark.step_6_createLabel
def test_create_label(auth_driver):
    page = LabelsPage(auth_driver)

    new_name, count_before, count_after = create_label_and_get_state(
        page,
        prefix="CreateLabel",
    )

    row_values = page.get_label_row_values(new_name)
    assert row_values["name"] == new_name

    print(
        f"\nУспех! Лейбл {new_name} появился в списке. "
        f"Было: {count_before}, стало: {count_after}"
    )


@pytest.mark.step_6_editLabel
def test_edit_label(auth_driver):
    page = LabelsPage(auth_driver)

    old_name, _, _ = create_label_and_get_state(
        page,
        prefix="EditLabelOld",
    )

    page.open_labels()
    page.open_label_by_name(old_name)

    # Проверка валидации пустого поля
    page.force_clear_input("name")
    page.click_save()
    assert "required" in page.get_error_message().lower()

    # Обновление значения
    new_name = build_unique_label_name("EditLabelNew")
    page.fill_label_form(name=new_name)
    page.click_save()

    page.open_labels()
    page.wait_for_label_present(new_name)

    # Проверка обновления на новые значения
    assert page.is_label_present(new_name)

    # Проверка исчезновения старых значений
    assert not page.is_label_present(old_name)

    row_values = page.get_label_row_values(new_name)
    assert row_values["name"] == new_name

    print("\nУспех! Редактирование и валидация проверены.")


@pytest.mark.step_6_deleteOne
def test_delete_label_via_checkbox(auth_driver):
    page = LabelsPage(auth_driver)

    target_name, _, count_before_delete = create_label_and_get_state(
        page,
        prefix="DeleteLabelCheckbox",
    )

    page.open_labels()
    page.select_checkbox_by_name(target_name)
    page.click_delete_button()

    page.open_labels()
    page.wait_for_label_absent(target_name)

    count_after_delete = page.get_labels_count()

    assert not page.is_label_present(target_name)
    assert count_after_delete == count_before_delete - 1

    print(
        f"\nУспех! Лейбл {target_name} удален через чекбокс. "
        f"Было: {count_before_delete}, стало: {count_after_delete}"
    )


@pytest.mark.step_6_deleteOne
def test_delete_label_via_edit(auth_driver):
    page = LabelsPage(auth_driver)

    target_name, _, count_before_delete = create_label_and_get_state(
        page,
        prefix="DeleteLabelEdit",
    )

    page.open_labels()
    page.open_label_by_name(target_name)
    page.click_delete_button()

    page.open_labels()
    page.wait_for_label_absent(target_name)

    count_after_delete = page.get_labels_count()

    assert not page.is_label_present(target_name)
    assert count_after_delete == count_before_delete - 1

    print(
        f"\nУспех! Лейбл {target_name} удален через редактирование. "
        f"Было: {count_before_delete}, стало: {count_after_delete}"
    )


@pytest.mark.step_6_deleteAll
def test_delete_all_labels(auth_driver):
    page = LabelsPage(auth_driver)
    page.open_labels()

    # Фиксиция списка labels до удаления
    initial_names = page.get_all_label_names()
    initial_count = len(initial_names)

    assert initial_count > 0, "Список пуст"

    page.select_all_checkbox()
    page.click_delete_button()

    # Ожидание empty state на странице после удаления
    page.wait_for_empty_state()

    assert page.get_labels_count() == 0
    assert page.is_empty_message_visible()

    # Проверка удаления зафиксированных labels
    for name in initial_names:
        assert not page.is_label_present(name), (
            f"Лейбл '{name}' остался после delete all"
        )

    print(
        f"\nУспех! Список лейблов полностью очищен. "
        f"Было: {initial_count}, стало: {page.get_labels_count()}"
    )