from .views import ProfileUpdateView
# from .views import ProfileEditView

from django.urls import path

urlpatterns = [
    path("<int:pk>/", ProfileUpdateView.as_view(), name="profile-update"),
    # path("<int:pk>/", ProfileEditView.as_view(), name="profile-edit"),
]