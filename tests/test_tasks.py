import time

import pytest

from pages.labels_page import LabelsPage
from pages.statuses_page import StatusesPage
from pages.tasks_page import TasksPage
from pages.users_page import UsersPage


def build_unique_task_payload(prefix):
    unique_value = time.time_ns()
    title = f"{prefix} {unique_value}"
    content = f"Description {unique_value}"
    return title, content


def build_unique_user_payload(prefix):
    unique_value = time.time_ns()
    email = f"{prefix.lower()}_{unique_value}@gmail.com"
    first = f"{prefix}First_{unique_value}"
    last = f"{prefix}Last_{unique_value}"
    return email, first, last


def build_unique_status_payload(prefix):
    unique_value = time.time_ns()
    name = f"{prefix}_{unique_value}"
    slug = f"slug_{unique_value}"
    return name, slug


def build_unique_label_name(prefix):
    return f"{prefix}_{time.time_ns()}"


def create_user_for_tasks(driver, prefix):
    page = UsersPage(driver)
    page.open_users()
    count_before_create = page.get_users_count()

    email, first, last = build_unique_user_payload(prefix)

    page.click_create()
    page.fill_user_form(email=email, first=first, last=last)
    page.click_save()

    page.open_users()
    page.wait_for_user_present(email)

    count_after_create = page.get_users_count()
    assert count_after_create == count_before_create + 1, (
        f"Ожидали {count_before_create + 1} users, "
        f"но нашли {count_after_create}"
    )
    assert page.is_user_present(email)

    return email


def create_status_for_tasks(driver, prefix):
    page = StatusesPage(driver)
    page.open_statuses()
    count_before_create = page.get_statuses_count()

    name, slug = build_unique_status_payload(prefix)

    page.click_create()
    page.fill_status_form(name=name, slug=slug)
    page.click_save()

    page.open_statuses()
    page.wait_for_status_present(name)

    count_after_create = page.get_statuses_count()
    assert count_after_create == count_before_create + 1, (
        f"Ожидали {count_before_create + 1} statuses, "
        f"но нашли {count_after_create}"
    )
    assert page.is_status_present(name)

    return name, slug


def create_label_for_tasks(driver, prefix):
    page = LabelsPage(driver)
    page.open_labels()
    count_before_create = page.get_labels_count()

    name = build_unique_label_name(prefix)

    page.click_create()
    page.fill_label_form(name=name)
    page.click_save()

    page.open_labels()
    page.wait_for_label_present(name)

    count_after_create = page.get_labels_count()
    assert count_after_create == count_before_create + 1, (
        f"Ожидали {count_before_create + 1} labels, "
        f"но нашли {count_after_create}"
    )
    assert page.is_label_present(name)

    return name


def create_task_dependencies(
    driver,
    prefix,
    *,
    label_count=1,
    with_alt_status=False,
):
    assignee = create_user_for_tasks(driver, f"{prefix}User")

    primary_status, _primary_slug = create_status_for_tasks(
        driver,
        f"{prefix}PrimaryStatus",
    )

    secondary_status = None
    if with_alt_status:
        secondary_status, _secondary_slug = create_status_for_tasks(
            driver,
            f"{prefix}SecondaryStatus",
        )

    labels = []
    for index in range(label_count):
        label_name = create_label_for_tasks(
            driver,
            f"{prefix}Label{index + 1}",
        )
        labels.append(label_name)

    return {
        "assignee": assignee,
        "primary_status": primary_status,
        "secondary_status": secondary_status,
        "labels": labels,
    }


def create_task_and_get_id(
    page,
    *,
    assignee,
    status,
    labels,
    prefix,
):
    page.open_tasks()
    assert page.verify_filters_visible(), (
        "Страница tasks не загрузилась перед созданием задачи"
    )

    count_before_create = page.get_tasks_count()
    title, content = build_unique_task_payload(prefix)

    page.create_task(
        assignee=assignee,
        title=title,
        content=content,
        status=status,
        labels=labels,
    )

    page.open_tasks()
    page.wait_for_task_by_title(title)

    task_id = page.find_task_id_by_title(title)
    assert task_id is not None, f"Задача {title} не найдена"

    count_after_create = page.get_tasks_count()
    assert count_after_create == count_before_create + 1, (
        f"Ожидали {count_before_create + 1} задач, "
        f"но нашли {count_after_create}"
    )

    return (
        task_id,
        title,
        content,
        count_before_create,
        count_after_create,
    )


