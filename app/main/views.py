from django.shortcuts import render, redirect
from django.views import generic
from django.urls import reverse_lazy
from .models import Location,Sensors,Result
from .forms import LocationForm, SensorsForm
from accounts.models import User, Profile
# ページへのアクセスをログインユーザーのみに制限する
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin

# 2023.9.29 from django.contrib.auth import get_user, get_user_model
from django.contrib import messages
from django.utils import timezone
import datetime
# Chart drawing with Plotly
import os
import logging
# Add cvs function
from main import addCsv
from .forms import FileUploadForm
# from .forms import UploadFileForm
import plotly.graph_objects as go
from plotly.subplots import make_subplots
# ajax trial
# 2023.9.29 from django.conf import settings
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

class OwnerOnly(UserPassesTestMixin):
    # 2023.10.23 所有者であるか否かを検証する。test_fuc()の返り値がTrueであれば所有者と判定
    def test_func(self):
        # Compare self.request.user and location_instance.user
        location_instance = self.get_object() # type: ignore
        # 2023.10.24 tentative
        # print("views#60_self.request.user = ", self.request.user) # type: ignore
        # print("views#61_location_instance.user = ", location_instance.user)
        
        return location_instance.user == self.request.user # type: ignore
    
    def handle_no_permission(self):
        # 2023.10.24 tentative
        pk=self.kwargs["pk"] # type: ignore
        # print("views#68_pk = ", pk)
        # print("views#69_user = ", self.request.user) # type: ignore
        # print("views#70_user.pk = ", self.request.user.pk) # type: ignore
        messages.error(self.request,f"情報の更新および削除ができるのは所有者のみです！: {pk}") # type: ignore
        # return redirect("main:location_detail", pk=self.kwargs["pk"])  # type: ignore
        return redirect("main:location_detail", pk)

# --- Main index view --------------------------------------------------------------
# Top view, you can select a target site for remote monitoring
class IndexView(LoginRequiredMixin, generic.ListView):
    template_name='main/index.html'
    model=Location
    
    def get_queryset(self):
        # Get the logged in user's information
        login_user=self.request.user
        # 空のクエリーを設定する
        location_list = Location.objects.none()        
        # ログインユーザーに許可されたQuery情報を渡す
        if login_user.is_authenticated:
            if 'fujico@kfjc.co.jp' in login_user.email: # type: ignore
                location_list = Location.objects.all()
            else:
                location_list = Location.objects.filter(name=login_user.profile.belongs) # type: ignore
                # location_list = Location.objects.filter(location.id = user.profile) # type: ignore
        return location_list.order_by('location.id')

# --- Registered users' view --------------------------------------------------------------
# 2023.10.23 display the user's profile
class RegistUserView(LoginRequiredMixin, generic.ListView):
    template_name = 'main/regist_user.html'
    model = User
    
    def get_queryset(self):
        login_user=self.request.user
        user_list = User.objects.none()
        
        if login_user.is_authenticated:
            if('fujico@kfjc.co.jp' in login_user.email): # type: ignore
                # 2023.10.23 users list display with being ordered by user.pk (=id) 
                user_list=User.objects.all().order_by('pk').reverse()
            else:
                # 2023.10.23 Modify only for the logged in user's profile information  
                user_list=User.objects.filter(pk = login_user.pk)                   
        
        return user_list

# --- Location List view --------------------------------------------------------------
# View of Locations' list 
class LocationListView(LoginRequiredMixin, generic.ListView):
    template_name='main/location_list.html'
    model=Location
    
    # Generating a query
    def get_context_data(self, **kwargs):
        login_user = self.request.user
        context = super().get_context_data(**kwargs)
        location_list = Location.objects.none()
        
        if "fujico@kfjc.co.jp" in login_user.email: # type: ignore
            # 管理者ログインなのでurlにpkはない！
            location_list = Location.objects.all()
            message = "管理者ログイン！"
        else:
            # 登録ユーザーのログイン、urlからpk情報を取得する
            # pk = self.kwargs['pk']  # This "pk" indicates the location.pk and also site_id
            message = "Not 管理者/" + login_user.profile.username + "(" + login_user.profile.belongs + "所属)" # type: ignore
            # 2023.10.23 Select the correct query of login_user's with login_user.profile.belongs
            location_list = Location.objects.filter(name = login_user.profile.belongs) # type: ignore
                
        context = {
            'location_list': location_list.order_by('location.created_date'),
            'message': message,
            'login_user': login_user
        }
        return context

