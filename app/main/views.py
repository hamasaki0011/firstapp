from django.shortcuts import render, redirect
from django.views import generic
from django.urls import reverse_lazy
from .models import Location,Sensors,Result
from .forms import LocationForm,SensorsForm
from accounts.models import User
# ページへのアクセスをログインユーザーのみに制限する
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin
from django.contrib.auth import get_user, get_user_model
from django.contrib import messages
from django.utils import timezone
import datetime
# Chart drawing with Plotly
import os
import logging
from main import addCsv
from .forms import FileUploadForm
# from .forms import UploadFileForm
import plotly.graph_objects as go
from plotly.subplots import make_subplots
# ajax trial
from django.conf import settings
from django.http import JsonResponse

# import dateutil
# from dateutil import tz
# from dateutil.relativedelta import relativedelta
# from django.http import Http404
# from django.shortcuts import get_object_or_404
# from django.http import HttpResponseRedirect
# from .application import data_rw
# for CSV file uploading
# import csv, io
# from django.http import HttpResponse 
# from sensor.forms import FileUploadForm
# import numpy as np
# from sensor import writeCsv
# embedded watchdog module
# import sys
# import time
# from watchdog.observers import Observer
# from watchdog.events import RegexMatchingEventHandler
# from watchdog.events import LoggingEventHandler

# directory to store the uploading files
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), 'static/uploads/')
# Define debug log-file
logger = logging.getLogger('development')
# logger = logging.getLogger(__name__)

# Color palette for chart drawing which prepared 10 colors
COLOR=['darkturquoise','orange','green','red','blue','brown','violet','magenta','gray','black']
# COMPANY={'saga':'A株式会社','kumamoto':'株式会社B','fukuoka':'C株式会社',}

class OwnerOnly(UserPassesTestMixin):
    def test_func(self):
        location_instance = self.get_object()
        return location_instance.user == self.request.user
    
    def handle_no_permission(self):
        messages.error(self.request,"You can edit and delete only for your's.")
        return redirect("main:location_detail", pk=self.kwargs["pk"]) 
# -----------------------------------------------------------------
def other_view(request):
    
    # user=request.user    
    users=User.objects.exclude(email=request.user)
    context={
        'users':users
    }
    return render(request, 'main/main_other.html',context)
# -----------------------------------------------------------------
# Top view, you can select a target site for remote monitoring
class IndexView(LoginRequiredMixin,generic.ListView):
    template_name='main/main_index.html'
    model=Location
    
    def get_queryset(self):
        # ここに来た時点でuser情報は取得できている @2023.3.24
        user=self.request.user
        # ログインユーザーに許可されたQuery情報を渡す
        if user.is_authenticated:
            if('fujico@kfjc.co.jp' in user.email):
                locations = Location.objects.all()
            else:
                locations = Location.objects.filter(name=user.profile.belongs)
        return locations

    # Get user infromation
    # def get_form_kwargs(self):
    #     kwgs=super().get_form_kwargs()
    #     kwgs["user"]=self.request.user    
    #     return kwgs
    # user=AnonymousUser or authenticatedUser
