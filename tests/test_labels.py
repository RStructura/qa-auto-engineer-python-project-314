import time

import pytest
from selenium.webdriver.common.by import By

from pages.labels_page import LabelsPage


def build_unique_label_name(prefix="Label"):
    return f"{prefix}_{time.time_ns()}"


@pytest.fixture
def labels_page(auth_driver):
    page = LabelsPage(auth_driver)
    assert page.delete_all_labels()
    return page


def create_label_and_get_state(page, prefix="Label"):
    page.open_labels()
    count_before_create = page.get_labels_count()

    new_name = build_unique_label_name(prefix)

    page.click_create()
    page.fill_label_form(name=new_name)
    page.click_save()

    page.open_labels()
    page.wait_for_label_present(new_name)

    count_after_create = page.get_labels_count()

    assert count_after_create == count_before_create + 1, (
        f"Ожидали {count_before_create + 1} labels, "
        f"но нашли {count_after_create}"
    )
    assert page.is_label_present(new_name)

    return new_name, count_before_create, count_after_create


def pick_target_and_untouched_label(page, first_name, second_name):
    page.open_labels()
    visible_names = page.get_all_label_names()

    assert first_name in visible_names
    assert second_name in visible_names

    if visible_names[0] == first_name:
        return second_name, first_name

    if visible_names[0] == second_name:
        return first_name, second_name

    return second_name, first_name


@pytest.mark.step_6_viewList
def test_view_labels_list(labels_page):
    target_name, _count_before, _count_after = create_label_and_get_state(
        labels_page,
        prefix="ViewLabel",
    )

    header_text = labels_page.driver.find_element(
        By.CSS_SELECTOR,
        "table thead",
    ).text

    assert "Name" in header_text
    assert labels_page.driver.find_element(By.TAG_NAME, "table").is_displayed()

    row_values = labels_page.get_label_row_values(target_name)
    assert row_values["name"] == target_name


@pytest.mark.step_6_createLabel
def test_create_label(labels_page):
    new_name, count_before, count_after = create_label_and_get_state(
        labels_page,
        prefix="CreateLabel",
    )

    row_values = labels_page.get_label_row_values(new_name)
    assert row_values["name"] == new_name
    assert count_after == count_before + 1


@pytest.mark.step_6_editLabel
def test_edit_label(labels_page):
    keep_name, _, _ = create_label_and_get_state(
        labels_page,
        prefix="KeepLabel",
    )
    editable_name, _, count_before_edit = create_label_and_get_state(
        labels_page,
        prefix="EditLabelOld",
    )

    target_name, untouched_name = pick_target_and_untouched_label(
        labels_page,
        keep_name,
        editable_name,
    )

    labels_page.open_labels()
    labels_page.open_label_by_name(target_name)

    labels_page.force_clear_input("name")
    assert labels_page.get_input_value("name") == "", (
        "Поле name не очистилось"
    )

    labels_page.click_save()
    assert "required" in labels_page.get_error_message().lower()

    new_name = build_unique_label_name("EditLabelNew")
    labels_page.fill_label_form(name=new_name)
    labels_page.click_save()

    labels_page.open_labels()
    labels_page.wait_for_label_present(new_name)

    count_after_edit = labels_page.get_labels_count()
    assert count_after_edit == count_before_edit, (
        "После редактирования количество labels не должно меняться"
    )
    assert labels_page.is_label_present(new_name)
    assert not labels_page.is_label_present(target_name)
    assert labels_page.is_label_present(untouched_name)

    row_values = labels_page.get_label_row_values(new_name)
    assert row_values["name"] == new_name


@pytest.mark.step_6_deleteOne
def test_delete_label_via_checkbox(labels_page):
    keep_name, _, _ = create_label_and_get_state(
        labels_page,
        prefix="KeepCheckboxLabel",
    )
    delete_name, _, count_before_delete = create_label_and_get_state(
        labels_page,
        prefix="DeleteLabelCheckbox",
    )

    target_name, untouched_name = pick_target_and_untouched_label(
        labels_page,
        keep_name,
        delete_name,
    )

    labels_page.open_labels()
    labels_page.select_checkbox_by_name(target_name)
    labels_page.click_delete_button()

    labels_page.open_labels()
    labels_page.wait_for_label_absent(target_name)

    count_after_delete = labels_page.get_labels_count()

    assert not labels_page.is_label_present(target_name)
    assert labels_page.is_label_present(untouched_name)
    assert count_after_delete == count_before_delete - 1


@pytest.mark.step_6_deleteOne
def test_delete_label_via_edit(labels_page):
    keep_name, _, _ = create_label_and_get_state(
        labels_page,
        prefix="KeepEditLabel",
    )
    delete_name, _, count_before_delete = create_label_and_get_state(
        labels_page,
        prefix="DeleteLabelEdit",
    )

    target_name, untouched_name = pick_target_and_untouched_label(
        labels_page,
        keep_name,
        delete_name,
    )

    labels_page.open_labels()
    labels_page.open_label_by_name(target_name)
    labels_page.click_delete_button()

    labels_page.open_labels()
    labels_page.wait_for_label_absent(target_name)

    count_after_delete = labels_page.get_labels_count()

    assert not labels_page.is_label_present(target_name)
    assert labels_page.is_label_present(untouched_name)
    assert count_after_delete == count_before_delete - 1


@pytest.mark.step_6_deleteAll
def test_delete_all_labels(labels_page):
    created_names = []
    for prefix in (
        "DeleteAllLabelA",
        "DeleteAllLabelB",
        "DeleteAllLabelC",
    ):
        created_name, _, _ = create_label_and_get_state(
            labels_page,
            prefix=prefix,
        )
        created_names.append(created_name)

    labels_page.open_labels()
    initial_count = labels_page.get_labels_count()
    assert initial_count == len(created_names)

    labels_page.select_all_checkbox()
    labels_page.click_delete_button()

    labels_page.open_labels()
    labels_page.wait_for_empty_state()

    assert labels_page.is_empty_message_visible()
    assert labels_page.get_labels_count() == 0

    for created_name in created_names:
        assert not labels_page.is_label_present(created_name)
