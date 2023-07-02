from allauth.account.adapter import DefaultAccountAdapter
from django.urls import reverse_lazy

class ProfileAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        resolved_url = super().get_login_redirect_url(request)
        user_obj = request.user
        profile_obj = user_obj.profile
        
        if user_obj.email == profile_obj.username:
            # mainアプリのurls.pyで誘導しているため、名前空間main:の指定がないと見つからない。
            resolved_url = reverse_lazy("main:profile-update", kwargs={"pk":profile_obj.pk})
        return resolved_url
