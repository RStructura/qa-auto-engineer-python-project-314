import uuid

import pytest

from .constants import USER
from .pages.login import LoginPage
from .pages.users import UsersPage


@pytest.fixture()
def users_page(driver, base_url):
    login_page = LoginPage(driver, base_url)
    login_page.login(USER["login"], USER["password"])
    page = UsersPage(driver, base_url)
    assert page.delete_all_users()
    return page


@pytest.fixture()
def seeded_user(users_page):
    email = f"user-{uuid.uuid4().hex[:6]}@example.com"
    assert users_page.create_user(email, "Name", "Surname")
    return users_page, email


@pytest.mark.step_4_createUser
def test_create_user(users_page):
    email = f"test-{uuid.uuid4().hex[:6]}@example.com"
    assert users_page.create_user(email, "John", "Doe")


@pytest.mark.step_4_viewList
def test_view_user_list(seeded_user):
    users_page, email = seeded_user
    users_page.open_page()
    users_page.wait_for_text("Email")
    users_page.wait_for_text(email)


@pytest.mark.step_4_editUser
def test_edit_user(seeded_user):
    users_page, email = seeded_user
    updated_name = f"Updated_{uuid.uuid4().hex[:5]}"
    assert users_page.edit_user(email, updated_name)


@pytest.mark.step_4_deleteOne
def test_delete_user(seeded_user):
    users_page, email = seeded_user
    assert users_page.delete_user(email)


@pytest.mark.step_4_deleteAll
def test_delete_all_users(seeded_user):
    users_page, _email = seeded_user
    assert users_page.delete_all_users()
