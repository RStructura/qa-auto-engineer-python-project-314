import time

import pytest
from selenium.webdriver.common.by import By

from pages.users_page import UsersPage


def build_unique_user_payload(prefix="User"):
    """Генерация уникальных email / first / last"""
    unique_value = time.time_ns()
    email = f"{prefix.lower()}_{unique_value}@gmail.com"
    first = f"{prefix}First_{unique_value}"
    last = f"{prefix}Last_{unique_value}"
    return email, first, last


def create_user_and_get_state(page, prefix="User"):
    """
    Создание пользователя и возврат:
    new_email, new_first, new_last, count_before_create, count_after_create
    """
    page.open_users()
    count_before_create = page.get_users_count()

    new_email, new_first, new_last = build_unique_user_payload(prefix)

    page.click_create()
    page.fill_user_form(
        email=new_email,
        first=new_first,
        last=new_last,
    )
    page.click_save()

    page.open_users()
    page.wait_for_user_present(new_email)

    count_after_create = page.get_users_count()

    assert count_after_create == count_before_create + 1, (
        f"Ожидали {count_before_create + 1} users, "
        f"но нашли {count_after_create}"
    )
    assert page.is_user_present(new_email)

    return (
        new_email,
        new_first,
        new_last,
        count_before_create,
        count_after_create,
    )


@pytest.mark.step_4_viewList
def test_view_users_list(auth_driver):
    # Проверка открытия списка и загрузки страницы
    page = UsersPage(auth_driver)
    page.open_users()

    # Проверка наличия элементов и списка
    header_text = auth_driver.find_element(
        By.CSS_SELECTOR,
        "table thead",
    ).text

    assert "Email" in header_text
    assert "First name" in header_text
    assert "Last name" in header_text
    assert page.get_users_count() > 0, "Список users пуст"

    email = auth_driver.find_element(
        By.CSS_SELECTOR,
        "tbody tr:first-child td.column-email",
    ).text.strip()
    first_name = auth_driver.find_element(
        By.CSS_SELECTOR,
        "tbody tr:first-child td.column-firstName",
    ).text.strip()
    last_name = auth_driver.find_element(
        By.CSS_SELECTOR,
        "tbody tr:first-child td.column-lastName",
    ).text.strip()

    assert "@" in email, "Email в первой строке не отображается"
    assert first_name, "First name в первой строке пустой"
    assert last_name, "Last name в первой строке пустой"

    print("\nУспех! Список и колонки отображаются.")


@pytest.mark.step_4_createUser
def test_create_new_user(auth_driver):
    page = UsersPage(auth_driver)

    (
        new_email,
        new_first,
        new_last,
        count_before,
        count_after,
    ) = create_user_and_get_state(
        page,
        prefix="CreateUser",
    )

    row_values = page.get_user_row_values(new_email)
    assert row_values["email"] == new_email
    assert row_values["first"] == new_first
    assert row_values["last"] == new_last

    print(
        f"\nУспех! Пользователь {new_email} создан. "
        f"Было: {count_before}, стало: {count_after}"
    )


@pytest.mark.step_4_editUser
def test_edit_user_with_validation(auth_driver):
    page = UsersPage(auth_driver)

    (
        old_email,
        old_first,
        old_last,
        _count_before_create,
        _count_after_create,
    ) = create_user_and_get_state(
        page,
        prefix="EditUserOld",
    )

    page.open_users()
    page.open_user_by_email(old_email)

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

    # Обновление значений
    new_email, new_first, new_last = build_unique_user_payload("EditUserNew")

    page.force_clear_input("email")
    page.force_clear_input("firstName")
    page.force_clear_input("lastName")
    page.fill_user_form(
        email=new_email,
        first=new_first,
        last=new_last,
    )
    page.click_save()

    page.open_users()
    page.wait_for_user_present(new_email)

    # Проверяем появление нового и исчезновение старого
    assert page.is_user_present(new_email)
    assert not page.is_user_present(old_email)

    row_values = page.get_user_row_values(new_email)
    assert row_values["email"] == new_email
    assert row_values["first"] == new_first
    assert row_values["last"] == new_last

    print("\nУспех! Редактирование и валидация проверены.")


@pytest.mark.step_4_deleteOne
def test_delete_user_via_checkbox(auth_driver):
    page = UsersPage(auth_driver)

    (
        target_email,
        _target_first,
        _target_last,
        _count_before_create,
        count_before_delete,
    ) = create_user_and_get_state(
        page,
        prefix="DeleteUserCheckbox",
    )

    page.open_users()
    page.select_checkbox_by_email(target_email)
    page.click_delete_button()

    page.open_users()
    page.wait_for_user_absent(target_email)

    count_after_delete = page.get_users_count()

    assert not page.is_user_present(target_email)
    assert count_after_delete == count_before_delete - 1

    print(
        f"\nУспех! Пользователь {target_email} удален через чекбокс. "
        f"Было: {count_before_delete}, стало: {count_after_delete}"
    )


@pytest.mark.step_4_deleteOne
def test_delete_user_via_edit(auth_driver):
    page = UsersPage(auth_driver)

    (
        target_email,
        _target_first,
        _target_last,
        _count_before_create,
        count_before_delete,
    ) = create_user_and_get_state(
        page,
        prefix="DeleteUserEdit",
    )

    page.open_users()
    page.open_user_by_email(target_email)
    page.click_delete_button()

    page.open_users()
    page.wait_for_user_absent(target_email)

    count_after_delete = page.get_users_count()

    assert not page.is_user_present(target_email)
    assert count_after_delete == count_before_delete - 1

    print(
        f"\nУспех! Пользователь {target_email} удален через редактирование. "
        f"Было: {count_before_delete}, стало: {count_after_delete}"
    )


@pytest.mark.step_4_deleteAll
def test_delete_all_users(auth_driver):
    page = UsersPage(auth_driver)
    page.open_users()

    initial_count = page.get_users_count()
    assert initial_count > 0, "Список пуст"

    page.select_all_checkbox()
    page.click_delete_button()

    page.open_users()

    assert page.get_users_count() == 0
    assert page.is_empty_message_visible()

    print(
        f"\nУспех! Все пользователи удалены. "
        f"Было: {initial_count}, стало: {page.get_users_count()}"
    )