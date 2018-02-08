import os
import configparser
from .models import Path, TablesInfo, PyScriptBaseInfoV2
from .forms import ScriptBaseInfoForm
from django.db.models import Model
from rcrontab.models import PyScriptOwnerList
from django.http import QueryDict
import time


class ReadProgramsInfo:

    def __init__(self, path):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_root = os.path.join(base_dir, 'media/project_conf/')
        self.project_conf = str(path.project_conf)
        conf_file = os.path.basename(self.project_conf)
        self.file = os.path.join(config_root, conf_file)

    def get_programs_info_list(self):
        conf = configparser.ConfigParser()
        conf.read(self.file, encoding='utf-8')
        for name in conf.sections():
            program_info = dict(conf.items(name))
            program_info['name'] = name
            self.handle_data_save(program_info)

    def handle_data_save(self, program_info):
        program_info_new = {}
        # --获取前置表和结果表
        if 'db_server' in program_info:
            db_server = program_info['db_server']
        else:
            db_server = ""

        if 'db_name' in program_info:
            db_name = program_info['db_name']
        else:
            db_name = ""

        result_tables_list = program_info['result_tables'].split(",")
        tables_info = self.handle_tables_info(program_info['name'], result_tables_list, db_server, db_name)
        result_tables = tables_info

        pre_tables = None
        if 'pre_tables' in program_info:
            if program_info['pre_tables']:
                result_tables_list = program_info['pre_tables'].split(",")
                tables_info = self.handle_tables_info(program_info['name'], result_tables_list, db_server, db_name)
                pre_tables = tables_info

        # --end 获取前置表和结果表-----
        # --外键 path------------
        program_info_new['path'] = Path.objects.get(project_conf=self.project_conf).id
        # ---------------------------------
        program_info_new["name"] = program_info['name']
        program_info_new["program_type"] = program_info['program_type']
        program_info_new["run_type"] = program_info['run_type']
        program_info_new["function"] = program_info['function']
        program_info_new["exec_plan"] = program_info['exec_plan']
        if 'exec_time' in program_info:
            program_info_new["exec_time"] = program_info['exec_time']
        if 'month' in program_info:
            program_info_new["exec_month"] = ",{month},".format(month=program_info['month'])
        if 'day' in program_info:
            program_info_new["exec_day"] = ",{day},".format(day=program_info['day'])
            # print('day:', program_info['day'])
        if 'times' in program_info:
            program_info_new["times"] = program_info['times']
        else:
            program_info_new['times'] = 1

        program_info_new['version'] = time.strftime("%Y-%m-%d")
        program_info_new["is_test"] = program_info['is_test']
        program_info_new["is_stop"] = 0
        # --获取owner
        program_info_new['owner'] = PyScriptOwnerList.objects.get(owner=program_info['owner'])
        qd = QueryDict(mutable=True)
        qd.update(program_info_new)
        for table_id in result_tables:
            qd.update({'result_tables': table_id})
        if pre_tables:
            for table_id in pre_tables:
                qd.update({'pre_tables': table_id})

        base_info = ScriptBaseInfoForm(qd)
        print("qd", qd)
        if base_info.is_valid():
            try:
                a = PyScriptBaseInfoV2.objects.get(name=program_info_new["name"])
                base_info = ScriptBaseInfoForm(qd, instance=a)
                base_info.save()
                string = "修改数据{name}".format(name=program_info_new["name"])
                print(string)
            except Exception as e:
                print(e)
                string = "新增数据{name}".format(name=program_info_new["name"])
                print(string)
                base_info.save()
        else:
            print(base_info.errors)

    @staticmethod
    def handle_tables_info(program_name, tables_list, db_server, db_name):
        tables_info_list = list()
        for table in tables_list:
            table_info = {}
            if ":" in table:
                table_info['db_server'] = table.split(":")[0]
                table = table.split(":")[1]
            else:
                table_info['db_server'] = db_server
            if "." in table:
                table_info['db_name'] = table.split(",")[0]
                table = table.split(",")[1]
            else:
                table_info['db_name'] = db_name
            table_info['table_name'] = table
            try:
                table = TablesInfo.objects.get(**table_info)
                tables_info_list.append(table.id)
            except TablesInfo.DoesNotExist:
                print("{program_name}: TablesInfo DoesNotExist:[{db_server}]{db_name}.{table_name}".format(
                    db_server=table_info['db_server'], db_name=table_info['db_name'],
                    table_name=table_info['table_name'], program_name=program_name
                ))
        return tables_info_list




