from django.shortcuts import render, redirect, HttpResponse
from .models import PyScriptBaseInfoV2, PyScriptOwnerListV2
from django.db import connections
from . import forms
from .read_program_base_info import ReadProgramsInfo
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required

# Create your views here.


@login_required
def insert(request):
    if request.method == 'POST':
        form = forms.ConfigFileLogForm(request.POST, request.FILES)
        print("Post:", request.POST)
        print("file_name:", request.FILES)
        if form.is_valid():
            # file is saved
            configfile = form.save()
            info = ReadProgramsInfo(configfile).get_programs_info_list()
        else:
            info = form.errors
            print(info)
        return HttpResponse(info)
    else:
        form = forms.ConfigFileLogForm()
        return render(request, 'rcrontab_formals/insert.html', {'form': form})


@login_required
def get_plan(request):
    owners = PyScriptOwnerListV2.objects.all()
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
            with connections['crontab_formal_db'].cursor() as cursor:
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
            with connections['crontab_formal_db'].cursor() as cursor:
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
    print(owners_programs_dict)
    return render(request, 'rcrontab_formals/get_plan.html', {'programs_dict': owners_programs_dict})


@login_required
def get_result(request):
    if request.method == 'GET':
        if request.GET:
            owner = request.GET['owner']
            version = request.GET['version']
            print(owner, version)
            sql_code = '''select 
              a.sid,a.`name`,a.version,
              a.owner_id as owner,
              b.begin_time,
              c.event_type as exec_result,
              c.end_time,
              c.extra_info,
              c.id,
              a.exec_plan,
              d.err_num,
              case when ISNULL(b.begin_time) then 0
              when b.begin_time > c.end_time then 1
              when isnull(c.end_time) then 2
              ELSE  3 END as stats
              from 
              (select b.sid,b.`name`,a.version,b.owner_id,b.exec_plan
              from 
              (select DISTINCT version from py_script_result_log order by version desc LIMIT 5) a
              ,(select sid,name,owner_id,exec_plan from py_script_base_info_v2
              )b ORDER BY a.version,b.sid) a
              LEFT JOIN 
              (SELECT 
              sid,version,max(event_time) as begin_time
              from
              py_script_result_log
              where event_type=1
              GROUP BY sid,version
              ) b on  a.version=b.version and a.sid=b.sid 
              LEFT JOIN 
              (
              select b.id,a.sid,a.version,a.event_time as end_time, b.extra_info,b.event_type
              from
              (SELECT 
              sid,version,max(event_time) as event_time
              from
              py_script_result_log
              where event_type in (2,3)
              GROUP BY sid,version) a
              LEFT JOIN (select id,sid,extra_info,event_type,version,event_time from py_script_result_log where event_type in (2,3))b
              on a.sid= b.sid and a.version=b.version and a.event_time=b.event_time
              ORDER BY a.version,a.event_time) c on a.version=c.version and a.sid=c.sid 
              LEFT JOIN
              (SELECT 
              sid,version,count(*) as err_num
              from
              py_script_result_log
              where event_type=3
              GROUP BY sid,version,date(event_time)) d on  a.version=d.version and a.sid=d.sid 
            where a.owner_id=%s  AND a.version=%s 
            ORDER by exec_plan, exec_result desc
            '''
            with connections['crontab_formal_db'].cursor() as cursor:
                cursor.execute(sql_code, [owner, version])
                result_list = cursor.fetchall()
                return render(request, 'rcrontab_formals/get_result_table.html', {'result_list': result_list})
        else:
            owners_list = PyScriptOwnerListV2.objects.all()
            time_list_sql_code = '''select DISTINCT version from py_script_result_log order by version desc LIMIT 5'''
            with connections['crontab_formal_db'].cursor() as cursor:
                cursor.execute(time_list_sql_code)
                time_list1 = cursor.fetchall()
                time_list2 = list()
                for ti in time_list1:
                    time_list2.append(str(ti[0]))
            return render(request, 'rcrontab_formals/get_result.html', {'owners_list': owners_list,
                                                                        'version_list': time_list2})


def send_email(request):
    if request.method == 'GET':
        subject = request.GET['subject']
        msg = request.GET['msg']
        to_address = request.GET['to_address']
        send_mail(subject, msg, 'huruizhi@pystandard.com', [to_address, ], fail_silently=False)
        return HttpResponse("OK")