# --- Location' detail view --------------------------------------------------------------
# Display the detail information for each location'
class LocationDetailView(LoginRequiredMixin, generic.DetailView):
    template_name='main/location_detail.html'
    model=Location
    
    # 2023.10.23 It seems ok if not below codes
    def get_object(self):
        location = super().get_object()
        
        # print('super().get_object() = ',tmp)
        # print('location.user = ',location.user)
        # print('login_user = ',self.request.user)
        # print('location = ', type(location))
        
        # return super().get_object()
        return location

# --- Location Update view --------------------------------------------------------------
# Update location's information
class LocationUpdateModelFormView(OwnerOnly,generic.UpdateView):
    template_name = "main/location_form.html"
    form_class = LocationForm
    success_url = reverse_lazy("main:location_list")
    
    def get_queryset(self):
        # in case of using a FormView, this function: get_queryset() is mandatory required 
        qs = Location.objects.all()
        # print("view#172_qs = ", qs)
        return qs
    
    # Update updated_date
    def form_valid(self, form):
        location = form.save(commit=False)
        location.updated_date = timezone.now()
        location.save()
        return super().form_valid(form)

# --- Location create view --------------------------------------------------------------
# Create a new location's information
class LocationCreateModelFormView(LoginRequiredMixin, generic.CreateView):
    template_name = "main/location_form.html"
    form_class = LocationForm
    success_url = reverse_lazy("main:location_list")
    
    # 2023.10.24 Get the logged in user information
    def get_form_kwargs(self):
        kwgs=super().get_form_kwargs()
        # 2023.10.24 this request.user means logged in user
        kwgs["user"]=self.request.user
        # 2023.10.24 at this moment, it doesn't have any location objects
        return kwgs
    
# --- Location delete view --------------------------------------------------------------
# Location delete view
# class LocationDeleteView(generic.DeleteView):
class LocationDeleteView(OwnerOnly,generic.DeleteView):
    template_name = 'main/location_delete.html'
    model = Location
    # form_class=LocationForm
    success_url = reverse_lazy('main:location_list')

# --- Chart drawing function --------------------------------------------------------------
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
                            color=COLOR[i],             # color pallet
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
                        color=COLOR[i-10],      # color pallet
                            width=2,
                        ),
                        line_dash="dot",
                        marker=dict(
                            symbol='circle',
                            color=COLOR[i-10],      # color pallet
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
                            color=COLOR[i-10],      # color pallet
                            width=2,
                            ),
                        line_dash="dot",
                        marker=dict(
                            symbol='square',
                            color=COLOR[i-10],      # color pallet
                            size=10,
                        ),
                    ),
                    secondary_y=True,
                )          
    return fig.to_html(include_plotlyjs='cdn',full_html=False).encode().decode('unicode-escape')
# --- Main detail view --------------------------------------------------------------
# View detail data of each site' sensor devices 
class DetailView(generic.ListView):
    template_name='main/detail.html'
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
        pointNum = len(sensor_list)

        # Get the smallest number of the point_id
        # 23.7.4 change 'sensor.id' to 'id' for django' revision up 3.2.17 to 4.2.3
        # startPoint=sensor_list.order_by('sensor.id').first().id
        if pointNum > 0:
            error = False
            # If there were some data, 
            startPoint=sensor_list.order_by('id').first().id # type: ignore
            #startPoint=sensor_list.order_by('id').first().id
            # Generate a graph data from sensor's measured_value   
            # Generate the table data including the device name and the most recent measured_data
            # recent_update=datetime.date(2023,2,27)
            # TD=9    # time differences
            # today = datetime.datetime.now() + datetime.timedelta(hours=TD)
            # 注意：最終的にはtimedeltaで1分前のデータを表示するように調整する
            today = datetime.datetime.now()
            start_date=today-datetime.timedelta(hours=1)
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
            # 2023.5.8 try it later y_tmp=[[]*latest for j in range(6)]
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
                y_tmp[startPoint-1+i]=data_list.filter(point_id=startPoint+i).order_by('measured_date')[:latest] # type: ignore

                for data in y_tmp[startPoint-1+i]:
                    ydata[startPoint-1+i].append(data.measured_value)
                """
                'if' and 'for' Statements both do not form scopes in Python. 
                Therefore, the variable if inside the sentence is the same as the variable outside.
                Variables, 'start_at' and 'd_tmp' later appeared are effective both inside and outside.
                """
        
            context={
                # for confirmation
                # For the latest measured value table
                "error":error, 
                "location":location,
                "results":results,
                "message":message,
                # For chart drawing
                "plot":line_charts(xdata,ydata,startPoint,pointNum,legend), 
            }
            return render(request, "main/detail.html", context)
        else:
            error = True
            # There are no data
            message = "デバイス(センサー)登録が未了で、まだ表示できるものがありません！"
            context = {
                "error":error, 
                "location":location,
                "message" :message
            }
        return render(request, 'main/detail.html', context)

