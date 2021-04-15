import re


def drop_database_safe(code):
    sql_code = re.findall(r'\s*drop\s+database\s+\S+;\s*', code, re.I)
    if len(sql_code) > 0:
        return 0
    else:
        return 1
