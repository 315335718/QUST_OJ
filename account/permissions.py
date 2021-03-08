def is_admin_or_root(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


def is_problem_manager(user, problem):
    return user.is_authenticated and (is_admin_or_root(user) or problem.managers.filter(pk=user.pk).exists())


def is_contest_manager(user, contest):
    return user.is_authenticated and (is_admin_or_root(user) or contest.managers.filter(pk=user.pk).exists())