# -----------------------------------------------------------------
# Chart drawing function
def line_charts(x_data,y_data,start,points,legend):
    # fig=go.Figure()    
    fig = make_subplots(
        # rows=2, cols=1,
        rows=1, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.2,
        specs=[[{"secondary_y": True}]]
        # specs=[[{"type": "scatter"}]]
        # specs=[[{"type": "scatter"}], [{"type": "scatter"}]]
    )
    
    fig.update_layout(
        title='直近30分(*30)間のデータ推移',
        grid=dict(
            rows=1,
            columns=1,
            pattern='independent',
            roworder='top to bottom',
        ),
         
        xaxis=dict(
            title='時間経過[minutes]',
            showline=True,
            showgrid=True,
            zeroline=True,
            showticklabels=True,
            linecolor='rgb(204,204,204)',
            linewidth=2,
            ticks='outside',
            tickcolor='rgb(204,204,204)',
            tickwidth=2,
            ticklen=5,
            tickfont=dict(
                family='Arial',
                size=12,
                color='rgb(82,82,82)',
            )  
        ),
        
        yaxis=dict(
            title='温度[℃]',
            showline=True,
            showgrid=True,
            zeroline=False,
            showticklabels=True,
            linecolor='rgb(204,204,204)',
            linewidth=2,
            autoshift=True,
            ticks='outside',
            tickcolor='rgb(204,204,204)',
            tickwidth=2,
            ticklen=5,
            tickfont=dict(
                family='Arial',
                size=12,
                color='rgb(82,82,82)',
            )  
        ),
        
        # xaxis2=dict(
        #     title='時間経過[minutes]',
        #     showline=True,
        #     showgrid=True,
        #     zeroline=True,
        #     showticklabels=True,
        #     linecolor='rgb(204,204,204)',
        #     linewidth=2,
        #     ticks='outside',
        #     tickcolor='rgb(204,204,204)',
        #     tickwidth=2,
        #     ticklen=5,
        #     tickfont=dict(
        #         family='Arial',
        #         size=12,
        #         color='rgb(82,82,82)',
        #     )  
        # ),
        
        yaxis2=dict(
            title='圧力[Pa]',
            showline=True,
            showgrid=True,
            zeroline=False,
            showticklabels=True,
            linecolor='rgb(204,204,204)',
            linewidth=2,
            autoshift=True,
            ticks='outside',
            tickcolor='rgb(204,204,204)',
            tickwidth=2,
            ticklen=5,
            tickfont=dict(
                family='Arial',
                size=12,
                color='rgb(82,82,82)',
            )  
        ),        
        
        hovermode='closest',
        autosize=True,
        showlegend=True,
        legend=dict(
            x=0.02,
            y=1.16,
            xanchor='left',
            yanchor='top',
            orientation='h',
        )
    )
    """_summary_ グラフ描画
        左軸：温度[℃]、マーカー● と 右軸：温度以外(以下のところ圧力[Pa]を準備)、マーカー■の2軸描画
        色分けが9色のみ、場合分けで20個まで描画可能
        Returns:
        _type_: _description_
    """
    for i in range(0,points):
        if(i<=9):
            # 温度 [℃]軸
            if('[℃]' in str(legend[i])):
                fig.add_trace(
                    go.Scatter(
                        x=x_data,
                        y=y_data[start-1+i],   
                        name=str(legend[i]),        # legend table
                        mode='lines+markers',
                        connectgaps=True,
                        line=dict(
                            color=COLOR[i],         # color palette
                            width=2,
                        ),
                        line_dash='solid',          # 
                        marker=dict(
                            symbol='circle',
                            color=COLOR[i],         # color palette
                            size=10,
                        ),   
                    )
                )
            # 圧力軸
            else:
                fig.add_trace(
                    go.Scatter(
                        x=x_data,
                        y=y_data[start-1+i],
                        # name='trace'+str(i+1),      
                        name='右軸: '+str(legend[i]),   # legend table
                        mode='lines+markers',
                        connectgaps=True,
                        line=dict(
                            color=COLOR[i],             # color pallete
                            width=2,
                        ),
                        line_dash='solid',
                        marker=dict(
                            symbol='square',
                            color=COLOR[i],             # color pallet
                            size=10,
                        ),   
                    ),
                    secondary_y=True,
                )                    
        elif(i<=19):
            # 温度軸
            if('[℃]' in str(legend[i])):
                fig.add_trace(
                    go.Scatter(
                        x=x_data,
                        y=y_data[start-1+i],
                        name=str(legend[i]),        # legend table
                        mode='lines+markers',
                        connectgaps=True,
                        line=dict(
                        color=COLOR[i-10],      # color palette
                            width=2,
                        ),
                        line_dash="dot",
                        marker=dict(
                            symbol='circle',
                            color=COLOR[i-10],      # color palette
                            size=10,
                        ),
                    )
                )
            # 圧力軸
            else:
                fig.add_trace(
                    go.Scatter(
                        x=x_data,
                        y=y_data[start-1+i],
                        # name='trace'+str(i+1),      
                        name='右軸: '+str(legend[i]),        # legend table
                        mode='lines+markers',
                        connectgaps=True,
                        line=dict(
                            color=COLOR[i-10],      # color palette
                            width=2,
                            ),
                        line_dash="dot",
                        marker=dict(
                            symbol='square',
                            color=COLOR[i-10],      # color palette
                            size=10,
                        ),
                    ),
                    secondary_y=True,
                )          
    return fig.to_html(include_plotlyjs='cdn',full_html=False).encode().decode('unicode-escape')
