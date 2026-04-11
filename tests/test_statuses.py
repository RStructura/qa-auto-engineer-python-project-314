import time

import pytest
from selenium.webdriver.common.by import By

from pages.statuses_page import StatusesPage


def build_unique_status_payload(prefix="Status"):
    unique_value = time.time_ns()
    name = f"{prefix}_{unique_value}"
    slug = f"slug_{unique_value}"
    return name, slug


@pytest.fixture
def statuses_page(auth_driver):
    page = StatusesPage(auth_driver)
    assert page.delete_all_statuses()
    return page


def create_status_and_get_state(page, prefix="Status"):
    page.open_statuses()
    count_before_create = page.get_statuses_count()

    new_name, new_slug = build_unique_status_payload(prefix)

    page.click_create()
    page.fill_status_form(name=new_name, slug=new_slug)
    page.click_save()

    page.open_statuses()
    page.wait_for_status_present(new_name)

    count_after_create = page.get_statuses_count()

    assert count_after_create == count_before_create + 1, (
        f"Ожидали {count_before_create + 1} statuses, "
        f"но нашли {count_after_create}"
    )
    assert page.is_status_present(new_name)

    return new_name, new_slug, count_before_create, count_after_create


def pick_target_and_untouched_status(page, first_name, second_name):
    page.open_statuses()
    visible_names = page.get_all_status_names()

    assert first_name in visible_names
    assert second_name in visible_names

    if visible_names[0] == first_name:
        return second_name, first_name

    if visible_names[0] == second_name:
        return first_name, second_name

    return second_name, first_name


@pytest.mark.step_5_viewList
def test_view_statuses_list(statuses_page):
    target_name, target_slug, _, _ = create_status_and_get_state(
        statuses_page,
        prefix="ViewStatus",
    )

    header_text = statuses_page.driver.find_element(
        By.CSS_SELECTOR,
        "table thead",
    ).text

    assert "Name" in header_text
    assert "Slug" in header_text
    assert statuses_page.driver.find_element(
        By.TAG_NAME,
        "table",
    ).is_displayed()

    row_values = statuses_page.get_status_row_values(target_name)
    assert row_values["name"] == target_name
    assert row_values["slug"] == target_slug


@pytest.mark.step_5_createStatus
def test_create_status(statuses_page):
    new_name, new_slug, count_before, count_after = (
        create_status_and_get_state(
            statuses_page,
            prefix="CreateStatus",
        )
    )

    row_values = statuses_page.get_status_row_values(new_name)
    assert row_values["name"] == new_name
    assert row_values["slug"] == new_slug
    assert count_after == count_before + 1


@pytest.mark.step_5_editStatus
def test_edit_status(statuses_page):
    keep_name, keep_slug, _, _ = create_status_and_get_state(
        statuses_page,
        prefix="KeepStatus",
    )
    editable_name, _editable_slug, _, count_before_edit = (
        create_status_and_get_state(
            statuses_page,
            prefix="EditStatusOld",
        )
    )

    target_name, untouched_name = pick_target_and_untouched_status(
        statuses_page,
        keep_name,
        editable_name,
    )
    untouched_slug = keep_slug if untouched_name == keep_name else None

    statuses_page.open_statuses()
    statuses_page.open_status_by_name(target_name)

    statuses_page.force_clear_input("name")
    statuses_page.force_clear_input("slug")
    assert statuses_page.get_input_value("name") == "", (
        "Поле name не очистилось"
    )
    assert statuses_page.get_input_value("slug") == "", (
        "Поле slug не очистилось"
    )

    statuses_page.click_save()
    assert "required" in statuses_page.get_error_message().lower()

    new_name, new_slug = build_unique_status_payload("EditStatusNew")
    statuses_page.fill_status_form(name=new_name, slug=new_slug)
    statuses_page.click_save()

    statuses_page.open_statuses()
    statuses_page.wait_for_status_present(new_name)

    count_after_edit = statuses_page.get_statuses_count()
    assert count_after_edit == count_before_edit, (
        "После редактирования количество statuses "
        "не должно меняться"
    )
    assert statuses_page.is_status_present(new_name)
    assert not statuses_page.is_status_present(target_name)
    assert statuses_page.is_status_present(untouched_name)

    row_values = statuses_page.get_status_row_values(new_name)
    assert row_values["name"] == new_name
    assert row_values["slug"] == new_slug

    untouched_row = statuses_page.get_status_row_values(untouched_name)
    assert untouched_row["name"] == untouched_name
    if untouched_slug is not None:
        assert untouched_row["slug"] == untouched_slug


@pytest.mark.step_5_deleteOne
def test_delete_status_via_checkbox(statuses_page):
    keep_name, keep_slug, _, _ = create_status_and_get_state(
        statuses_page,
        prefix="KeepCheckboxStatus",
    )
    delete_name, _delete_slug, _, count_before_delete = (
        create_status_and_get_state(
            statuses_page,
            prefix="DeleteStatusCheckbox",
        )
    )

    target_name, untouched_name = pick_target_and_untouched_status(
        statuses_page,
        keep_name,
        delete_name,
    )

    statuses_page.open_statuses()
    statuses_page.select_checkbox_by_name(target_name)
    statuses_page.click_delete_button()

    statuses_page.open_statuses()
    statuses_page.wait_for_status_absent(target_name)

    count_after_delete = statuses_page.get_statuses_count()

    assert not statuses_page.is_status_present(target_name)
    assert statuses_page.is_status_present(untouched_name)
    if untouched_name == keep_name:
        untouched_row = statuses_page.get_status_row_values(untouched_name)
        assert untouched_row["slug"] == keep_slug
    assert count_after_delete == count_before_delete - 1


@pytest.mark.step_5_deleteOne
def test_delete_status_via_edit(statuses_page):
    keep_name, keep_slug, _, _ = create_status_and_get_state(
        statuses_page,
        prefix="KeepEditStatus",
    )
    delete_name, _delete_slug, _, count_before_delete = (
        create_status_and_get_state(
            statuses_page,
            prefix="DeleteStatusEdit",
        )
    )

    target_name, untouched_name = pick_target_and_untouched_status(
        statuses_page,
        keep_name,
        delete_name,
    )

    statuses_page.open_statuses()
    statuses_page.open_status_by_name(target_name)
    statuses_page.click_delete_button()

    statuses_page.open_statuses()
    statuses_page.wait_for_status_absent(target_name)

    count_after_delete = statuses_page.get_statuses_count()

    assert not statuses_page.is_status_present(target_name)
    assert statuses_page.is_status_present(untouched_name)
    if untouched_name == keep_name:
        untouched_row = statuses_page.get_status_row_values(untouched_name)
        assert untouched_row["slug"] == keep_slug
    assert count_after_delete == count_before_delete - 1


@pytest.mark.step_5_deleteAll
def test_delete_all_statuses(statuses_page):
    created_statuses = []
    for prefix in (
        "DeleteAllStatusA",
        "DeleteAllStatusB",
        "DeleteAllStatusC",
    ):
        name, slug, _, _ = create_status_and_get_state(
            statuses_page,
            prefix=prefix,
        )
        created_statuses.append((name, slug))

    statuses_page.open_statuses()
    initial_count = statuses_page.get_statuses_count()
    assert initial_count == len(created_statuses)

    statuses_page.select_all_checkbox()
    statuses_page.click_delete_button()

    statuses_page.open_statuses()
    statuses_page.wait_for_empty_state()

    assert statuses_page.get_statuses_count() == 0
    assert statuses_page.is_empty_message_visible()

    for name, _slug in created_statuses:
        assert not statuses_page.is_status_present(name)
