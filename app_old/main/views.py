from django.shortcuts import render
# Create your views here.
from django.views import generic
from django.urls import reverse_lazy
from .models import Location,Sensors
#from .models import ,Result
#from .forms import LocationForm,SensorsForm

# Top view, you can select a target site for remote monitoring
class IndexView(generic.TemplateView):
    template_name='main_index.html'


# -----------------------------------------------------------------
# Locations' list view 
class LocationListView(generic.ListView):
    template_name='main/location_list.html'
    model=Location
    
    def get_queryset(self):
        qs = Location.objects.all()
        # ユーザーがログインしていれば、リストを表示する
        # q = self.request.GET.get("search")
        # qs = Record.objects.search(query=q)
        # if self.request.user.is_authenticated:
        #     qs = qs.filter(Q(public=True)|Q(user=self.request.user))
        # else:
        #     qs = qs.filter(public=True)
        # the selected records are re-ordered  by "created_date"         
        qs = qs.order_by("created_date")[:7]
        return qs
# -----------------------------------------------------------------
# Sensors' list view 
class SensorsListView(generic.ListView):
    template_name='main/sensor_list.html'
    model=Sensors

    # user情報を取得する
    #23.6.30 def get_form_kwargs(self):
    #23.6.30     kwgs=super().get_form_kwargs()
    #23.6.30     kwgs["user"]=self.request.user
    #23.6.30     return kwgs
    
    # def get_queryset(self):
    #     qs = Sensors.objects.all()
    #     # ユーザーがログインしていれば、リストを表示する
    #     # q = self.request.GET.get("search")
    #     # qs = Record.objects.search(query=q)
    #     # if self.request.user.is_authenticated:
    #     #     qs = qs.filter(Q(public=True)|Q(user=self.request.user))
    #     # else:
    #     #     qs = qs.filter(public=True)
    #     # # the selected records are re-ordered  by "created_date"         
    #     # qs = qs.order_by("created_date")[:7]
    #     return qs
# -----------------------------------------------------------------

