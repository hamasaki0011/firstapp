from django.db import models
from django.conf import settings
from django.utils import timezone
#import datetime

class Record(models.Model):
    class Meta:
        db_table='record'
        verbose_name='開発記録'
        verbose_name_plural='記録一覧'
        
    # author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title=models.CharField(verbose_name='標題',max_length=200)
    text=models.TextField(verbose_name='記事')
    created_date=models.DateTimeField(default=timezone.now)
    published_date=models.DateTimeField(blank=True, null=True)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.title
    
    #def __str__(self):
        # 管理画面で表示する時間に9時間加算する
    #    datetime_now = self.update_at + datetime.timedelta(hours=9)
    #    datetime_now = datetime_now.strftime("%Y/%m/%d %H:%M:%S")
    #    return f'{self.name} {datetime_now}'

