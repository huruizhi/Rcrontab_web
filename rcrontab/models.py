from django.db import models
# Create your models here.


class PyScriptBaseInfoNew(models.Model):
    exec_plan_choice = ((1, 'day'),
                        (2, 'month'),
                        (3, 'quarter'))

    is_jk_choice = ((0, '不监控'),
                    (1, '监控'))

    is_stop_choice = ((0, '执行'),
                      (1, '停止'))

    sid = models.AutoField(primary_key=True)
    parent_id = models.CharField(max_length=20, blank=True, null=True)
    name = models.CharField(verbose_name='脚本名称', max_length=50)
    deploy_server = models.CharField(verbose_name='部署服务器', max_length=20)
    deploy_directory = models.CharField(verbose_name='部署目录', max_length=50)
    function = models.CharField(verbose_name='程序功能', max_length=50, blank=True, null=True)
    exec_plan = models.IntegerField(verbose_name='执行计划', choices=exec_plan_choice, blank=True, null=True)
    exec_time = models.CharField(max_length=50, blank=True, null=True)
    owner = models.ForeignKey('PyScriptOwnerList', models.DO_NOTHING, db_column='owner')
    script_svn = models.CharField(max_length=100, blank=True, null=True)
    form_svn = models.CharField(max_length=100, blank=True, null=True)
    is_jk = models.IntegerField(default=0, choices=is_jk_choice)
    is_stop = models.IntegerField(default=0, choices=is_stop_choice)

    class Meta:
        db_table = 'py_script_base_info_new'

    def __str__(self):
        return "sid:%s server:%s script_name:%s " % (self.sid, self.deploy_server, self.name)


class PyScriptErrInfoDaliy(models.Model):
    start_time = models.DateTimeField()
    sid = models.ForeignKey('PyScriptBaseInfoNew', models.DO_NOTHING, db_column='sid')
    is_normal = models.IntegerField()
    err_info = models.CharField(max_length=255, blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'py_script_err_info_daliy'

    def __str__(self):
        return self.sid, self.start_time


class PyScriptOwnerList(models.Model):
    owner = models.CharField(verbose_name='所有者', max_length=10, primary_key=True)
    mail = models.EmailField()
    password = models.CharField(max_length=255, blank=True, null=True)
    vip = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'py_script_owner_list'

    def __str__(self):
        return self.owner



