from django.db import models
from rcrontab import models as rmodels
# Create your models here.


class ServerInfo(models.Model):
    is_alive = ((1, 'on_line'), (0, 'off_line'))
    ip = models.GenericIPAddressField(protocol='IPv4')
    port = models.IntegerField(default=33541)
    name = models.CharField(max_length=100)
    uptime = models.DateTimeField(auto_now=True)
    status = models.IntegerField(choices=is_alive, default=0)

    def __str__(self):
        return 'IP:%s, is_alive:%s' % (self.ip, self.status)

    class Meta:
        db_table = 'py_script_server_info_v2'


class Path(models.Model):
    server = models.ForeignKey('ServerInfo', on_delete=models.DO_NOTHING)
    path = models.CharField(max_length=200)
    project = models.CharField(verbose_name='项目名称', max_length=50)
    project_conf = models.FileField(upload_to='project_conf/', blank=True, null=True)
    project_package = models.FileField(upload_to='project_package/', blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    def __str__(self):
        return "project:(%s),Server:(%s),Path:%s" % (self.server, self.project, self.path)

    class Meta:
        db_table = 'py_script_programs_path'
        unique_together = ('server', 'path', 'project', 'project_conf')


class TablesInfo(models.Model):
    db = (('db_ali', 'db_阿里云'), ('db_151', 'db_151'), ('db_153', 'db_153'))
    db_server = models.CharField(max_length=20, choices=db)
    db_name = models.CharField(max_length=30)
    table_name = models.CharField(max_length=100)

    def __str__(self):
        return "%s:%s.%s" % (self.db_server, self.db_name, self.table_name)

    class Meta:
        db_table = 'py_script_tables_info'
        unique_together = ('db_server', 'db_name', 'table_name')


class PyScriptBaseInfoV2(models.Model):
    exec_plan_choice = ((1, 'day'),
                        (2, 'month'),
                        (3, 'quarter'))

    is_stop_choice = ((0, '执行'),
                      (1, '停止'))

    is_test = ((1, '测试'), (0, '正式'),)

    run_type = ((0, '调用api'),
                (1, '调用程序'))

    program_type = ((0, '抓取'),
                    (1, '计算'),
                    (2, '其他'))

    sid = models.AutoField(primary_key=True)
    name = models.CharField(verbose_name='名称', max_length=50)
    program_type = models.IntegerField(verbose_name='程序类型', choices=program_type)
    version = models.DateField(blank=True, null=True)
    run_type = models.SmallIntegerField(choices=run_type, default=0)
    pre_tables = models.ManyToManyField('TablesInfo', related_name='son_program', blank=True )
    result_tables = models.ManyToManyField('TablesInfo', related_name='father_program')
    path = models.ForeignKey('Path', on_delete=models.DO_NOTHING, related_name='program')
    function = models.TextField(verbose_name='程序功能', max_length=50)
    exec_plan = models.IntegerField(verbose_name='执行计划', choices=exec_plan_choice)
    exec_month = models.CharField(max_length=30, blank=True, null=True)
    exec_day = models.CharField(max_length=30, blank=True, null=True)
    exec_time = models.CharField(max_length=50, blank=True, null=True)
    owner = models.ForeignKey(rmodels.PyScriptOwnerList, models.DO_NOTHING, related_name='programs')
    times = models.IntegerField(default=1)
    is_stop = models.IntegerField(default=0, choices=is_stop_choice)
    is_test = models.IntegerField(default=0, choices=is_test)

    def __str__(self):
        return "sid:%s server:%s script_name:%s " % (self.sid, self.path, self.name)

    class Meta:
        db_table = 'py_script_base_info_v2'
        unique_together = ('name', )


# class PyScriptBaseExtraInfoV2(models.Model):
#     insert_way_choice = ((0, 'ignore'), (1, 'replace'))
#     sid = models.OneToOneField('PyScriptBaseInfoV2',
#                                on_delete=models.DO_NOTHING, related_name='extra_info', db_column='sid')
#     insert_way = models.IntegerField(choices=insert_way_choice)


class ResultLog(models.Model):
    event_type_list = ((0, '执行调度'), (1, '开始执行'), (2, '正常结束'), (3, '异常终止'),
                       (4, '质控正常'), (5, '质控异常'))
    script = models.ForeignKey('PyScriptBaseInfoV2', models.DO_NOTHING, related_name='result', db_column='sid')
    version = models.DateField()
    event_time = models.DateTimeField()
    subversion = models.DateTimeField(blank=True, null=True)
    event_type = models.IntegerField(choices=event_type_list)
    extra_info = models.TextField(blank=True, null=True)
    flag = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.script, self.version

    class Meta:
        db_table = 'py_script_result_log'



