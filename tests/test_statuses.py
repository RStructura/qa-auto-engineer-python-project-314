import time

import pytest

from pages.statuses_page import StatusesPage
from selenium.webdriver.common.by import By


@pytest.mark.step_5_viewList
def test_view_statuses_list(auth_driver):
    # Проверка открытия списка и загрузки страницы
    page = StatusesPage(auth_driver)
    page.open_statuses()
    # Проверка наличия элементов и списка
    header_text = auth_driver.find_element(
        By.CSS_SELECTOR, 'table thead').text
    assert "Name" in header_text
    assert "Slug" in header_text
    assert page.get_statuses_count() >= 0
    print("\nУспех! Список и колонки отображаются.")


@pytest.mark.step_5_createStatus
def test_create_status(auth_driver):
    page = StatusesPage(auth_driver)
    page.open_statuses()
    # Создание переменной для проверки изм. списка
    initial_count = page.get_statuses_count()
    # Создание переменных для генерации данных
    test_name = f"Status_{int(time.time())}"
    test_slug = f"slug_{int(time.time())}"
    # Создание статуса
    page.click_create()
    page.fill_status_form(name=test_name, slug=test_slug)
    page.click_save()
    # Пауза для видимой проверки
    time.sleep(1)
    # Обновление страницы на всякий случай
    page.open_statuses()
    # Провека изменений
    assert test_name in auth_driver.page_source
    assert page.get_statuses_count() == initial_count + 1
    print(
        f"\nУспех! Статус {test_name} появился в списке."
        f" Было: {initial_count}, стало: {page.get_statuses_count()}"
    )


@pytest.mark.step_5_editStatus
def test_edit_status(auth_driver):
    page = StatusesPage(auth_driver)
    page.open_statuses()
    page.open_first_status()
    # Проверка валидации пустых полей
    page.force_clear_input("name")
    page.force_clear_input("slug")
    page.click_save()
    assert "required" in page.get_error_message().lower()
    # Обновление значений и сохранение
    new_name = "Status_updated"
    page.fill_status_form(name=new_name, slug="slug_update")
    page.click_save()
    # Проверка изменений
    time.sleep(1)
    page.open_statuses()
    assert new_name in auth_driver.page_source
    print("\nУспех! Редактирование и валидация проверены.")


@pytest.mark.step_5_deleteOne
def test_delete_status_via_checkbox(auth_driver):
    page = StatusesPage(auth_driver)
    page.open_statuses()

    if page.get_statuses_count() == 0:
        pytest.skip("Список пуст")

    initial_count = page.get_statuses_count()
    name_to_del = page.get_first_status_name()

    page.select_first_checkbox()
    page.click_delete_button()

    time.sleep(1)
    page.open_statuses()

    assert name_to_del not in auth_driver.page_source
    assert page.get_statuses_count() == initial_count - 1
    print(
        f"\nУспех! Статус {name_to_del} удален через чекбокс."
        f"Было: {initial_count}, стало: {page.get_statuses_count()}"
    )


@pytest.mark.step_5_deleteOne
def test_delete_status_via_edit(auth_driver):
    page = StatusesPage(auth_driver)
    page.open_statuses()

    if page.get_statuses_count() == 0:
        pytest.skip("Список пуст")

    initial_count = page.get_statuses_count()
    name_to_del = page.get_first_status_name()

    page.open_first_status()
    page.click_delete_button()

    time.sleep(1)
    page.open_statuses()

    assert name_to_del not in auth_driver.page_source
    assert page.get_statuses_count() == initial_count - 1
    print(
        f"\nУспех! Статус {name_to_del} удален через редактирование."
        f"Было: {initial_count}, стало: {page.get_statuses_count()}"
    )


@pytest.mark.step_5_deleteAll
def test_delete_all_statuses(auth_driver):
    page = StatusesPage(auth_driver)
    page.open_statuses()

    initial_count = page.get_statuses_count()
    if initial_count == 0:
        pytest.skip("Список уже пуст")

    page.select_all_checkbox()
    page.click_delete_button()

    time.sleep(1)
    page.open_statuses()

    assert page.get_statuses_count() == 0
    assert page.is_empty_message_visible()
    print("\nУспех! Список статусов полностью очищен.")
