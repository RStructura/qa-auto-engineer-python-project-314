import time

import pytest
from selenium.webdriver.common.by import By

from pages.users_page import UsersPage


@pytest.mark.step_4_viewList
def test_view_users_list(auth_driver):
    # Проверка открытия списка и загрузки страницы
    page = UsersPage(auth_driver)
    page.open_users()
    # Проверка наличия в элементов и списка
    header_text = auth_driver.find_element(
        By.CSS_SELECTOR, 'table thead').text
    assert "Email" in header_text
    assert "First name" in header_text
    assert "Last name" in header_text
    assert page.get_users_count() >= 0
    print("\nУспех! Список и колонки отображаются.")


@pytest.mark.step_4_createUser
def test_create_new_user(auth_driver):
    page = UsersPage(auth_driver)
    page.open_users()
    # Создание переменной для проверки изм. списка
    initial_count = page.get_users_count()
    # Создание переменных для генерации данных
    test_email = f"email_{int(time.time())}@gmail.com"
    test_first = f"FirstName_{int(time.time())}"
    test_last = f"LastName_{int(time.time())}"
    # Создание пользователя
    page.click_create()
    page.fill_user_form(email=test_email, first=test_first, last=test_last)
    page.click_save()
    # Пауза для видимой проверки
    time.sleep(1)
    # Обновление страницы на всякий случай
    page.open_users()
    # Провека изменений
    assert test_email in auth_driver.page_source
    assert page.get_users_count() == initial_count + 1
    print(
        f"\nУспех! Пользователь {test_email} создан."
        f" Было: {initial_count}, стало: {page.get_users_count()}"
    )


@pytest.mark.step_4_editUser
def test_edit_user_with_validation(auth_driver):
    page = UsersPage(auth_driver)
    page.open_users()
    page.open_first_user()
    # Проверка валидации пустых полей
    page.force_clear_input("email")
    page.force_clear_input("firstName")
    page.force_clear_input("lastName")
    page.click_save()
    assert "required" in page.get_error_message().lower()
    # Проверка валидации некорректного email
    page.fill_user_form(email="invalid_email")
    page.click_save()
    assert "incorrect" in page.get_error_message().lower()
    # Обновление значений и сохранение
    new_first = "Name_updated"
    page.force_clear_input("email")
    page.fill_user_form(
        email="correct@gmail.com", first=new_first, last="Lastname_update"
    )
    page.click_save()
    # Проверка изменений
    time.sleep(1)
    page.open_users()
    assert new_first in auth_driver.page_source
    print("\nУспех! Редактирование и валидация проверены.")


@pytest.mark.step_4_deleteOne
def test_delete_user_via_checkbox(auth_driver):
    page = UsersPage(auth_driver)
    page.open_users()

    if page.get_users_count() == 0:
        pytest.skip("Список пуст")

    initial_count = page.get_users_count()
    email_to_delete = page.get_first_user_email()

    page.select_first_checkbox()
    page.click_delete_button()

    time.sleep(1)
    page.open_users()

    assert email_to_delete not in auth_driver.page_source
    assert page.get_users_count() == initial_count - 1
    print(
        f"\nУспех! Удален через чекбокс: {email_to_delete}. "
        f"Было: {initial_count}, стало: {page.get_users_count()}"
    )


@pytest.mark.step_4_deleteOne
def test_delete_user_via_edit(auth_driver):
    page = UsersPage(auth_driver)
    page.open_users()

    if page.get_users_count() == 0:
        pytest.skip("Список пуст")

    initial_count = page.get_users_count()
    email_to_delete = page.get_first_user_email()

    page.open_first_user()
    page.click_delete_button()

    time.sleep(1)
    page.open_users()

    assert email_to_delete not in auth_driver.page_source
    assert page.get_users_count() == initial_count - 1
    print(
        f"\nУспех! Удален через редактирование: {email_to_delete}. "
        f"Было: {initial_count}, стало: {page.get_users_count()}"
    )


@pytest.mark.step_4_deleteAll
def test_delete_all_users(auth_driver):
    page = UsersPage(auth_driver)
    page.open_users()

    initial_count = page.get_users_count()
    if initial_count == 0:
        pytest.skip("Список уже пуст")

    page.select_all_checkbox()
    page.click_delete_button()

    time.sleep(1)
    page.open_users()

    assert page.get_users_count() == 0
    assert page.is_empty_message_visible()
    print("\nУспех! Все пользователи удалены.")
