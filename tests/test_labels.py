import time

import pytest
from selenium.webdriver.common.by import By

from pages.labels_page import LabelsPage


@pytest.mark.step_6_viewList
def test_view_labels_list(auth_driver):
    # Проверка открытия списка и загрузки страницы
    page = LabelsPage(auth_driver)
    page.open_labels()

    # Проверка наличия элементов и списка
    header_text = auth_driver.find_element(
        By.CSS_SELECTOR, 'table thead').text
    assert "Name" in header_text
    assert page.get_labels_count() > 0, "Список labels пуст"

    name = auth_driver.find_element(
        By.CSS_SELECTOR, "tbody tr:first-child td.column-name"
    ).text.strip()
    assert name, "Name в первой строке пустой"

    print("\nУспех! Список и колонки отображаются.")


@pytest.mark.step_6_createLabel
def test_create_label(auth_driver):
    page = LabelsPage(auth_driver)
    page.open_labels()

    # Создание переменной для проверки изм. списка
    initial_count = page.get_labels_count()

    # Создание переменных для генерации данных
    test_name = f"Label_{int(time.time())}"

    # Создание
    page.click_create()
    page.fill_label_form(name=test_name)
    page.click_save()

    # Пауза для видимой проверки
    time.sleep(1)

    # Обновление страницы на всякий случай
    page.open_labels()

    # Провека изменений
    assert test_name in auth_driver.page_source
    assert page.get_labels_count() == initial_count + 1

    print(
        f"\nУспех! Лейбл {test_name} появился в списке."
        f" Было: {initial_count}, стало: {page.get_labels_count()}"
    )


@pytest.mark.step_6_editLabel
def test_edit_label(auth_driver):
    page = LabelsPage(auth_driver)
    page.open_labels()
    page.open_first_label()

    # Проверка валидации пустых полей
    page.force_clear_input("name")
    page.click_save()
    assert "required" in page.get_error_message().lower()

    # Обновление значений и сохранение
    new_name = "Label_updated"
    page.fill_label_form(name=new_name)
    page.click_save()

    # Проверка изменений
    time.sleep(1)
    page.open_labels()
    assert new_name in auth_driver.page_source

    print("\nУспех! Редактирование и валидация проверены.")


@pytest.mark.step_6_deleteOne
def test_delete_label_via_checkbox(auth_driver):
    page = LabelsPage(auth_driver)
    page.open_labels()

    assert page.get_labels_count() > 0, "Список пуст"

    initial_count = page.get_labels_count()
    name_to_del = page.get_first_label_name()

    page.select_first_checkbox()
    page.click_delete_button()

    time.sleep(1)
    page.open_labels()

    assert not page.is_label_present(name_to_del)
    assert page.get_labels_count() == initial_count - 1

    print(
        f"\nУспех! Лейбл {name_to_del} удален через чекбокс."
        f"Было: {initial_count}, стало: {page.get_labels_count()}"
    )


@pytest.mark.step_6_deleteOne
def test_delete_label_via_edit(auth_driver):
    page = LabelsPage(auth_driver)
    page.open_labels()

    assert page.get_labels_count() > 0, "Список пуст"

    initial_count = page.get_labels_count()
    name_to_del = page.get_first_label_name()

    page.open_first_label()
    page.click_delete_button()

    time.sleep(1)
    page.open_labels()

    assert not page.is_label_present(name_to_del)
    assert page.get_labels_count() == initial_count - 1

    print(
        f"\nУспех! Лейбл {name_to_del} удален через редактирование."
        f"Было: {initial_count}, стало: {page.get_labels_count()}"
    )


@pytest.mark.step_6_deleteAll
def test_delete_all_labels(auth_driver):
    page = LabelsPage(auth_driver)
    page.open_labels()

    initial_count = page.get_labels_count()
    
    assert page.get_labels_count() > 0, "Список пуст"

    page.select_all_checkbox()
    page.click_delete_button()

    time.sleep(1)
    page.open_labels()

    assert page.get_labels_count() == 0
    assert page.is_empty_message_visible()

    print(
        f"\nУспех! Список лейблов полностью очищен."
        f"Было: {initial_count}, стало: {page.get_labels_count()}"
    )
