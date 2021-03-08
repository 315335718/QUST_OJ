from django.db import models

class Server(models.Model):
    name = models.CharField("名字", max_length=30, unique=True)
    ip = models.CharField("IP", max_length=30)
    port = models.IntegerField("端口号")
    token = models.CharField("密钥", max_length=192)
    add_time = models.DateTimeField("创建时间", auto_now_add=True)
    enabled = models.BooleanField(default=False)
    concurrency = models.PositiveIntegerField("并发量", default=1)
    master = models.BooleanField("主节点", default=True)

    def __str__(self):
        return self.name + ' - ' + self.ip

    class Meta:
        ordering = ["add_time"]
        verbose_name_plural = '判题服务器'

    @property
    def http_address(self):
        return 'http://' + self.ip + ':' + str(self.port)