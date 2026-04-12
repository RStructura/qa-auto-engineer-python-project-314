def pytest_configure(config):
    markers = [
        "smoke: smoke test",
        "step_3: auth test",
        "step_4_viewList: users list test",
        "step_4_createUser: users create test",
        "step_4_editUser: users edit test",
        "step_4_deleteOne: users delete one test",
        "step_4_deleteAll: users delete all test",
        "step_5_viewList: statuses list test",
        "step_5_createStatus: statuses create test",
        "step_5_editStatus: statuses edit test",
        "step_5_deleteOne: statuses delete one test",
        "step_5_deleteAll: statuses delete all test",
        "step_6_viewList: labels list test",
        "step_6_createLabel: labels create test",
        "step_6_editLabel: labels edit test",
        "step_6_deleteOne: labels delete one test",
        "step_6_deleteAll: labels delete all test",
        "step_7_viewBoard: tasks board test",
        "step_7_filtersTasks: tasks filter test",
        "step_7_createTasks: tasks create test",
        "step_7_editTasks: tasks edit test",
        "step_7_dragAndDropTasks: tasks dnd test",
        "step_7_deleteTasks: tasks delete test",
    ]

    for marker in markers:
        config.addinivalue_line("markers", marker)
