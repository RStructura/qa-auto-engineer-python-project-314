import uuid

import pytest

from pages.users_page import UsersPage


@pytest.fixture
def users_page(auth_driver):
    page = UsersPage(auth_driver)
    assert page.delete_all_users()
    return page


@pytest.fixture
def seeded_user(users_page):
    email = f"user-{uuid.uuid4().hex[:6]}@example.com"
    first = f"Name_{uuid.uuid4().hex[:4]}"
    last = f"Surname_{uuid.uuid4().hex[:4]}"
    assert users_page.create_user(email, first, last)
    return users_page, email, first, last


@pytest.mark.step_4_viewList
def test_view_users_list(seeded_user):
    users_page, email, first, last = seeded_user
    users_page.open_users()
    assert users_page.get_table() is not None

    row_values = users_page.get_user_row_values(email)
    assert row_values["email"] == email
    assert row_values["first"] == first
    assert row_values["last"] == last


@pytest.mark.step_4_createUser
def test_create_new_user(users_page):
    email = f"test-{uuid.uuid4().hex[:6]}@example.com"
    first = f"John_{uuid.uuid4().hex[:4]}"
    last = f"Doe_{uuid.uuid4().hex[:4]}"

    assert users_page.create_user(email, first, last)

    row_values = users_page.get_user_row_values(email)
    assert row_values["email"] == email
    assert row_values["first"] == first
    assert row_values["last"] == last


@pytest.mark.step_4_editUser
def test_edit_user_with_validation(seeded_user):
    users_page, email, _first, _last = seeded_user
    users_page.open_users()
    users_page.open_user_by_email(email)

    users_page.force_clear_input("email")
    users_page.force_clear_input("firstName")
    users_page.force_clear_input("lastName")

    users_page.click_save()
    assert "required" in users_page.get_error_message().lower()

    users_page.fill_user_form(
        email="invalid_email",
        first="ValidFirst",
        last="ValidLast",
    )
    users_page.click_save()
    assert "incorrect" in users_page.get_error_message().lower()

    new_email = f"updated-{uuid.uuid4().hex[:6]}@example.com"
    new_first = f"Updated_{uuid.uuid4().hex[:4]}"
    new_last = f"Last_{uuid.uuid4().hex[:4]}"

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

    row_values = users_page.get_user_row_values(new_email)
    assert row_values["email"] == new_email
    assert row_values["first"] == new_first
    assert row_values["last"] == new_last
    assert not users_page.is_user_present(email)


@pytest.mark.step_4_deleteOne
def test_delete_user_via_checkbox(users_page):
    keep_email = f"keep-{uuid.uuid4().hex[:6]}@example.com"
    target_email = f"delete-{uuid.uuid4().hex[:6]}@example.com"
    keep_first = f"Keep_{uuid.uuid4().hex[:4]}"
    keep_last = f"Stay_{uuid.uuid4().hex[:4]}"

    assert users_page.create_user(keep_email, keep_first, keep_last)
    assert users_page.create_user(target_email, "Delete", "Me")

    users_page.open_users()
    users_page.select_checkbox_by_email(target_email)
    users_page.click_delete_button()

    users_page.open_users()
    users_page.wait_for_user_absent(target_email)

    assert not users_page.is_user_present(target_email)
    assert users_page.is_user_present(keep_email)

    row_values = users_page.get_user_row_values(keep_email)
    assert row_values["first"] == keep_first
    assert row_values["last"] == keep_last


@pytest.mark.step_4_deleteOne
def test_delete_user_via_edit(seeded_user):
    users_page, email, _first, _last = seeded_user
    assert users_page.delete_user(email)
    assert not users_page.is_user_present(email)


@pytest.mark.step_4_deleteAll
def test_delete_all_users(seeded_user):
    users_page, email, _first, _last = seeded_user
    extra_email = f"extra-{uuid.uuid4().hex[:6]}@example.com"
    assert users_page.create_user(extra_email, "Extra", "User")

    assert users_page.delete_all_users()
    assert users_page.is_empty_message_visible()
    assert not users_page.is_user_present(email)
    assert not users_page.is_user_present(extra_email)
