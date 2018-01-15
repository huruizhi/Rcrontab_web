from django.contrib import admin
from rcrontab import models

# Register your models here.


class BaseInfo(admin.ModelAdmin):
    list_display = ('sid', 'parent_id', 'name', 'deploy_server', 'deploy_directory',
                    'function', 'exec_plan', 'exec_time', 'owner', 'is_stop')

    search_fields = ('sid', 'owner__owner',)
    list_filter = ('owner', 'deploy_server')
    list_editable = ('exec_time', 'owner', 'is_stop')


admin.site.register(models.PyScriptOwnerList)
admin.site.register(models.PyScriptBaseInfoNew, BaseInfo)
admin.site.register(models.PyScriptErrInfoDaliy)