def apply_filters(page, *, assignee, status, label):
    page.select_filter("assignee_id", assignee)
    page.select_filter("status_id", status)
    page.select_filter("label_id", label)
    time.sleep(1)


def create_filter_dataset(driver):
    filter_user_email = create_user_for_tasks(driver, "FilterUser")
    other_user_email = create_user_for_tasks(driver, "OtherUser")

    filter_status_name, _filter_status_slug = create_status_for_tasks(
        driver,
        "FilterStatus",
    )
    other_status_name, _other_status_slug = create_status_for_tasks(
        driver,
        "OtherStatus",
    )

    filter_label_name = create_label_for_tasks(driver, "FilterLabel")
    other_label_name = create_label_for_tasks(driver, "OtherLabel")

    tasks_page = TasksPage(driver)

    matching_task = create_task_and_get_id(
        tasks_page,
        assignee=filter_user_email,
        status=filter_status_name,
        labels=[filter_label_name],
        prefix="FilterMatch",
    )
    wrong_user_task = create_task_and_get_id(
        tasks_page,
        assignee=other_user_email,
        status=filter_status_name,
        labels=[filter_label_name],
        prefix="FilterWrongUser",
    )
    wrong_status_task = create_task_and_get_id(
        tasks_page,
        assignee=filter_user_email,
        status=other_status_name,
        labels=[filter_label_name],
        prefix="FilterWrongStatus",
    )
    wrong_label_task = create_task_and_get_id(
        tasks_page,
        assignee=filter_user_email,
        status=filter_status_name,
        labels=[other_label_name],
        prefix="FilterWrongLabel",
    )

    return {
        "filter_user_email": filter_user_email,
        "filter_status_name": filter_status_name,
        "filter_label_name": filter_label_name,
        "matching_task": matching_task,
        "wrong_user_task": wrong_user_task,
        "wrong_status_task": wrong_status_task,
        "wrong_label_task": wrong_label_task,
    }


@pytest.mark.step_7_viewBoard
def test_view_tasks(auth_driver):
    page = TasksPage(auth_driver)
    page.open_tasks()

    assert page.verify_filters_visible(), (
        "Фильтры на странице Tasks не загрузились"
    )

    count = page.get_tasks_count()
    assert count > 0, "Задачи не отображаются на канбан-доске"


@pytest.mark.step_7_filtersTasks
def test_filter_tasks(auth_driver):
    dataset = create_filter_dataset(auth_driver)
    page = TasksPage(auth_driver)
    page.open_tasks()

    initial_ids = set(page.get_all_task_ids())
    initial_count = len(initial_ids)
    assert dataset["matching_task"][0] in initial_ids, (
        "Контрольная задача отсутствует на доске до фильтрации"
    )

    apply_filters(
        page,
        assignee=dataset["filter_user_email"],
        status=dataset["filter_status_name"],
        label=dataset["filter_label_name"],
    )

    filtered_ids = set(page.get_all_task_ids())
    filtered_count = len(filtered_ids)

    matching_task_id, matching_title, matching_content, _, _ = (
        dataset["matching_task"]
    )
    wrong_user_task_id = dataset["wrong_user_task"][0]
    wrong_status_task_id = dataset["wrong_status_task"][0]
    wrong_label_task_id = dataset["wrong_label_task"][0]

    assert filtered_count == 1, (
        f"После фильтрации ожидали 1 задачу, но нашли {filtered_count}"
    )
    assert filtered_ids == {matching_task_id}, (
        "Фильтрация вернула не только контрольную задачу"
    )
    assert filtered_ids != initial_ids, "Фильтрация не изменила набор задач"
    assert filtered_count < initial_count, "Фильтры не сузили выборку"

    visible_in_column = set(
        page.get_task_ids_in_column(dataset["filter_status_name"])
    )
    assert filtered_ids == visible_in_column, (
        "После фильтра по статусу видны не только "
        "задачи нужного статуса"
    )

    assert not page.is_task_present(wrong_user_task_id), (
        "Задача с неверным assignee не была отфильтрована"
    )
    assert not page.is_task_present(wrong_status_task_id), (
        "Задача с неверным status не была отфильтрована"
    )
    assert not page.is_task_present(wrong_label_task_id), (
        "Задача с неверным label не была отфильтрована"
    )

    page.open_task_show(matching_task_id)
    details = page.get_current_page_text()

    assert dataset["filter_user_email"].lower() in details, (
        "Контрольная задача не соответствует фильтру assignee"
    )
    assert dataset["filter_label_name"].lower() in details, (
        "Контрольная задача не соответствует фильтру label"
    )
    assert matching_title.lower() in details, (
        "Title контрольной задачи не найден на show-странице"
    )
    assert matching_content.lower() in details, (
        "Content контрольной задачи не найден на show-странице"
    )


