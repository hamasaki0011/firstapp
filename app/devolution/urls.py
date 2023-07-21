from django.urls import path
from . import views

app_name='devolution'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    #path('detail/<int:pk>/', views.RecordDetailView.as_view(), name='record_detail'),
    #path('update/<int:pk>/', views.RecordUpdateView.as_view(), name='record_update'),
    #path('create/', views.RecordCreateView.as_view(), name='record_create'),
    #path('delete/<int:pk>/', views.RecordDeleteView.as_view(), name='record_delete'),
    
    # Articles
    # path('article/', views.RecordArticleView.as_view(), name='record_article'),
    # path('python/', views.RecordPythonView.as_view(), name='record_python'),
    # path('server/', views.RecordServerView.as_view(), name='record_server'),   
]