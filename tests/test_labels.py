import uuid

import pytest

from .constants import USER
from .pages.labels import LabelsPage
from .pages.login import LoginPage


@pytest.fixture()
def labels_page(driver, base_url):
    login_page = LoginPage(driver, base_url)
    login_page.login(USER["login"], USER["password"])
    page = LabelsPage(driver, base_url)
    assert page.delete_all_labels()
    assert page.create_label("Label_Name")
    return page


@pytest.fixture()
def seeded_label(labels_page):
    name = f"Label_{uuid.uuid4().hex[:5]}"
    assert labels_page.create_label(name)
    return labels_page, name


@pytest.mark.step_6_createLabel
def test_create_label(labels_page):
    name = f"New_Label_{uuid.uuid4().hex[:5]}"
    assert labels_page.create_label(name)


@pytest.mark.step_6_viewList
def test_view_labels_list(labels_page):
    labels_page.open_page()
    labels_page.wait_until_label_present("Label_Name")
    assert labels_page.get_table() is not None


@pytest.mark.step_6_editLabel
def test_edit_label(seeded_label):
    labels_page, name = seeded_label
    new_name = f"{name}_Updated"
    assert labels_page.edit_label(name, new_name)


@pytest.mark.step_6_deleteOne
def test_delete_label(seeded_label):
    labels_page, name = seeded_label
    assert labels_page.delete_label(name)


@pytest.mark.step_6_deleteAll
def test_delete_all_labels(seeded_label):
    labels_page, _name = seeded_label
    assert labels_page.delete_all_labels()
