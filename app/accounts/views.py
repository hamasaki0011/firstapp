from django.shortcuts import render, redirect

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy

from .models import Profile
from .forms import ProfileUpdateForm

# --- Does permit only for owner --------------------------------------------------------------
class OwnProfileOnly(UserPassesTestMixin):
    def test_func(self):
        profile_obj = self.get_object() # type: ignore
        try:
            return profile_obj == self.request.user.profile  # type: ignore
        except:
            return False

# 2023.9.28 ↓今はまだ完成していない
class SuperUserOnly(UserPassesTestMixin):
    login_user: str
    
    def test_func(self):
        profile_obj = self.get_object() # type: ignore
        login_user = self.request.user # type: ignore
        # print("login_user = ",login_user)
        try:
            return profile_obj == self.request.user.profile # type: ignore
        except:
            return False
    
    def handle_no_permission(self,login_user):
        # messages.error(self.request,"You can edit and delete only for your's.")
        pk=self.kwargs["pk"] # type: ignore
        # print("pk = ",pk)
        if login_user.admin:
            return redirect("main:profile-update", pk=self.kwargs["pk"]) # type: ignore
            
        else:
            return

# --- Update user' profile view--------------------------------------------------------------         
# class ProfileUpdateView(SuperUserOnly, UpdateView):
class ProfileUpdateView(LoginRequiredMixin, UpdateView):
# class ProfileUpdateView(OwnProfileOnly, UpdateView):
    template_name = "profile-form.html"
    model = Profile
    # model = User
    form_class=ProfileUpdateForm
    success_url = reverse_lazy("main:index")    

