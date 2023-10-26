from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.db.models.signals import post_save
from django.core.validators import RegexValidator

class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_staffuser(self, email, password):
        user = self.create_user(
            email,
            password=password,
        )
        user.staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(
            email,
            password=password,
        )
        user.staff = True
        user.admin = True
        user.save(using=self._db)
        return user
    
class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='Eメールアドレス',
        max_length=255,
        unique=True,
    )
    # company = models.CharField(max_length=100, blank=True, null=True, verbose_name="所属")
    active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False) 
    admin = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    
    # In order to link UserManager
    objects = UserManager()

    def __str__(self):             
        return self.email

    def has_perm(self, perm, obj=None):
        return self.admin

    def has_module_perms(self, app_label):
        return self.admin

    @property
    def is_staff(self):
        return self.staff

    @property
    def is_admin(self):
        return self.admin

    @property
    def is_active(self):
        return self.active
    
class Profile(models.Model):      
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=100, verbose_name="ユーザー名")
    belongs = models.CharField(max_length=100, blank=True, null=True, verbose_name="会社名")
    tel_number_regex = RegexValidator(regex=r'^[0-9]+$', message = ("電話番号は、'09012345678'のようにハイフンを省略して入力してください！"))
    tel_number = models.CharField(validators=[tel_number_regex], max_length=15, blank=True, null=True, verbose_name='緊急連絡電話番号')

    def __str__(self):
        return self.username
    
def post_user_created(sender, instance, created, **kwargs):
    if created:
        profile_obj = Profile(user=instance)
        profile_obj.username = instance.email
        profile_obj.save()

post_save.connect(post_user_created, sender=User)