# -----------------------------------------------------------------
# Main detail view, List view for sensor devices at each site 
class MainDetailView(generic.ListView):
    template_name='main/main_detail.html'
    model=Result

    def get(self, request, *args, **kwargs):
        # Get 'pk' which indicates the monitoring site information
        id=Location.objects.get(pk=self.kwargs['pk'])
        # Get the name of monitoring site
        location=Location.objects.get(pk=id.pk)
        # Get queryset for Measured_data, result
        
        # Horizontal point's number
        latest=30
        # Get sensor device point's number
        sensor_list=Sensors.objects.filter(site_id=id.pk)
        # Get the number of sensor device point's 
        pointNum=len(sensor_list)
        # Get the smallest number of the point_id
        # 23.7.4 change 'sensor.id' to 'id' for django' revision up 3.2.17 to 4.2.3
        #startPoint=sensor_list.order_by('sensors.id').first().id
        startPoint=sensor_list.order_by('id').first().id
        
        # Generate a graph data from sensor's measured_value   
        # Generate the table data including the device name and the most recent measured_data
        # recent_update=datetime.date(2023,2,27)
        # TD=9    # time deffernce
        # today = datetime.datetime.now() + datetime.timedelta(hours=TD)
        # 注意：最終的にはtimedeltaで1分前のデータを表示するように調整する
        today = datetime.datetime.now()
        start_date=today-datetime.timedelta(hours=4)
        results=Result.objects.all().filter(place_id=id.pk, created_date__range=(start_date,today))
        # results=Result.objects.all().filter(place_id=id.pk)
        if results.first() is None:
            message="最新の測定データが取得できません"
        else:
            message="1分毎に更新(工事中は30分毎)"     
        
        # Prepare the Legend' array    
        legend=[]
        # First of drawing the chart, prepare the legend's list as legend
        for sensor in sensor_list:
            legend.append(sensor.device)
        # Prepare the xAxis data array            
        xdata=[]
        # Create the x_axis data
        n=int(latest)
        while(n>=0):
            xdata.append(-n)
            n-=1

        # Create y_Axis data
        #2023.5.8 try it lator y_tmp=[[]*latest for j in range(6)]
        y_tmp=[[] for j in range(latest)]
        """ this means followings; 
            device0 : y_tmp[0][0] ~ y_tmp[0][29]
            device1 : y_tmp[1][0] ~ y_tmp[1][29]
            ...
            device5 : y_tmp[5][0] ~ y_tmp[1][29]
        """
        # Prepare the array to memory the y_axis data as ydata[][]
        ydata=[[] for j in range(latest)]        
        data_list=Result.objects.all().filter(place_id=id.pk) 

        for i in range(pointNum):
            # 課題：センサー番号がシリーズであることが前提のquery設定
            y_tmp[startPoint-1+i]=data_list.filter(point_id=startPoint+i).order_by('measured_date')[:latest]

            for data in y_tmp[startPoint-1+i]:
                ydata[startPoint-1+i].append(data.measured_value)
        
            """
            'if' and 'for' Statements both do not form scopes in Python. 
            Therefore, the variable if inside the sentence is the same as the variable outside.
            Variables, 'start_at' and 'd_tmp' lator appeared are effective both inside and outside.
            """
        
        context={
            # for confirmation
            # For the latest measured value table 
            "location":location,
            "results":results,
            "message":message,
            # For chart drawing
            "plot":line_charts(xdata,ydata,startPoint,pointNum,legend), 
        }
        return render(request, "main/main_detail.html", context)
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
# Each location's detail information view
class LocationDetailView(generic.DetailView):
    template_name='main/location_detail.html'
    model=Location
    
    # def get_object(self):
    #     return super().get_object()
