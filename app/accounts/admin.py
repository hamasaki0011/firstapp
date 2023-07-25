from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User,Profile
from .forms import CustomAdminChangeForm

class UserAdmin(BaseUserAdmin):
    form = CustomAdminChangeForm
    
    list_display = (
        "email",
        "active",
        "staff",
        "admin",
    )
    list_filter = (
        "admin",
        "active",
    )
    filter_horizontal = ()
    ordering = ("email",)
    search_fields = ('email',)

    # Set 編集フォーム
    fieldsets = (
        # ("見出し", {"fields": (フィールド名1, ...)}),
        (None, {'fields': ('email', 'password')}),
        # プロフィールフォームを追加
        ('プロフィール', {'fields':(
            'username',
            'belongs',
            'phone_number',
        )}),
        ('Permissions', {'fields': ('staff','admin',)}),
    )

    # Set 新規登録フォーム
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}
        ),
    )
    
admin.site.register(User, UserAdmin)
# admin.site.register(Profile)
