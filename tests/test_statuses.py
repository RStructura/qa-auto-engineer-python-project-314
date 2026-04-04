import uuid

import pytest

from pages.statuses_page import StatusesPage


@pytest.fixture
def statuses_page(auth_driver):
    page = StatusesPage(auth_driver)
    assert page.delete_all_statuses()
    return page


@pytest.fixture
def seeded_status(statuses_page):
    name = f"Status_{uuid.uuid4().hex[:5]}"
    slug = f"slug-{uuid.uuid4().hex[:5]}"
    assert statuses_page.create_status(name, slug)
    return statuses_page, name, slug


@pytest.mark.step_5_createStatus
def test_create_status(statuses_page):
    name = f"Backlog_{uuid.uuid4().hex[:5]}"
    slug = f"backlog-{uuid.uuid4().hex[:5]}"
    assert statuses_page.create_status(name, slug)


@pytest.mark.step_5_viewList
def test_view_statuses_list(seeded_status):
    statuses_page, name, slug = seeded_status
    statuses_page.open_statuses()
    assert statuses_page.get_table() is not None
    assert statuses_page.is_status_present(name)
    row_values = statuses_page.get_status_row_values(name)
    assert row_values["name"] == name
    assert row_values["slug"] == slug


@pytest.mark.step_5_editStatus
def test_edit_status(seeded_status):
    statuses_page, name, _slug = seeded_status
    new_name = f"{name}_Updated"
    new_slug = f"updated-{uuid.uuid4().hex[:5]}"
    assert statuses_page.edit_status(name, new_name, new_slug)


@pytest.mark.step_5_deleteOne
def test_delete_status_via_edit(seeded_status):
    statuses_page, name, _slug = seeded_status
    assert statuses_page.delete_status(name)


@pytest.mark.step_5_deleteAll
def test_delete_all_statuses(seeded_status):
    statuses_page, _name, _slug = seeded_status
    assert statuses_page.delete_all_statuses()
