from django.shortcuts import render
# Create your views here.
from django.views import generic

# Top view, you can select a target site for remote monitoring
class IndexView(generic.TemplateView):
    template_name='main_index.html'


