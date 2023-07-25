from django import forms
# 2023.7.24 from django.forms.fields import DateField
from django.utils.translation import gettext_lazy as _
# 2023.7.24 from django.utils.translation import gettext
from django.contrib.auth.forms import UserChangeForm
from .models import User, Profile
from accounts.models import Profile

class CustomAdminChangeForm(UserChangeForm):
#Profileクラスのフィールドを追記します
    username = forms.CharField(max_length=100)
    belongs = forms.CharField(max_length=100, required=False)
    phone_number = forms.IntegerField(required=False) 

    class Meta:
        model = User
        fields =('email', 'password', 'active', 'admin')

# Save initial value if Profileが存在する場合
    def __init__(self, *args, **kwargs):
        user_obj = kwargs["instance"]
        if hasattr(user_obj, "profile"):
            profile_obj = user_obj.profile
            self.base_fields["username"].initial = profile_obj.username
            self.base_fields["belongs"].initial = profile_obj.belongs
            self.base_fields["phone_number"].initial = profile_obj.phone_number
        super().__init__(*args, **kwargs)

# Define 保存機能
    def save(self, commit=True):
        user_obj = super().save(commit=False)
        username = self.cleaned_data.get("username")
        belongs = self.cleaned_data.get("belongs")
        phone_number = self.cleaned_data.get("phone_number")
        if hasattr(user_obj, "profile"):
            profile_obj = user_obj.profile
        else:
            profile_obj = Profile(user=user_obj)
        if username is not None:
            profile_obj.username = username
        if belongs is not None:
            profile_obj.belongs = belongs
        if phone_number is not None:
            profile_obj.phone_number = phone_number
        profile_obj.save()
        if commit:
            user_obj.save()
        return user_obj
    
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ["user"]
    # usernameフィールドのvalidation機能搭載
    def clean_username(self):
        username = self.cleaned_data.get("username")
        user_email = self.instance.user.email
        if username == user_email:
            raise forms.ValidationError("ユーザー名を変更してください")
        else:
            # 2023.2.27 これだけで十分？いつか見直す?
            if "@" in username and ".com" in username:
                raise forms.ValidationError("ユーザー名にEメールアドレスは使用できません")
            elif "@" in username and ".co.jp" in username:
                raise forms.ValidationError("ユーザー名にEメールアドレスは使用できません")                 
        return username
