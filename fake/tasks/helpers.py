def before(task, prereq):
    task.prereqs.append(prereq)


def after(task, postreq):
    task.postreqs.append(postreq)