# -----------------------------------------------------------------
# Create a new location's information view
class LocationCreateModelFormView(LoginRequiredMixin,generic.CreateView):
    template_name = "main/location_form.html"
    form_class = LocationForm
    success_url = reverse_lazy("main:location_list")
    
    # user情報を取得する
    def get_form_kwargs(self):
        kwgs=super().get_form_kwargs()
        kwgs["user"]=self.request.user
        return kwgs
    
    # このviewではデータの取り込み、保存も一括して行われるので以下はいらない。  
    # # Received and saved data 
    # def form_valid(self, form):
    #     data = form.cleaned_data    # 入力したデータを辞書型で取り出す
    #     obj=Location(**data)        # 入力したデータでオブジェクトを作成し保存する
    #     obj.save()
    #     return super().form_valid(form)
"""
Another way to create
class LocationCreateView(LoginRequiredMixin,generic.CreateView):
    template_name='main/location_create.html'
    # model=Location
    form_class=LocationForm
    success_url=reverse_lazy('main:location_list')
    
    # Received and saved data 
    def form_valid(self, form):
        location = form.save(commit=False)
        # location.author = self.request.user
        location.crteated_date = timezone.now()
        location.updated_date = timezone.now()
        location.save()
        return super().form_valid(form)
"""
# -----------------------------------------------------------------
# Update location's information
class LocationUpdateModelFormView(OwnerOnly,generic.UpdateView):
    template_name = "main/location_form.html"
    form_class = LocationForm
    success_url = reverse_lazy("main:location_list")
    # Following get_querryset() is mondatly requrered.
    # in case of using a FormView
    def get_queryset(self):
        qs = Location.objects.all()
        return qs
    # Update updated_date
    def form_valid(self, form):
        location = form.save(commit=False)
        location.updated_date = timezone.now()
        location.save()
        return super().form_valid(form)
"""
Another way
class LocationUpdateView(LoginRequiredMixin,generic.UpdateView):
class LocationUpdateView(generic.UpdateView):
    template_name = 'main/location_update.html'
    model = Location
    # form_class = LocationForm
    fields = ('name', 'memo',)
    success_url = reverse_lazy('main:location_list')
 
    def form_valid(self, form):
        location = form.save(commit=False)
        # location.author = self.request.user
        location.updated_date = timezone.now()
        location.save()
        return super().form_valid(form)
"""
# -----------------------------------------------------------------
# Delete location information
class LocationDeleteView(OwnerOnly,generic.DeleteView):
    template_name = 'main/location_delete.html'
    model = Location
    # form_class=LocationForm
    success_url = reverse_lazy('main:location_list')
# -----------------------------------------------------------------
# Sensors' list view 
class SensorsListView(generic.ListView):
    template_name='main/sensor_list.html'
    model=Sensors

    # user情報を取得する
    def get_form_kwargs(self):
        kwgs=super().get_form_kwargs()
        kwgs["user"]=self.request.user
        return kwgs
    
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
# Each Sensors's detail information view
class SensorsDetailView(generic.DetailView):
    template_name='main/sensors_detail.html'
    model=Sensors
# class SensorDeviceDetailView(generic.DetailView):
#     def get(self,request, *args,**kwargs):
#         id=SensorDevice.objects.get(pk=self.kwargs['pk'])
#         site=SensorDevice.objects.get(id=id.pk)
#         data=MeasureData.objects.filter(point_id=id.pk)
#         # # as following if you use "filter", you can get all contents of DB
#         # memo=SensorDevice.objects.get(pk=sensor_device_id) 
#         context={
#             "id":id,
#             "site":site,
#             "data":data
#         }
#         return render(request, 'sensor/detail.html', context)
#     #  model=SensorDevice
#     #  template_name= 'sensor/detail.html'    

# # class SensorDeviceDetailView(generic.DetailView):
# #     template_name='sensor/sensor_device_detail.html'
# #     model=SensorDevice
# -----------------------------------------------------------------
# Create a new Sensor place information view
class SensorsCreateModelFormView(generic.CreateView):
    template_name = "main/sensors_create.html"
    form_class = SensorsForm
    success_url = reverse_lazy("main:sensors_list")
    
    # place情報を取得する
    # def get_form_kwargs(self):
    #     kwgs=super().get_form_kwargs()
    #     kwgs["place"]=self.place
    #     return kwgs
    
    # このviewではデータの取り込み、保存も一括して行われるので以下はいらない。  
    # # Received and saved data 
    # def form_valid(self, form):
    #     data = form.cleaned_data    # 入力したデータを辞書型で取り出す
    #     obj=Location(**data)        # 入力したデータでオブジェクトを作成し保存する
    #     obj.save()
    #     return super().form_valid(form)