# --- All sensors' view --------------------------------------------------------------
# If you have signed in, you can view the all sensors' list
class SensorsAllListView(LoginRequiredMixin, generic.ListView):
    template_name='main/sensors_all_list.html'
    model=Sensors
 
    # def get_form_kwargs(self):
    #     kwgs=super().get_form_kwargs() # type: ignore
    #     kwgs["user"]=self.request.user
    #     return kwgs
    
    # 2023.10.25 get the user information and query, Sensors.objects
    def get_queryset(self):
        # 2023.10.25 This case of self.request.user is logged in user
        login_user = self.request.user
        sensors_list = Sensors.objects.none()
        locations =Location.objects.all()

        if login_user.is_authenticated:
            if "fujico@kfjc.co.jp" in login_user.email: # type: ignore
                # 2023.10.25 If logged in user is administrator, set all of Sensors.objects
                sensors_list = Sensors.objects.all()
            else:
                # 2023.10.25 Select the location.pk from Location objects which belongs to logged in user.
                location_key = locations.filter(name = login_user.profile.belongs).first().id # type: ignore
                sensors_list = Sensors.objects.filter(site = location_key)
        return sensors_list.order_by("site")

# --- sensor create view --------------------------------------------------------------
# Create sensor'
# このページで現場がChoiceファームになっているのが気に入らない！
class SensorsCreateModelFormView(generic.CreateView):
    template_name = "main/sensors_create.html"
    form_class = SensorsForm
    # SensorsForm.fields['site'].queryset = Sensors.objects.filter(pk=3)
    success_url = reverse_lazy("main:sensors_all_list")
    
    # 2023.10.11　site情報をview関数から取得する必要がある
        
    # place情報を取得する
    # def get_form_kwargs(self):
    #     kwgs=super().get_form_kwargs()
    #     # kwgs["place"]=self.place # type: ignore
    #     print('self = ',self.get_context_data) # type: ignore
    #     return kwgs
    
# Create a new Sensor place information view
# 2023.10.5 tentatively omitted
# class SensorsCreateModelFormView(generic.CreateView):
#     template_name = "main/sensors_create.html"
#     form_class = SensorsForm
#     success_url = reverse_lazy("main:sensor_list")
    
    # place情報を取得する
    # def get_form_kwargs(self):
    #     kwgs=super().get_form_kwargs()
    #     kwgs["place"]=self.place
    #     return kwgs
    
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
        sensors.created_date = timezone.now()
        sensors.updated_date = timezone.now()
        sensors.save()
        return super().form_valid(form)
