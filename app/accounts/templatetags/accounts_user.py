from django import template
register = template.Library()

@register.filter
def user_display(user):
    user_display = "ログインしてください！"
    if user.is_authenticated:
        user_display = user.email
    return user_display