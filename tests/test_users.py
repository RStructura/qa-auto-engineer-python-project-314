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
    assert users_page.create_user(email, "Name", "Surname")
    return users_page, email


@pytest.mark.step_4_createUser
def test_create_new_user(users_page):
    email = f"test-{uuid.uuid4().hex[:6]}@example.com"
    assert users_page.create_user(email, "John", "Doe")


@pytest.mark.step_4_viewList
def test_view_users_list(seeded_user):
    users_page, email = seeded_user
    users_page.open_users()
    assert users_page.get_table() is not None
    assert users_page.is_user_present(email)


@pytest.mark.step_4_editUser
def test_edit_user_with_validation(seeded_user):
    users_page, email = seeded_user
    updated_first_name = f"Updated_{uuid.uuid4().hex[:5]}"
    assert users_page.edit_user(email, updated_first_name)


@pytest.mark.step_4_deleteOne
def test_delete_user_via_edit(seeded_user):
    users_page, email = seeded_user
    assert users_page.delete_user(email)


@pytest.mark.step_4_deleteAll
def test_delete_all_users(seeded_user):
    users_page, _email = seeded_user
    assert users_page.delete_all_users()
