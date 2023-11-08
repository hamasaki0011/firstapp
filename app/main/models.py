from django.db import models
from django.contrib.auth import get_user, get_user_model
from django.contrib import admin
import datetime
from datetime import datetime as dt
from django.utils import timezone
# import uuid
# to embed a DB updating at 2022/11/10
#23.7.6 from django.urls import reverse

User=get_user_model()
# Location model
class Location(models.Model):
    """ Location model
        監視サイトを定義 """
    class Meta:
        db_table='location'
        verbose_name='現場'
        verbose_name_plural='現場一覧'
    # author=models.ForeignKey('auth.User',on_delete=models.CASCADE)    
    # CASCADE指定で、userデータが削除されたとき、locationデータも削除される
    # ↓この場合、Userが親モデル、Locationが子モデルになる
    # "on_delete"は、「子オブジェクトを持つ親オブジェクトが削除される際のアプリの動作を設定する引数」
    """_summary_ 2023.10.20
    子オブジェクトを削除したときに親オブジェクトを別のオブジェクトに切り替える
        from django.db import models
        from django.contrib.auth.models import User
        
        def get_first_user():
            users = User.objects.order_by('username')
            return users[0].pk
            
        class Comment(models.Model):
            contributor = models.ForeignKey(User, on_delete=models.SET(get_first_user))
        
        Returns:
            _type_: _description_
    """
    # 2023.10.23 name はprofileから参照できない？
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    name=models.CharField(verbose_name='現場', max_length=100)
    memo=models.CharField(verbose_name='メモ', max_length=500, default='',blank=True,null=True)
    created_date=models.DateTimeField(verbose_name='作成日', auto_now_add=True)
    updated_date=models.DateTimeField(verbose_name='更新日', blank=True, null=True)

    def __str__(self):
        return self.name
    
    # @staticmethod
    # def get_absolute_url(self):
    #     return reverse('main/index')

# Sensors model
class Sensors(models.Model):
    """ Sensors model
        各センサーを定義 """
    class Meta:
        db_table='sensors'
        # unique_together=(('site','device'),)
        verbose_name='センサー'
        verbose_name_plural='センサー一覧'
    
    site=models.ForeignKey(Location, verbose_name='現場', on_delete=models.CASCADE)
    device=models.CharField(verbose_name='センサー', max_length=127, default='',blank=True,null=True)
    note=models.CharField(verbose_name='補足', max_length=255,default='',blank=True,null=True)
    created_date=models.DateTimeField(verbose_name='作成日', auto_now_add=True)
    updated_date=models.DateTimeField(verbose_name='更新日', blank=True, null=True)

    def __str__(self):
        return self.device 

class Result(models.Model):
    """ Result model
        各ポイントの測定結果を定義 """
    class Meta:
        db_table='result'
        unique_together=(('point','measured_date',),)
        verbose_name='測定結果'
        verbose_name_plural='測定結果一覧'
    place=models.ForeignKey(Location, verbose_name='場所', on_delete=models.CASCADE, default = None)
    point=models.ForeignKey(Sensors, verbose_name='センサー', on_delete=models.CASCADE, default = None)
    measured_date=models.DateTimeField(verbose_name='測定日時', default=dt.strptime('2001-01-01 00:00:00','%Y-%m-%d %H:%M:%S'))
    measured_value=models.FloatField(verbose_name='測定値', default=0.0, blank=True, null=True)
    created_date=models.DateTimeField(verbose_name='作成日', auto_now_add=True)
    updated_date=models.DateTimeField(verbose_name='更新日', blank=True, null=True)


    def __str__(self):
        res: str
        if self.point.device is not None:
            res = self.point.device + str(self.measured_value)+ " 日付・時間: " +  str(self.measured_date)
        else:
            res = str(self.measured_value)+ " 日付・時間: " +  str(self.measured_date)         
        # return self.point.device + str(self.measured_value)+ " 日付・時間: " +  str(self.measured_date)
        return res  

    @admin.display(
        boolean=True,
        ordering = 'measured_date',
        description='最新?'
    )

    def was_measured_recently(self):
        now=timezone.now()
        return now-datetime.timedelta(days=1)<=self.measured_date<=now
