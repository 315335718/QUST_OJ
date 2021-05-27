import re

def get_table(type, description, checker):
    result = dict()
    table_to_delete = re.findall(r'\s*create\s+table\s+(\S+)\s*\(', description, re.I)
    result['table_to_delete'] = table_to_delete
    if type == '查询类':
        result['other'] = ''
    elif type == '更新类':
        # table_to_select = re.findall(r'\s*update\s+(\S+)\s+', checker, re.I)
        cur = re.findall(r'\s*update\s+(\S+)\s+', checker, re.I)
        if len(cur) > 0:
            table_to_select = cur
        else:
            cur = re.findall(r'\s*delete\s+from\s+(\S+)\s+', checker, re.I)
            if len(cur) > 0:
                table_to_select = cur
            else:
                cur = re.findall(r'\s*insert\s+into\s+(\S+)\s*\(', checker, re.I)
                if len(cur) > 0:
                    table_to_select = cur
                else:
                    table_to_select = re.findall(r'\s*insert\s+into\s+(\S+)\s+', checker, re.I)
        result['other'] = table_to_select
    elif type == '创建视图类':
        view_to_select = re.findall(r'\s*create\s+view\s+(\S+)\s*', checker, re.I)
        result['other'] = view_to_select
    elif type == '创建基本表':
        table_to_create = re.findall(r'\s*create\s+table\s+(\S+)\s*\(', checker, re.I)
        result['other'] = table_to_create
    return result
