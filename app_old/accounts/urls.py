from .views import ProfileUpdateView
from django.urls import path

urlpatterns = [
    path("<int:pk>/", ProfileUpdateView.as_view(), name="profile-update"),
]