from django.shortcuts import render, redirect

from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy

from .models import Profile
from .forms import ProfileUpdateForm

class OwnProfileOnly(UserPassesTestMixin):
    def test_func(self):
        profile_obj = self.get_object()
        try:
            return profile_obj == self.request.user.profile 
        except:
            return False

# 2023.9.28 ↓今はまだ完成していない
class SuperUserOnly(UserPassesTestMixin):
    def test_func(self):
        profile_obj = self.get_object()
        print("profile_obj = ",profile_obj)
        
        try:
            return profile_obj == self.request.user.profile
        except:
            return False
    
    def handle_no_permission(self):
        # messages.error(self.request,"You can edit and delete only for your's.")
        pk=self.kwargs["pk"]
        print("pk = ",pk)
        return
        # return redirect("main:profile-update", pk=self.kwargs["pk"]) 

# class ProfileUpdateView(SuperUserOnly, UpdateView):
# class ProfileUpdateView(UpdateView):
class ProfileUpdateView(OwnProfileOnly, UpdateView):
    template_name = "profile-form.html"
    model = Profile
    form_class=ProfileUpdateForm
    success_url = reverse_lazy("main:main_index")
