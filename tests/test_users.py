import time

import pytest
from selenium.webdriver.common.by import By

from pages.users_page import UsersPage


def build_unique_user_payload(prefix="User"):
    unique_value = time.time_ns()
    email = f"{prefix.lower()}_{unique_value}@gmail.com"
    first = f"{prefix}First_{unique_value}"
    last = f"{prefix}Last_{unique_value}"
    return email, first, last


def create_user_and_get_state(page, prefix="User"):
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
    page = UsersPage(auth_driver)
    page.open_users()

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
        _old_first,
        _old_last,
        _count_before_create,
        count_before_edit,
    ) = create_user_and_get_state(
        page,
        prefix="EditUserOld",
    )

    page.open_users()
    page.open_user_by_email(old_email)

    page.force_clear_input("email")
    page.force_clear_input("firstName")
    page.force_clear_input("lastName")
    assert page.get_input_value("email") == "", "Поле email не очистилось"
    assert page.get_input_value("firstName") == "", (
        "Поле firstName не очистилось"
    )
    assert page.get_input_value("lastName") == "", (
        "Поле lastName не очистилось"
    )

    page.click_save()
    assert "required" in page.get_error_message().lower()

    page.fill_user_form(
        email="invalid_email",
        first="ValidFirst",
        last="ValidLast",
    )
    page.click_save()
    assert "incorrect" in page.get_error_message().lower()

    new_email, new_first, new_last = build_unique_user_payload(
        "EditUserNew"
    )

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

    count_after_edit = page.get_users_count()
    assert count_after_edit == count_before_edit, (
        "После редактирования количество users не должно меняться"
    )
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

    created_emails = []
    for prefix in ("DeleteAllUserA", "DeleteAllUserB"):
        created_email, *_ = create_user_and_get_state(
            page,
            prefix=prefix,
        )
        created_emails.append(created_email)

    page.open_users()
    initial_emails = page.get_all_user_emails()
    initial_count = len(initial_emails)

    assert initial_count > 0, "Список пуст"
    for created_email in created_emails:
        assert created_email in initial_emails, (
            f"Контрольный пользователь '{created_email}' "
            "не найден перед delete all"
        )

    page.select_all_checkbox()
    page.click_delete_button()

    page.open_users()
    page.wait_for_empty_state()

    assert page.is_empty_message_visible(), (
        "После delete all не появился empty state"
    )
    assert page.get_users_count() == 0, (
        "После delete all на странице остались строки users"
    )

    for created_email in created_emails:
        assert not page.is_user_present(created_email), (
            f"Контрольный пользователь '{created_email}' "
            "остался после delete all"
        )

    print(
        f"\nУспех! Все пользователи удалены. "
        f"Было: {initial_count}, стало: {page.get_users_count()}"
    )
