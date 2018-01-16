from django.db import models
from rcrontab import models as rmodels
# Create your models here.


class ServerInfo(models.Model):
    is_alive = ((1, 'on_line'), (0, 'off_line'))
    ip = models.GenericIPAddressField(protocol='IPv4')
    name = models.CharField(max_length=100)
    uptime = models.DateTimeField(auto_now=True)
    status = models.IntegerField(choices=is_alive, default=0)

    def __str__(self):
        return 'IP:%s, is_alive:%s' % (self.ip, self.status)


class Path(models.Model):
    server = models.ForeignKey('ServerInfo', on_delete=models.DO_NOTHING)
    path = models.CharField(max_length=200)

    def __str__(self):
        return "%s:%s" % (self.server, self.path)


class TablesInfo(models.Model):
    db_server = models.CharField(max_length=20)
    db_name = models.CharField(max_length=30)
    table_name = models.CharField(max_length=30)


class PyScriptBaseInfoNew(models.Model):
    exec_plan_choice = ((1, 'day'),
                        (2, 'month'),
                        (3, 'quarter'))
    is_stop_choice = ((0, '执行'),
                      (1, '停止'))
    sid = models.AutoField(primary_key=True)
    version = models.DateField()
    pre_tables = models.ManyToManyField('TablesInfo', related_name='son_program')
    result_tables = models.ManyToManyField('TablesInfo', related_name='father_program')
    name = models.CharField(verbose_name='脚本名称', max_length=50)
    deploy_directory = models.ForeignKey('Path', on_delete=models.DO_NOTHING)
    function = models.CharField(verbose_name='程序功能', max_length=50)
    exec_plan = models.IntegerField(verbose_name='执行计划', choices=exec_plan_choice, blank=True, null=True)
    exec_month = models.IntegerField(blank=True, null=True)
    exec_day = models.IntegerField(blank=True, null=True)
    exec_time = models.CharField(max_length=50, blank=True, null=True)
    owner = models.ForeignKey(rmodels.PyScriptOwnerList, models.DO_NOTHING, related_name='programs')
    is_stop = models.IntegerField(default=0, choices=is_stop_choice)

    def __str__(self):
        return "sid:%s server:%s script_name:%s " % (self.sid, self.deploy_directory, self.name)


class ResultLog(models.Model):
    script = models.ForeignKey('PyScriptBaseInfoNew', models.DO_NOTHING, related_name='result')
    version = models.DateField()
    start_time = models.DateTimeField()
    is_normal = models.IntegerField()
    err_info = models.CharField(max_length=255, blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.script, self.start_time



