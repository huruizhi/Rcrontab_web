from django.db import models

# Create your models here.


class ServerInfo(models.Model):
    is_alive = ((1, 'on_line'), (0, 'off_line'))
    IP = models.GenericIPAddressField(protocol='IPv4')
    name = models.CharField(max_length=100)
    uptime = models.DateTimeField(auto_now=True)
    status = models.IntegerField(choices=is_alive)

    def __str__(self):
        return 'IP:%s, is_alive:%s' %(self.IP, self.status)