@pytest.mark.step_7_createTasks
def test_create_new_task(auth_driver):
    dependencies = create_task_dependencies(
        auth_driver,
        "CreateTask",
        label_count=2,
    )
    page = TasksPage(auth_driver)

    (
        task_id,
        test_title,
        test_content,
        initial_count,
        final_count,
    ) = create_task_and_get_id(
        page,
        assignee=dependencies["assignee"],
        status=dependencies["primary_status"],
        labels=dependencies["labels"],
        prefix="CreateTask",
    )

    assert page.is_task_in_column(
        task_id,
        dependencies["primary_status"],
    ), "Новая задача не попала в ожидаемую колонку"

    assert page.get_task_title(task_id).lower() == test_title.lower()
    assert page.get_task_content(task_id).lower() == test_content.lower()

    page.open_task_show(task_id)
    details = page.get_current_page_text()

    assert dependencies["assignee"].lower() in details
    assert test_title.lower() in details
    assert test_content.lower() in details

    for label_name in dependencies["labels"]:
        assert label_name.lower() in details

    assert final_count == initial_count + 1


@pytest.mark.step_7_editTasks
def test_edit_task(auth_driver):
    dependencies = create_task_dependencies(
        auth_driver,
        "EditTask",
        label_count=2,
        with_alt_status=True,
    )
    page = TasksPage(auth_driver)

    (
        anchor_task_id,
        anchor_title,
        anchor_content,
        _anchor_before,
        _anchor_after,
    ) = create_task_and_get_id(
        page,
        assignee=dependencies["assignee"],
        status=dependencies["primary_status"],
        labels=[dependencies["labels"][0]],
        prefix="AnchorTask",
    )

    (
        task_id,
        old_title,
        old_content,
        _count_before_create,
        _count_after_create,
    ) = create_task_and_get_id(
        page,
        assignee=dependencies["assignee"],
        status=dependencies["primary_status"],
        labels=[dependencies["labels"][0]],
        prefix="EditTaskOld",
    )

    page.open_task_edit(task_id)

    new_title, new_content = build_unique_task_payload("EditTaskNew")

    page.update_task_fields(
        title=new_title,
        content=new_content,
        status=dependencies["secondary_status"],
        new_labels=[dependencies["labels"][1]],
        old_labels=[dependencies["labels"][0]],
    )

    page.open_tasks()
    page.wait_for_task_title(task_id, new_title)

    assert page.is_task_present(task_id), (
        f"После редактирования задача {task_id} пропала с доски"
    )
    assert page.is_task_in_column(
        task_id,
        dependencies["secondary_status"],
    ), "После редактирования задача не сменила статус"
    assert not page.is_task_in_column(
        task_id,
        dependencies["primary_status"],
    ), "После редактирования задача осталась в старом статусе"

    current_title = page.get_task_title(task_id)
    current_content = page.get_task_content(task_id)

    assert current_title.lower() == new_title.lower()
    assert current_content.lower() == new_content.lower()

    assert current_title.lower() != old_title.lower()
    assert current_content.lower() != old_content.lower()

    assert page.get_task_title(anchor_task_id).lower() == (
        anchor_title.lower()
    )
    assert page.get_task_content(anchor_task_id).lower() == (
        anchor_content.lower()
    )

    page.open_task_show(task_id)
    details = page.get_current_page_text()

    assert dependencies["labels"][1].lower() in details
    assert dependencies["labels"][0].lower() not in details
    assert new_title.lower() in details
    assert new_content.lower() in details


