from django import template

register = template.Library()


@register.simple_tag
def menu_list():
    modules_list = {0: ({'id': 0, 'name': 'overview', 'desc': "概览"},
                        {'id': 1, 'name': "get_plan", 'desc': "执行计划"},
                        {'id': 2, 'name': 'get_result', 'desc': "执行结果"},
                        {'id': 3, 'name': 'insert_plan', 'desc': "添加执行计划"},),
                    1: ({'id': 4,  'name': 'insert_plan', 'desc': "执行计划"},)}

    return modules_list
