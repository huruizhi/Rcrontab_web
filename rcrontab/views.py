from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from django.db import connection
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate, forms as uforms
from django.forms.models import model_to_dict
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
import socket
import time
import json
from rcrontab import models, forms

# Create your views here.

def do_login(request):
    if request.method == 'POST':
        user = authenticate(username=request.POST.get('username'),
                            password=request.POST.get('password'))
        if user is not None:
            login(request, user)
            return HttpResponseRedirect('/index/')
        else:
            return render(request, 'crontab/login.html',  {'err_info': "valid username or password"})
    else:
        return render(request, 'crontab/login.html')


@login_required
def index(request, mode='index', sid=None):
    if sid:
        sid = int(sid)
    in_index = InIndex(request, sid)
    if not hasattr(in_index, mode):
        mode = 'index'
    func = getattr(in_index, mode)
    resp = func()
    return resp


def do_logout(request):
    logout(request)
    return HttpResponseRedirect('/index/')


class InIndex:

    def __init__(self, request, sid=None):
        self.r = request
        self.sid = sid
        self.user = uforms.User.objects.get(username=self.r.user)
        setattr(self, 'get_plan', self._get_plan)
        setattr(self, 'get_result', self._exec_result)
        setattr(self, 'edit_plan', self._edit_plan)
        setattr(self, 'exec_log', self._exec_log)
        setattr(self, 'index', self._index)
        setattr(self, 'rerun_program', self._rerun_program)
        setattr(self, 'insert_plan', self._insert_plan)

    @staticmethod
    def _index():
        return HttpResponseRedirect('/index/get_plan/')

    def _get_plan(self):
        if self.r.method == "POST":
            dic = json.loads(self.r.POST['data_list'])
            user = dic['name']
            sql_str = "select sid,parent_id,exec_time,deploy_server,CONCAT(deploy_directory,name),function" \
                      " from py_script_base_info_new where exec_plan=1 and `owner`=%s"
            with connection.cursor() as cursor:
                cursor.execute(sql_str, [user])
                rows = cursor.fetchall()
            return render(self.r, 'crontab/sql_query_plan.html', {'item_list': rows, 'user_name': self.user})
        else:
            sql_query_owners = "select distinct owner from py_script_base_info_new"
            with connection.cursor() as cursor:
                cursor.execute(sql_query_owners)
                owners = cursor.fetchall()
            active_module = {'id': 1, 'name': "get_plan", 'desc': "执行计划"}
            return render(self.r, 'crontab/get_exec_plan.html',
                          {'owner_list': owners, 'user_name': self.user,
                           'active_module': active_module})

    def _insert_plan(self):
        active_module = {'id': 3, 'name': 'insert_plan', 'desc': "添加执行计划"}
        if self.r.method == "GET":
            form = forms.EditExec()

        else:
            plan_info = self.r.POST
            form = forms.EditExec(plan_info)
            if form.is_valid():
                form.save()
                form = forms.EditExec()

        return render(self.r, 'crontab/insert.html', {'form': form, 'user_name': self.user,
                                                      'active_module': active_module, 'errs': form.errors})

    def _exec_result(self):
        if self.r.method == "GET":
            if 'name' not in self.r.GET:
                sql_query_owners = "select distinct owner from py_script_base_info_new"
                with connection.cursor() as cursor:
                    cursor.execute(sql_query_owners)
                    owners = cursor.fetchall()
                active_module = {'id': 2, 'name': 'get_result', 'desc': "执行结果"}
                return render(self.r, 'crontab/get_exec_result.html',
                              {'owner_list': owners, 'user_name': self.user,
                               'active_module': active_module})

            else:
                user = self.r.GET['name']
                print(self.r.GET)
                if 'page' not in self.r.GET:
                    page = 1
                else:
                    page = self.r.GET['page']
                now = time.time()
                yesterday = now - 60 * 60 * 24
                date_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(yesterday))
                sql_str = "SELECT a.sid,a.name, CAST(b.start_time as char),cast(b.end_time as CHAR),b.is_normal from " \
                          "(select sid, `name` from py_script_base_info_new " \
                          "where exec_plan=1 and `owner`= %s and is_stop=0) a" \
                          " LEFT JOIN " \
                          "(select sid,start_time,end_time,is_normal from py_script_err_info_daliy" \
                          " where start_time > %s) b" \
                          " on a.sid=b.sid "
                with connection.cursor() as cursor:
                    cursor.execute(sql_str, [user, date_str])
                    rows = cursor.fetchall()
                    page_row = Paginator(rows, 15)
                    try:
                        rows_list = page_row.page(page)
                    except PageNotAnInteger:
                        rows_list = page_row.page(1)
                    except EmptyPage:
                        rows_list = page_row.page(page_row.num_pages)
                    contacts = page_row.get_page(page)
                    return render(self.r, 'crontab/sql_query_plan_result.html',
                                  {'item_list': rows_list.object_list, 'contacts': contacts,
                                   'name': user, 'page_range': page_row.page_range})

    def _edit_plan(self):
        sid = self.sid
        script_info = models.PyScriptBaseInfoNew.objects.get(sid=sid)
        if self.r.method == "POST":
            data_dict = self.r.POST
            form = forms.EditExec(data_dict, initial=model_to_dict(script_info))
            if form.is_valid():
                if form.has_changed():
                    f = forms.EditExec(data_dict, instance=script_info)
                    f.save()
                    return HttpResponse("OK")
                else:
                    return HttpResponse("NoChange")
            else:
                print(form.errors)
                return render(self.r, 'crontab/forms.html', {'form': form, 'errs': form.errors})
        else:
            form = forms.EditExec(initial=model_to_dict(script_info))
        return render(self.r, 'crontab/forms.html', {'form': form})

    def _exec_log(self):
        if self.r.method == 'GET':
            sid = self.sid
            sql_str = "select sid,CAST(start_time as char),cast(end_time as CHAR),is_normal" \
                      " from py_script_err_info_daliy as a where sid=%s order by start_time desc limit 10"
            with connection.cursor() as cursor:
                cursor.execute(sql_str, [sid, ])
                rows = cursor.fetchall()
            return render(self.r, 'crontab/table_exec_result.html', {'list': rows, })
        else:
            return HttpResponse("ERROR!")

    def _rerun_program(self):
        if self.r.method == 'GET':
            sid = self.sid
            sid = {'sid': sid, }
            _send_to_master(5, **sid)
            print(sid)
            return HttpResponse("OK")


def _send_to_master(msg_type, **kwargs):
    ip = '192.168.0.155'
    port = 22349
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        string = {'type': msg_type}
        if kwargs:
            string = dict(string, **kwargs)
            print(string)
        send_str = json.dumps(string).encode('utf-8')
        print(ip, port)
        s.connect((ip, port))
        s.sendall(send_str)
        data = s.recv(1024).decode('utf-8')
        print('send_to_master:', data)