"""Another way to create
# class SensorsCreateView(LoginRequiredMixin,generic.CreateView):
class SensorsCreateView(generic.CreateView):
    template_name='main/sensors_create.html'
    model=Sensors
    # form_class=LocationForm
    success_url=reverse_lazy('main:sensors_list')
    
    # Received and saved data 
    def form_valid(self, form):
        sensors = form.save(commit=False)
        # sensors.author = self.request.user
        sensors.crteated_date = timezone.now()
        sensors.updated_date = timezone.now()
        sensors.save()
        return super().form_valid(form)
"""
# -----------------------------------------------------------------
# Update location's information
class SensorsUpdateModelFormView(generic.UpdateView):
    template_name = "main/sensors_update.html"
    form_class = SensorsForm
    success_url = reverse_lazy("main:sensors_list")
    
    # Following get_querryset() is mondatly requrered.
    # in order to get place data
    def get_queryset(self):
        return Sensors.objects.all()
    # Update updated_date
    def form_valid(self, form):
        sensors = form.save(commit=False)
        sensors.updated_date = timezone.now()
        sensors.save()
        return super().form_valid(form)
"""
Another way
class LocationUpdateView(LoginRequiredMixin,generic.UpdateView):
class LocationUpdateView(generic.UpdateView):
    template_name = 'main/location_update.html'
    model = Location
    # form_class = LocationForm
    fields = ('name', 'memo',)
    success_url = reverse_lazy('main:location_list')
 
    def form_valid(self, form):
        location = form.save(commit=False)
        # location.author = self.request.user
        location.updated_date = timezone.now()
        location.save()
        return super().form_valid(form)
"""
# -----------------------------------------------------------------
# Delete Sensor information
class SensorsDeleteView(generic.DeleteView):
    template_name = 'main/sensors_delete.html'
    model = Sensors
    # form_class=LocationForm
    success_url = reverse_lazy('main:sensors_list')
# -----------------------------------------------------------------
# 2022/11/8 CSV file uplaoding
# it does need as reverse url path, does not it need? at 2022/11/11  
# def index(req):
#     return render(req, 'main/index.html')

# class DetailView(generic.DetailView):
#     def get(self,request, *args,**kwargs):
#         # in this case, "pk" indicates the point_id
#         id=SensorDevice.objects.get(pk=self.kwargs['pk'])
#         site=SensorDevice.objects.get(id=id.pk)
#         data=MeasureData.objects.filter(point_id=id.pk)
#         # # as following if you use "filter", you can get all contents of DB
#         # memo=SensorDevice.objects.get(pk=sensor_device_id) 
#         context={
#             "id":id,
#             "site":site,
#             "data":data
#         }
#         return render(request, 'sensor/detail.html', context)
#     #  model=SensorDevice
#     #  template_name= 'sensor/detail.html'

# def detail(request, sensor_device_id):
#     device=get_object_or_404(SensorDevice, pk=sensor_device_id)
#     # # as following if you use "filter", you can get all contents of DB
#     # memo=SensorDevice.objects.get(pk=sensor_device_id) 
#     context={
#         "device":device,
#     }
#     return render(request, 'sensor/detail.html', context)
#     # try:
#     #     device = SensorDevice.objects.get(pk=sensor_device_id)
#     # except SensorDevice.DoesNotExist:
#     #     raise Http404("SensorDevice does not exist")
#     # return render(request, 'sensor/detail.html', {'device': device })
# -----------------------------------------------------------------
# handling the uploading file
def handle_uploaded_file(f):
    path = os.path.join(UPLOAD_DIR, f.name)
    with open(path, 'wb+') as destination:
        """ 'w': 書込み用でファイルを開く
            ファイル名に指定したものがすでに存在する場合は上書き
            'b': バイナリーモードで開く
            '+': 更新のためディスクファイルを開く
            他に、'Y': 読み込み用、'X': 新規ファイルの書き込み用
            'a': 書込み用で開く、すでに存在している場合末行に追加書込み
        """
        for chunk in f.chunks():
            destination.write(chunk)
    try:
        addCsv.insert_csv_data(path)        # register the contents of csv file' to DB
    except Exception as exc:
        logger.error(exc)
    # Delete the apploaded file
    os.remove(path)                         