"""

# --- Sensor' location create view --------------------------------------------------------------
# You can view the each site' sensors create
# class SensorsLocationCreateView(generic.CreateView):
#     template_name='main/sensors_location_create.html'
#     # model=Sensors
#     form_class = SensorsForm
#     # SensorsForm.fields['site'].queryset = Sensors.objects.filter(pk=3)
#     success_url = reverse_lazy("main:sensors_all_list")
    
#     # place情報を取得する
#     def get_form_kwargs(self):
#         kwgs=super().get_form_kwargs()
#         kwgs["pk"]=self.kwargs
#         # print('pk = ', kwgs['pk'])
#         return kwgs

# --- Sensor list view --------------------------------------------------------------
# You can view the each site' sensors list
# class SensorsEachListView(generic.ListView):
#     template_name='main/sensors_each_list.html'
#     model=Sensors

#     # urlのpkを取得してクエリを生成する
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         pk = self.kwargs['pk']  # This "pk" indicates the site_id and also location.id 
#         sensors_list = Sensors.objects.filter(site_id = pk) # pkを指定してデータを絞り込む
        
#         # Put message whether adapt query is there or not
#         if sensors_list.first() is not None:
#             message = "There are some query data"
#         else:
#             message = "センサーを追加してください！"
            
#         context = {
#             'sensors_list': sensors_list,
#             'location': Location.objects.get(id = pk),
#             'msg': message,
#         }
#         return context
    
    # Queryを取得する
    # def get_queryset(self, **kwargs): 
    #     context = super().get_context_data(**kwargs)
    #     pk = self.kwargs['pk']
    #     print("pk = ", pk)
    #     object_list = Sensors.objects.filter(id = pk)
    #     login_user = self.request.user
    #     print("login_user =", login_user)
        
    #     if object_list is None:
    #         print("オブジェクトが登録されていません\r\n代わりにすべて表示します。")
            
    #     else:
    #         print("なぜかオブジェクトがあります")
        
    #     # # ユーザーがログインしていれば、リストを表示する
    #     # if self.request.user.is_authenticated:
    #     #     # print("site =", Sensors.site(user.id))  
    #     #     qs = qs.filter(id = context['pk'])
    #     #     print("qs =", qs)
    #     #     # qs = qs.filter(Q(public=True)|Q(user=self.request.user))
    #     # else:
    #     #     print("user =", self.request.user)
    #     #     # print("Sensors.site =", Sensors.site.location)
    #     #     # qs = qs.filter(public=True)
    #     # # # the selected records are re-ordered  by "created_date"         
    #     # qs = qs.order_by("created_date")[:7]
    #     qs = Sensors.objects.all()
    #     return qs

# --- Sensors' detail view  --------------------------------------------------------------
# You can view the each site' sensors detail
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

# --- Sensor update view --------------------------------------------------------------
# Update sensor' information
class SensorsUpdateModelFormView(generic.UpdateView):
    template_name = "main/sensors_update.html"
    form_class = SensorsForm
    success_url = reverse_lazy("main:sensors_all_list")
    
    # Following get_queryset() is mandatory required.
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

# --- Senor delete view --------------------------------------------------------------
# Delete Sensor information
class SensorsDeleteView(generic.DeleteView):
    template_name = 'main/sensors_delete.html'
    model = Sensors
    # form_class=LocationForm
    success_url = reverse_lazy('main:sensors_all_list')
# -----------------------------------------------------------------
# 2022/11/8 CSV file uploading
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

# --- handle uploading function --------------------------------------------------------------
# handling the uploading file
def handle_uploaded_file(f):
    path = os.path.join(UPLOAD_DIR, f.name)
    """ 'w': 書込み用でファイルを開く
        ファイル名に指定したものがすでに存在する場合は上書き
        'b': バイナリーモードで開く
        '+': 更新のためディスクファイルを開く
        他に、'Y': 読み込み用、'X': 新規ファイルの書き込み用
        'a': 書込み用で開く、すでに存在している場合末行に追加書込み
    """
    with open(path, 'wb+') as destination:
        """  ~ in xxx: リストオブジェクトxxxから1つずつ要素を
            取り出して、~の変数に代入してループ処理を行う。
            リストオブジェクトは、メソッドchunk()で分割されたもの
            chunk(): ファイルをchunk_sizeに指定したサイズの塊りずつ
            読みだす。chunk_sizeのデフォールトは64KB。
        """
        for chunk in f.chunks():
            destination.write(chunk)
    
    try:
        addCsv.insert_csv_data(path)        # register the contents of csv file' to DB
    except Exception as exc:
        logger.error(exc)
    # Delete the uploaded file
    os.remove(path)                         

# --- Upload view --------------------------------------------------------------
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

# --- Upload complete view --------------------------------------------------------------
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
#         # set prefix of correct csv file's name into variables
#         variables='test'    # variable to pass to form
#         kwargs=super(Load,self).get_form_kwargs()
#         kwargs.update({'variables':variables})
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

# --- Ajax number function --------------------------------------------------------------
# Testing an ajax function
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