@pytest.mark.step_7_dragAndDropTasks
def test_drag_and_drop_between_columns(auth_driver):
    dependencies = create_task_dependencies(
        auth_driver,
        "DnDTask",
        label_count=1,
        with_alt_status=True,
    )
    page = TasksPage(auth_driver)

    (
        anchor_task_id,
        anchor_title,
        anchor_content,
        _anchor_before,
        _anchor_after,
    ) = create_task_and_get_id(
        page,
        assignee=dependencies["assignee"],
        status=dependencies["primary_status"],
        labels=dependencies["labels"],
        prefix="DnDAnchor",
    )

    (
        task_id,
        title,
        content,
        _count_before_create,
        _count_after_create,
    ) = create_task_and_get_id(
        page,
        assignee=dependencies["assignee"],
        status=dependencies["primary_status"],
        labels=dependencies["labels"],
        prefix="DnDTask",
    )

    start_status = dependencies["primary_status"]
    target_status = dependencies["secondary_status"]

    assert page.is_task_in_column(task_id, start_status), (
        f"Задача {task_id} должна быть в {start_status} "
        "перед началом теста"
    )

    page.move_task_to_status(task_id, target_status)

    assert not page.is_task_in_column(task_id, start_status), (
        f"Задача {task_id} осталась в {start_status}"
    )
    assert page.is_task_in_column(task_id, target_status), (
        f"Задача {task_id} не перемещена в {target_status}"
    )

    assert page.is_task_in_column(anchor_task_id, start_status), (
        "Контрольная задача неожиданно сменила колонку"
    )
    assert page.get_task_title(task_id).lower() == title.lower()
    assert page.get_task_content(task_id).lower() == content.lower()
    assert page.get_task_title(anchor_task_id).lower() == (
        anchor_title.lower()
    )
    assert page.get_task_content(anchor_task_id).lower() == (
        anchor_content.lower()
    )


@pytest.mark.step_7_deleteTasks
def test_delete_task_by_show(auth_driver):
    dependencies = create_task_dependencies(
        auth_driver,
        "DeleteTask",
        label_count=1,
    )
    page = TasksPage(auth_driver)

    (
        anchor_task_id,
        anchor_title,
        anchor_content,
        _anchor_before,
        _anchor_after,
    ) = create_task_and_get_id(
        page,
        assignee=dependencies["assignee"],
        status=dependencies["primary_status"],
        labels=dependencies["labels"],
        prefix="DeleteAnchor",
    )

    (
        task_id,
        title,
        _content,
        _count_before_create,
        count_before_delete,
    ) = create_task_and_get_id(
        page,
        assignee=dependencies["assignee"],
        status=dependencies["primary_status"],
        labels=dependencies["labels"],
        prefix="DeleteTask",
    )

    assert page.is_task_present(task_id), f"Задача {task_id} не найдена"

    page.open_task_delete(task_id)
    page.delete_task()
    time.sleep(1)

    page.open_tasks()
    page.wait_for_task_absence(task_id)

    final_count = page.get_tasks_count()
    assert final_count == count_before_delete - 1, (
        f"Ожидали {count_before_delete - 1} задач, "
        f"но нашли {final_count}"
    )
    assert not page.is_task_present(task_id), (
        f"Карточка с ID = {task_id} не была удалена"
    )
    assert page.is_task_present(anchor_task_id), (
        "Контрольная задача была удалена вместо целевой"
    )
    assert page.get_task_title(anchor_task_id).lower() == (
        anchor_title.lower()
    )
    assert page.get_task_content(anchor_task_id).lower() == (
        anchor_content.lower()
    )

    page_context = page.get_page_context().lower()
    assert title.lower() not in page_context, (
        f"Удаленная задача '{title}' все еще видна на странице"
    )