# -----------------------------------------------------------------
# CSV file uploading
class Upload(generic.FormView):
    template_name = 'main/upload.html'
    form_class = FileUploadForm
    
    def get_form_kwargs(self):
        # set prefix of correct csv file's name into variables
        # Pass variable to form
        variables='test'    
        kwargs=super(Upload,self).get_form_kwargs()
        kwargs.update({'variables':variables})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = self.get_form()
        context = {
            'form': form,
        }
        return context

    def form_valid(self, form):
        handle_uploaded_file(self.request.FILES['file'])
        # Redirect to upload complete view
        return redirect('main:upload_complete')  
"""
Another way
def upload(request):
    if request.method == 'POST':
        # form = UploadFileForm(request.POST, request.FILES)
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'])
            return redirect('main:upload_complete')  # アップロード完了画面にリダイレクト
    else:
        # form = UploadFileForm()
        form = FileUploadForm()
    return render(request, 'main/upload.html', {'form': form})
"""
# -----------------------------------------------------------------
# Complete the file uploading
class UploadComplete(generic.FormView):
    template_name = 'main/upload_complete.html'
    form_class = FileUploadForm
"""
Another way
def upload_complete(request):
    return render(request, 'main/upload_complete.html')
    return render(request, 'main/upload.html')
"""
# -----------------------------------------------------------------
# class Load(generic.FormView):
#     template_name = 'load.html'
#     form_class = FileUploadForm
    
#     def get_form_kwargs(self):
#         # set prefix of correct csv file's name into valiables
#         valiables='test'    # valiable to pass to form
#         kwargs=super(Load,self).get_form_kwargs()
#         kwargs.update({'valiables':valiables})
#         return kwargs

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         form = self.get_form()
#         context = {
#             'form': form,
#         }
#         return context

#     def form_valid(self, form):
#         handle_uploaded_file(self.request.FILES['file'])
#         # return redirect('sensor:upload_complete')  # to redirect to upload complete view
#         return redirect('sensor:load')
#         # 2022.12.21 why can not return to index page from here
#         # return redirect('index(req)')

# 2022/12/21 Download csv file 
# def download(request):
#     # To produce csv file to download
#     response = HttpResponse(content_type='text/csv')
#     # 2022/12/21 need to generate a "filename" based on the download data
#     response['Content-Disposition'] = 'attachment;  filename="VerticalWriting_FUJICO.csv"'
#     writer = csv.writer(response)
#     # 2022/12/21 arrange csv format data
#     writer.writerow(['F','as 1st letter'])
#     writer.writerow(['U','as 2nd letter'])
#     writer.writerow(['J','as 3rd letter'])
#     writer.writerow(['C','as 4th letter'])
#     writer.writerow(['O','as 5th letter'])
#     return response

# def call_write_data(req):
#     if req.method == 'GET':
#         # write_data.pyのwrite_csv()メソッドを呼び出す。
#         # ajaxで送信したデータのうち"input_data"を指定して取得する。
#         data_rw.write_csv_1(req.GET.get("input_data"))
#         data_rw.write_csv_1(req.GET.get("input_data1"))
#         # 読み出し、write_data.pyの中に新たに記述したメソッド(return_text())を呼び出す。
#         data = data_rw.return_text(req.GET.get("input_data"))
#         data1 = data_rw.return_text(req.GET.get("input_data1"))
#         # 受け取ったデータをhtmlに渡す。
#         return HttpResponse(data)
#         # writeの場合のリターン
#         #return HttpResponse()
# -----------------------------------------------------------------
def ajax_number(request):
    number1 = int(request.POST.get('number1'))
    number2 = int(request.POST.get('number2'))
    plus = number1 + number2
    minus = number1 - number2
    d = {
        'plus': plus,
        'minus': minus,
    }
    return JsonResponse(d)
