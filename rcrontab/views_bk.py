from django.shortcuts import render, HttpResponse,HttpResponseRedirect
from django.db import connection
from django.forms.models import model_to_dict
from django.forms.formsets import formset_factory
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
import time
import json
from rcrontab import models, forms
# Create your views here.


def do_login(request):
    if request.path == 'POST':
        user = authenticate(username=request.POST.get('username'),
                            password=request.POST.get('password'))
        if user:
            login(request, user)
            return HttpResponseRedirect('/index/')
    return render(request, 'crontab/index.html')


@login_required
def index(request):
    if request.method == "GET":
        if 'func' in request.GET:
            func = request.GET['func']
            print(func)
            index_ajax = InIndex(request)
            if hasattr(index_ajax, func):
                f = getattr(index_ajax, func)
                html = f()
                return html
        else:
            return render(request, 'crontab/index.html')
    else:
        if 'func' in request.POST:
            func = request.POST['func']
            print(func)
            index_ajax = InIndex(request)
            if hasattr(index_ajax, func):
                f = getattr(index_ajax, func)
                html = f()
                return html


class InIndex:

    def __init__(self, request):
        self.r = request
        setattr(self, 'plan', self.get_plan)
        setattr(self, 'result', self.exec_result)
        setattr(self, 'edit', self.edit_exec)

    def get_plan(self):
        if self.r.method == "POST":
            dic = json.loads(self.r.POST['data_list'])
            user = dic['name']
            sql_str = "select sid,parent_id,exec_time,deploy_server,CONCAT(deploy_directory,name)" \
                      " from py_script_base_info_new where exec_plan=1 and `owner`=%s"
            with connection.cursor() as cursor:
                cursor.execute(sql_str, [user])
                rows = cursor.fetchall()
            return render(self.r, 'crontab/sql_query_plan.html', {'item_list': rows})
        else:
            sql_query_owners = "select distinct owner from py_script_base_info_new"
            with connection.cursor() as cursor:
                cursor.execute(sql_query_owners)
                owners = cursor.fetchall()
                print(owners)
            return render(self.r, 'crontab/get_exec_plan.html', {'owner_list': owners})

    def exec_result(self):
        if self.r.method == "POST":
            dic = json.loads(self.r.POST['data_list'])
            user = dic['name']
            now = time.time()
            yesterday = now-60*60*24
            date_str = time.strftime('%Y-%m-%d %H:%M:%S',  time.localtime(yesterday))
            sql_str = "SELECT a.sid,CAST(b.start_time as char),cast(b.end_time as CHAR),b.is_normal from " \
                      "(select sid from py_script_base_info_new where exec_plan=1 and `owner`= %s) a" \
                      " LEFT JOIN " \
                      "py_script_err_info_daliy b" \
                      " on a.sid=b.sid " \
                      "where b.start_time> %s"
            with connection.cursor() as cursor:
                cursor.execute(sql_str, [user, date_str])
                rows = cursor.fetchall()
            print(rows)
            return render(self.r, 'crontab/sql_query_plan_result.html', {'item_list': rows})
        else:
            sql_query_owners = "select distinct owner from py_script_base_info_new"
            with connection.cursor() as cursor:
                cursor.execute(sql_query_owners)
                owners = cursor.fetchall()
                print(owners)
            return render(self.r, 'crontab/get_exec_result.html', {'owner_list': owners})

    def edit_exec(self):
        if self.r.method == "POST":
            data_dict = json.loads(self.r.POST['data'])
            sid = int(data_dict['sid'])
            print(data_dict)
            form = forms.EditExec(data_dict)
            if form.is_valid():
                a = models.PyScriptBaseInfoNew.objects.get(sid=sid)
                f = forms.EditExec(data_dict, instance=a)
                f.save()
                return HttpResponse("OK")
            else:
                return render(self.r, 'crontab/forms.html', {'form': form})
        else:
            sid = int(self.r.GET['sid'])
            script_info = models.PyScriptBaseInfoNew.objects.get(sid=sid)
            form = forms.EditExec(instance=script_info).as_p()
        return render(self.r, 'crontab/forms.html', {'form': form})


def edit_exec(request):
    # edit_form_factor = formset_factory(forms.EditForm, extra=2, max_num=1)
    # form = edit_form_factor(initial=[{'sid': 1, 'url': 'http://www.baidu.com'},
    #                                 {'sid': 2, 'url': 'http://www.youku.com'}],).as_p()
    if request.method == "POST":
        form = forms.EditForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            return HttpResponse("OK")
        else:
            print(form.errors)
    else:
        form = forms.EditForm().as_ul()
    return render(request, 'test/form_test001.html', {'form': form})


def edit_plan(request):
    # edit_form_factor = formset_factory(forms.EditForm, extra=2, max_num=1)
    # form = edit_form_factor(initial=[{'sid': 1, 'url': 'http://www.baidu.com'},
    #                                 {'sid': 2, 'url': 'http://www.youku.com'}],).as_p()
    if request.method == "POST":
        form = forms.EditExec(request.POST)
        sid = request.POST['sid']
        if form.is_valid():
            print(form.cleaned_data)
            a = models.PyScriptBaseInfoNew.objects.get(sid=sid)
            form.save(request.POST, a)
            return HttpResponse("OK")
        else:
            print(form.errors)
    else:
        form = forms.EditExec().as_ul()
    return render(request, 'test/form_test001.html', {'form': form})






