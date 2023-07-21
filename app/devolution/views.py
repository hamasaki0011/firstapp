from django.shortcuts import render
# Create your views here.
from django.shortcuts import redirect
from django.views import generic
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt

# Top-view of devolution, select configuration items

class IndexView(generic.TemplateView):
    template_name='devolution/index.html'

    def get(self, request, *args, **kwargs):
        context = {
            'message': "Hello World! from View!!",
        }
        return render(request, 'devolution/index.html', context)

    # @csrf_exempt
    def post(self, request, *args, **kwargs):
        context = {
            'message': "POST method OK!!",
        }
        return render(request, 'devolution/index.html', context)
    

    
