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


@pytest.fixture
def users_page(auth_driver):
    page = UsersPage(auth_driver)
    assert page.delete_all_users()
    return page


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


def pick_target_and_untouched_user(page, first_email, second_email):
    page.open_users()
    visible_emails = page.get_all_user_emails()

    assert first_email in visible_emails
    assert second_email in visible_emails

    if visible_emails[0] == first_email:
        return second_email, first_email

    if visible_emails[0] == second_email:
        return first_email, second_email

    return second_email, first_email


@pytest.mark.step_4_viewList
def test_view_users_list(users_page):
    email, first_name, last_name, _, _ = create_user_and_get_state(
        users_page,
        prefix="ViewUser",
    )

    header_text = users_page.driver.find_element(
        By.CSS_SELECTOR,
        "table thead",
    ).text

    assert "Email" in header_text
    assert "First name" in header_text
    assert "Last name" in header_text
    assert users_page.driver.find_element(
        By.TAG_NAME,
        "table",
    ).is_displayed()

    row_values = users_page.get_user_row_values(email)
    assert row_values["email"] == email
    assert row_values["first"] == first_name
    assert row_values["last"] == last_name


@pytest.mark.step_4_createUser
def test_create_new_user(users_page):
    (
        new_email,
        new_first,
        new_last,
        count_before,
        count_after,
    ) = create_user_and_get_state(
        users_page,
        prefix="CreateUser",
    )

    row_values = users_page.get_user_row_values(new_email)
    assert row_values["email"] == new_email
    assert row_values["first"] == new_first
    assert row_values["last"] == new_last
    assert count_after == count_before + 1


@pytest.mark.step_4_editUser
def test_edit_user_with_validation(users_page):
    (
        keep_email,
        keep_first,
        keep_last,
        _count_before_keep,
        _count_after_keep,
    ) = create_user_and_get_state(
        users_page,
        prefix="KeepUser",
    )
    (
        old_email,
        _old_first,
        _old_last,
        _count_before_target,
        count_before_edit,
    ) = create_user_and_get_state(
        users_page,
        prefix="EditUserOld",
    )

    target_email, untouched_email = pick_target_and_untouched_user(
        users_page,
        keep_email,
        old_email,
    )
    untouched_first = keep_first if untouched_email == keep_email else None
    untouched_last = keep_last if untouched_email == keep_email else None

    users_page.open_users()
    users_page.open_user_by_email(target_email)

    users_page.force_clear_input("email")
    users_page.force_clear_input("firstName")
    users_page.force_clear_input("lastName")

    assert users_page.get_input_value("email") == "", (
        "Поле email не очистилось"
    )
    assert users_page.get_input_value("firstName") == "", (
        "Поле firstName не очистилось"
    )
    assert users_page.get_input_value("lastName") == "", (
        "Поле lastName не очистилось"
    )

    users_page.click_save()
    assert "required" in users_page.get_error_message().lower()

    invalid_first = f"CheckFirst_{time.time_ns()}"
    invalid_last = f"CheckLast_{time.time_ns()}"
    users_page.fill_user_form(
        email="invalid_email",
        first=invalid_first,
        last=invalid_last,
    )
    users_page.click_save()
    assert "incorrect" in users_page.get_error_message().lower()

    new_email, new_first, new_last = build_unique_user_payload(
        "EditUserNew",
    )
    users_page.force_clear_input("email")
    users_page.force_clear_input("firstName")
    users_page.force_clear_input("lastName")
    users_page.fill_user_form(
        email=new_email,
        first=new_first,
        last=new_last,
    )
    users_page.click_save()

    users_page.open_users()
    users_page.wait_for_user_present(new_email)

    count_after_edit = users_page.get_users_count()
    assert count_after_edit == count_before_edit, (
        "После редактирования количество users "
        "не должно меняться"
    )
    assert users_page.is_user_present(new_email)
    assert not users_page.is_user_present(target_email)
    assert users_page.is_user_present(untouched_email)

    row_values = users_page.get_user_row_values(new_email)
    assert row_values["email"] == new_email
    assert row_values["first"] == new_first
    assert row_values["last"] == new_last

    untouched_row = users_page.get_user_row_values(untouched_email)
    assert untouched_row["email"] == untouched_email
    if untouched_first is not None:
        assert untouched_row["first"] == untouched_first
    if untouched_last is not None:
        assert untouched_row["last"] == untouched_last


@pytest.mark.step_4_deleteOne
def test_delete_user_via_checkbox(users_page):
    (
        keep_email,
        keep_first,
        keep_last,
        _count_before_keep,
        _count_after_keep,
    ) = create_user_and_get_state(
        users_page,
        prefix="KeepCheckboxUser",
    )
    (
        delete_email,
        _delete_first,
        _delete_last,
        _count_before_target,
        count_before_delete,
    ) = create_user_and_get_state(
        users_page,
        prefix="DeleteUserCheckbox",
    )

    target_email, untouched_email = pick_target_and_untouched_user(
        users_page,
        keep_email,
        delete_email,
    )

    users_page.open_users()
    users_page.select_checkbox_by_email(target_email)
    users_page.click_delete_button()

    users_page.open_users()
    users_page.wait_for_user_absent(target_email)

    count_after_delete = users_page.get_users_count()

    assert not users_page.is_user_present(target_email)
    assert users_page.is_user_present(untouched_email)
    if untouched_email == keep_email:
        untouched_row = users_page.get_user_row_values(untouched_email)
        assert untouched_row["first"] == keep_first
        assert untouched_row["last"] == keep_last
    assert count_after_delete == count_before_delete - 1


@pytest.mark.step_4_deleteOne
def test_delete_user_via_edit(users_page):
    (
        keep_email,
        keep_first,
        keep_last,
        _count_before_keep,
        _count_after_keep,
    ) = create_user_and_get_state(
        users_page,
        prefix="KeepEditUser",
    )
    (
        delete_email,
        _delete_first,
        _delete_last,
        _count_before_target,
        count_before_delete,
    ) = create_user_and_get_state(
        users_page,
        prefix="DeleteUserEdit",
    )

    target_email, untouched_email = pick_target_and_untouched_user(
        users_page,
        keep_email,
        delete_email,
    )

    users_page.open_users()
    users_page.open_user_by_email(target_email)
    users_page.click_delete_button()

    users_page.open_users()
    users_page.wait_for_user_absent(target_email)

    count_after_delete = users_page.get_users_count()

    assert not users_page.is_user_present(target_email)
    assert users_page.is_user_present(untouched_email)
    if untouched_email == keep_email:
        untouched_row = users_page.get_user_row_values(untouched_email)
        assert untouched_row["first"] == keep_first
        assert untouched_row["last"] == keep_last
    assert count_after_delete == count_before_delete - 1


@pytest.mark.step_4_deleteAll
def test_delete_all_users(users_page):
    created_users = []
    for prefix in (
        "DeleteAllUserA",
        "DeleteAllUserB",
        "DeleteAllUserC",
    ):
        email, first, last, _, _ = create_user_and_get_state(
            users_page,
            prefix=prefix,
        )
        created_users.append((email, first, last))

    users_page.open_users()
    initial_count = users_page.get_users_count()
    assert initial_count == len(created_users)

    users_page.select_all_checkbox()
    users_page.click_delete_button()

    users_page.open_users()
    users_page.wait_for_empty_state()

    assert users_page.get_users_count() == 0
    assert users_page.is_empty_message_visible()

    for email, _first, _last in created_users:
        assert not users_page.is_user_present(email)
