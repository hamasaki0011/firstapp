from django.urls import path
from . import views

app_name='record'
urlpatterns = [
    path('list/', views.RecordListView.as_view(), name='record_list'),
    path('detail/<int:pk>/', views.RecordDetailView.as_view(), name='record_detail'),
    path('update/<int:pk>/', views.RecordUpdateView.as_view(), name='record_update'),
    path('create/', views.RecordCreateView.as_view(), name='record_create'),
    path('delete/<int:pk>/', views.RecordDeleteView.as_view(), name='record_delete'),
    # Articles
    path('record/article/', views.RecordArticleView.as_view(), name='record_article'),
    path('record/python/', views.RecordPythonView.as_view(), name='record_python'),
    path('record/server/', views.RecordServerView.as_view(), name='record_server'),   
]