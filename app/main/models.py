from django.db import models
# Create your models here.
from django.contrib.auth import get_user, get_user_model
import datetime
from datetime import datetime as dt
from django.utils import timezone

User=get_user_model()

# Location model =========================
class Location(models.Model):
    """ Location model
        監視サイトを定義 """
    class Meta:
        db_table='location'
        verbose_name='現場'
        verbose_name_plural='現場一覧'
    # author=models.ForeignKey('auth.User',on_delete=models.CASCADE)    
    # CASCADE指定で、userデータが削除されたとき、locationデータも削除される
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    name=models.CharField(verbose_name='現場', max_length=100)
    memo=models.CharField(verbose_name='メモ', max_length=500, default='',blank=True,null=True)
    created_date=models.DateTimeField(verbose_name='作成日', default=timezone.now)
    updated_date=models.DateTimeField(verbose_name='データ更新日', default=timezone.now)
    # updated_date=models.DateTimeField(verbose_name='更新日', blank=True, null=True)

    def __str__(self):
        return self.name
    
    # @staticmethod
    # def get_absolute_url(self):
    #     return reverse('main/main_index')

# Sensors model =========================
class Sensors(models.Model):
    """ Sensors model
        各センサーを定義 """
    class Meta:
        db_table='sensors'
        unique_together=(('site','device'),)
        verbose_name='センサー'
        verbose_name_plural='センサー一覧'
    
    site=models.ForeignKey(Location, verbose_name='現場', on_delete=models.PROTECT)
    device=models.CharField(verbose_name='センサー', max_length=127,default='',blank=True,null=True)
    note=models.CharField(verbose_name='補足', max_length=255,default='',blank=True,null=True)
    created_date=models.DateTimeField(verbose_name='登録日',default=timezone.now)
    updated_date=models.DateTimeField(verbose_name='更新日',default=timezone.now)
    
    def __str__(self):
        return self.device 
