from django.urls import path,include
from . import views
# from .views import LocationCreateFormView

app_name='main'
urlpatterns=[
    # Top index view
    path('', views.IndexView.as_view(), name='main_index'),
    # path('user/', views.user_view, name='main_user'),
    path('other/', views.other_view, name='main_other'),
    # Main detail view
    path('detail/<int:pk>/', views.MainDetailView.as_view(), name='main_detail'),
    path('user/', views.MainDetailView.as_view(), name='main_user'),
    # Location list view
    path('location/list', views.LocationListView.as_view(), name='location_list'),
    # Location list view
    # path('location/select', views.LocationSelectView.as_view(), name='location_select'),
    # Detail view
    path('location/detail/<int:pk>/', views.LocationDetailView.as_view(), name='location_detail'),
    # Location create view
    path('location/create/', views.LocationCreateModelFormView.as_view(), name='location_create'),
    # Location update view
    path('location/update/<int:pk>/', views.LocationUpdateModelFormView.as_view(), name='location_update'),    
    # Location delete view
    path('location/delete/<int:pk>/', views.LocationDeleteView.as_view(), name='location_delete'),
    
    # Sensors list view
    path('sensors/list', views.SensorsListView.as_view(), name='sensors_list'),
    # Sensors detail view
    path('sensors/detail/<int:pk>/', views.SensorsDetailView.as_view(), name='sensors_detail'),
    # Sensors create view
    path('sensors/create/', views.SensorsCreateModelFormView.as_view(), name='sensors_create'),
    # Sensors update view
    path('sensors/update/<int:pk>/', views.SensorsUpdateModelFormView.as_view(), name='sensors_update'),
    # Sensor's delete view
    path('sensors/delete/<int:pk>/', views.SensorsDeleteView.as_view(), name='sensors_delete'),
    
    path("profile/", include("accounts.urls")),
    
    # for file uploading at 2022/11/9
    path('upload/', views.Upload.as_view(), name='upload'),
    # path('upload/', views.upload, name='upload'),
    path('upload/complete/', views.UploadComplete.as_view(), name='upload_complete'),
    # path('upload/complete/', views.upload_complete, name='upload_complete'),
    # path('load/', views.Load.as_view(), name='load'),
    # path('download/', views.download, name='download'),
    
    path('ajax_number/', views.ajax_number, name='ajax_number'),
    
    # # Display path root for all sensor devices belong in each site/location
    # path('sensor/device/list/<int:pk>/', views.SensorDeviceListView.as_view(), name='sensor_device_list'),
    # # 2022/12/14 Draw chart by using another chart tool
    # # path('sensor/device/list/<int:pk>/chart', views.update_chart, name='chart'),
    
    # # Display all sensor devices
    # path('sensor/list', views.SensorListView.as_view(), name='sensor_list'),
    # # 2022/12/2 SensorDeviceDetail detail contents of all sensor devices list
    # path('sensor/<int:pk>/', views.DetailView.as_view(), name='detail'),
    
    # path('sensor/device/detail/<int:pk>/', views.SensorDeviceDetailView.as_view(), name='sensor_device_detail'),
    # # Display location list view at 2022/11/28
    # path('sensor/location/list', views.LocationListView.as_view(), name='location_list'),
    # # Detail view with PK
    # # path('sensor/detail/<uuid:pk>/', views.SensorDetailView.as_view(), name='sensor_detail'),
    # path('sensor/location/detail/<int:pk>/', views.LocationDetailView.as_view(), name='location_detail'),
    # # path('sensor/detail/<int:pk>/', views.SensorDeviceDetailView.as_view(), name='sensor_device_detail'),
    # # Create view / Setting view
    # # path('sensor/setting/', views.SensorSettingView.as_view(), name='sensor_setting'),
    # path('sensor/location/setting/', views.LocationSettingView.as_view(), name='location_setting'),
 
    # # Create complete / Setting done
    # path('sensor/setting/done/', views.SensorSettingDoneView.as_view(), name='sensor_setting_done'),
    # path('sensor/location/setting/done/', views.LocationSettingDoneView.as_view(), name='location_setting_done'),
 
    # # Update view with PK
    # # path('sensor/update/<uuid:pk>/', views.SensorUpdateView.as_view(), name='sensor_update'),
    # # path('sensor/location/setting/<int:pk>/', views.LocationSettingView.as_view(), name='location_setting'),
    # path('sensor/location/update/<int:pk>/', views.LocationUpdateView.as_view(), name='location_update'),
    
    # # Delete view with PK
    # # path('sensor/delete/<uuid:pk>/', views.SensorDeleteView.as_view(), name='sensor_delete'),
    # path('sensor/location/delete/<int:pk>/', views.LocationDeleteView.as_view(), name='location_delete'),
    
    # # 以下を追記(views.pyのcall_write_data()にデータを送信できるようにする)
    # path("ajax/", views.call_write_data, name="call_write_data"),
]