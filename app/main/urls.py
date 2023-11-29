from django.urls import path,include
from . import views
# from .views import LocationCreateFormView

app_name='main'
urlpatterns=[
    # 2023.11.29 Main view ~ top index view
    path('', views.IndexView.as_view(), name='index'),
    path('index/', views.IndexView.as_view(), name='index'),
    # /regist/user/'
    path('regist/user/', views.RegistUserView.as_view(), name='regist_user'),
    # user' profile update is handled in account application 
        
    # Main detail view
    path('detail/<int:pk>/', views.DetailView.as_view(), name='detail'),
    # Location list view
    path('location/list', views.LocationListView.as_view(), name='location_list'),
    # 2023.10.25 Is it ok to remove below
    # path('location/list/<int:pk>/', views.LocationListView.as_view(), name='location_list'),

    # Location detail view
    path('location/detail/<int:pk>/', views.LocationDetailView.as_view(), name='location_detail'),
    # Location create view
    path('location/create/', views.LocationCreateModelFormView.as_view(), name='location_create'),
    # path('location/create/<int:pk>/', views.LocationCreateModelFormView.as_view(), name='location_create'),
    # Location update view
    path('location/update/<int:pk>/', views.LocationUpdateModelFormView.as_view(), name='location_update'),    
    # Location delete view
    path('location/delete/<int:pk>/', views.LocationDeleteView.as_view(), name='location_delete'),
    # 2023.11.29 All of sensors' list view
    path('sensors/list/', views.SensorsListView.as_view(), name='sensors_list'),
    # Sensors create view
    path('sensors/create/', views.SensorsCreateModelFormView.as_view(), name='sensors_create'),
    path('sensors/create/<int:pk>/', views.SensorsCreateModelFormView.as_view(), name='sensors_create'),
    # Sensors update view
    path('sensors/update/<int:pk>/', views.SensorsUpdateModelFormView.as_view(), name='sensors_update'),
    # Sensors delete view
    path('sensors/delete/<int:pk>/', views.SensorsDeleteView.as_view(), name='sensors_delete'),
    
    # Sensors detail view
    path('sensors/detail/<int:pk>/', views.SensorsDetailView.as_view(), name='sensors_detail'),
    # Sensors update view
    
    path("profile/", include("accounts.urls")),
    
    # for file uploading at 2022/11/9
    path('upload/', views.Upload.as_view(), name='upload'),
    # path('upload/', views.upload, name='upload'),
    path('upload/complete/', views.UploadComplete.as_view(), name='upload_complete'),
    # path('download/', views.download, name='download'),
    
    path('ajax_number/', views.ajax_number, name='ajax_number'),
    
    # # 2022/12/14 Draw chart by using another chart tool
    # # path('sensor/device/list/<int:pk>/chart', views.update_chart, name='chart'),
    
    # path('sensor/device/detail/<int:pk>/', views.SensorDeviceDetailView.as_view(), name='sensor_device_detail'),
    # # Display location list view at 2022/11/28
    # path('sensor/location/list', views.LocationListView.as_view(), name='location_list'),
    # # Detail view with PK
    # # path('sensor/detail/<uuid:pk>/', views.SensorDetailView.as_view(), name='sensor_detail'),
    
    # # Update view with PK
    # # path('sensor/update/<uuid:pk>/', views.SensorUpdateView.as_view(), name='sensor_update'),
    
    # # 以下を追記(views.pyのcall_write_data()にデータを送信できるようにする)
    # path("ajax/", views.call_write_data, name="call_write_data"),
]