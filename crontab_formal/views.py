from django.shortcuts import render, redirect
from rcrontab.models import PyScriptOwnerList
from .models import PyScriptBaseInfoV2
from django.db import connection
from . import forms
from .read_program_base_info import ReadProgramsInfo

# Create your views here.


def insert(request):
    if request.method == 'POST':
        form = forms.Path(request.POST, request.FILES)
        if form.is_valid():
            # file is saved
            path = form.save()
            ReadProgramsInfo(path).get_programs_info_list()
    else:
        form = forms.Path()
    return render(request, 'rcrontab_formals/insert.html', {'form': form})


def get_plan(request):
    owners = PyScriptOwnerList.objects.all()
    owners_programs_dict = {}
    for owner in owners:
        programs = PyScriptBaseInfoV2.objects.filter(owner=owner)
        programs_dic = {}
        for program in programs:
            sid = program.sid
            programs_dic[sid] = {}
            programs_dic[sid]['program_info'] = program
            result_tables_sql_code = """select concat("[",c.db_server,"]",c.db_name,".",c.table_name)
                       from py_script_base_info_v2 a
                       left join py_script_base_info_v2_result_tables b on a.sid = b.pyscriptbaseinfov2_id
                       left JOIN py_script_tables_info c on c.id = b.tablesinfo_id
                       where a.sid = {sid}""".format(sid=sid)
            with connection.cursor() as cursor:
                cursor.execute(result_tables_sql_code)
                tables = cursor.fetchall()
                tables_str = ""
                n = 1
                for table in tables:
                    if table[0]:
                        tables_str += "{number}.{table_name} <br>".format(number=n, table_name=table[0])
                        n += 1
                programs_dic[program.sid]['result_tables'] = tables_str

            pre_tables_sql_code = """select concat("[",c.db_server,"]",c.db_name,".",c.table_name)
                                   from py_script_base_info_v2 a
                                   left join py_script_base_info_v2_pre_tables b on a.sid = b.pyscriptbaseinfov2_id
                                   left JOIN py_script_tables_info c on c.id = b.tablesinfo_id
                                   where a.sid = {sid}""".format(sid=sid)
            with connection.cursor() as cursor:
                cursor.execute(pre_tables_sql_code)
                tables = cursor.fetchall()
                tables_str = ""
                n = 1
                for table in tables:
                    if table[0]:
                        tables_str += "{number}.{table_name} <br>".format(number=n, table_name=table[0])
                        n += 1
                programs_dic[program.sid]['pre_tables'] = tables_str

        owners_programs_dict[owner.owner] = programs_dic
    return render(request, 'rcrontab_formals/get_plan.html', {'programs_dict': owners_programs_dict})








