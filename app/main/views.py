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
from main import drawChart

# from .forms import UploadFileForm
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

# 2023.11.1 below chart drawing function was relocated in external application file named drawChart.py
# import plotly.graph_objects as go
# from plotly.subplots import make_subplots
# Color palette for chart drawing which prepared 10 colors
# COLOR=['darkturquoise','orange','green','red','blue','brown','violet','magenta','gray','black']
# ~ 2023.11.1

class OwnerOnly(UserPassesTestMixin):
    # 2023.10.23 Check whether user who logged in is the owner or not.
    # If owner case, test_func() will return 'True'.
    def test_func(self):
        # Compare self.request.user and location_instance.user
        location_instance = self.get_object() # type: ignore
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
        # 2023.10.26 Get the logged in user's information.
        login_user=self.request.user
        # 2023.10.26 Set a vacant query as the location_list.
        location_list = Location.objects.none()        
        # 2023.10.26 Pass the correct query to logged in user.
        if login_user.is_authenticated:
            if 'fujico@kfjc.co.jp' in login_user.email: # type: ignore
                location_list = Location.objects.all()
            else:
                location_list = Location.objects.filter(name=login_user.profile.belongs) # type: ignore
                print('view#92_location_list = ', location_list)
        # 2023.11.6 Is it ok to use "location.id" for the display site list with ordering?
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
                # user_list=User.objects.all().order_by('pk').reverse()
                print('view#_user.pk' ,login_user.pk)
                print('view#_user.belongs' ,login_user.profile.belongs) # type: ignore
        
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
    
    # 2023.10.31     
    def get_context_data(self, **kwargs):
        login_user = self.request.user
        # Get location.objects' data
        location = super().get_object()
        # Get context data
        context = super().get_context_data(**kwargs)
        # Set Sensors.object to display all of own sensor settings
        sensors_list = Sensors.objects.none()
        
        if login_user.is_authenticated:
        # if "fujico@kfjc.co.jp" in login_user.email: # type: ignore
            # 管理者ログインなのでurlにpkはない！
            sensors_list = Sensors.objects.filter(site = location.pk)
        else:
            # Except for admin user, no user can view this page.
            sensors_list = Sensors.objects.none()
                
        context = {
            'location': location,
            'sensors_list': sensors_list.order_by('site'),
            'login_user': login_user,
        }
        return context

# --- Location Update view --------------------------------------------------------------
# Update location's information
class LocationUpdateModelFormView(OwnerOnly,generic.UpdateView):
    template_name = "main/location_form.html"
    form_class = LocationForm
    success_url = reverse_lazy("main:location_list")
    
    def get_queryset(self):
        # 2023.11.1 This function: get_queryset() is mandatory required in case of using a FormView,  
        qs = Location.objects.all()
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
# Delete location' information view
class LocationDeleteView(OwnerOnly,generic.DeleteView):
    template_name = 'main/location_delete.html'
    model = Location
    # form_class=LocationForm
    success_url = reverse_lazy('main:location_list')

# --- Main detail view --------------------------------------------------------------
# View detail information of sensor devices at each location'. 
# class DetailView(generic.ListView):
class DetailView(generic.DetailView):
# class DetailView(LoginRequiredMixin, generic.ListView):
    template_name='main/detail.html'
    model=Result

    def get(self, request, *args, **kwargs):
        # 2023.11.2 Solve the selected location information from url.
        location=Location.objects.get(pk = self.kwargs['pk'])
        # 2023.11.2 Get the latest results
        today = datetime.datetime.now()
        # 2023.11.6 Set the display period.
        # 注意：最終的にはtimedeltaで1分前のデータを表示するように調整する
        # start_date=today - datetime.timedelta(minutes = 30)
        start_date=today - datetime.timedelta(hours = 3)
        
        # 2023.11.6 Are there any sensor setting at first?n
        sensors = Sensors.objects.filter(site_id = location.pk)
        # 2023.11.6 Judge to alert there are no sensor settings
        recent_data = []
        # 2023.11.7 Firstly, check whether Sensors.objects have valid settings or not.
        if sensors.first() is not None:
            error = False
            # 2023.11.7 Choose the satisfied data for selected location
            results = Result.objects.filter(place_id = location.pk)
            if results.first() is None:
                message="まだ測定データが取得できていません！"
            else: 
                message="1分毎に更新します。(工事中は30分毎に設定)"

                # 2023.11.6 Prepare the latest data for each sensor device.
                latest = results.filter(created_date__range = (start_date,today))                
                tmp_result = None
                for sensor in sensors:
                    latest_chk = latest.filter(point_id = sensor.pk)
                    if latest_chk.first() is None:
                        # 2023.11.7 If the latest data does Not exist
                        tmp_result = results.filter(point_id = sensor.pk).order_by('measured_date').reverse().first()
                        if tmp_result is None:
                            # 2023.11.7 This subject would be solved in the future.
                            message = f"{sensor.device}のデータが取れていません。"
                    else:
                        # 2023.11.7 If the latest data does exist  
                        tmp_result = latest_chk.first()
                    # 2023.11.7 Finally, get the latest data array as recent_result     
                    recent_data.append(tmp_result)

            # 2023.11.7 Prepare the chart drawing data.
            # The first, produce a x-axis data -30 from 0
            X_MAX = 30
            # 2023.11.2 Prepare x and y axis data array and legend array
            xdata = []         
            # 2023.11.2 Create the x_axis series data
            
            # 2023.11.6 Prepare the y-axis data
            sensors = Sensors.objects.filter(site_id = location.pk)
            key_num = []    # 2023.11.6 Prepare series number  
            s_name =[]      # 2023.11.6 Prepare series name        
            d_value =[]     # 2023.11.6 Prepare data value
            
            s_index =0           
            for sensor in sensors:
                # 2023.11.7 Prepare the legend's dictionary. 
                key_num.append(s_index)
                s_name.append(sensor)
                s_index += 1
                
                # 2023.11.8 Generate a xdata from all sensors at the location.
                r_list = results.filter(point_id = sensor.pk)
                for m_data in r_list:
                    if m_data.measured_date not in xdata:
                        xdata.append(m_data.measured_date)  
            
            legend = dict(zip(key_num, s_name))

            dot_max = 0            
            for sensor in sensors:
                r_list = results.filter(point_id = sensor.pk)
                if dot_max < len(r_list):
                    dot_max = len(r_list)
                                        
                d_arry = [0.0 for i in range(dot_max)]
                for m_data in r_list:
                    dot_num = 0
                    for date in xdata:
                        if m_data.measured_value is not None and date == m_data.measured_date:
                            d_arry[dot_num] = m_data.measured_value
                        dot_num += 1
                d_value.append(d_arry)

            ydata = dict(zip(key_num, d_value))

            context={
                # 2023.11.6 Judge to display alert or not
                "error": error, 
                "location": location,
                "results": recent_data,
                # "remark": remark,
                'sensors': sensors.order_by('pk'),
                
                "xdata": xdata,
                "series_name": legend,
                "ydata": ydata,

                "message":message,
                
                # 2023.11.2 tentatively comment out For chart drawing
                "plot":drawChart.line_charts(xdata, ydata, 0, len(legend), legend), 
            }
            
        else:
            # 2023.11.6 No sensor settings
            error = True
            
            # 2023.11.7 Put the alert message there are no sensor settings' data.
            message = "デバイス(センサー)登録が未了で、まだ表示できるものがありません！"
            
            context = {
                "error":error,
                "location":location,
                "message" :message,
            }
                        
        return render(request, "main/detail.html", context)


# --- All sensors' view --------------------------------------------------------------
# 2023.10.27 If you have signed in, you can view the all sensors' list
class SensorsAllListView(LoginRequiredMixin, generic.ListView):
    template_name='main/sensors_all_list.html'
    model=Sensors
        
    # 2023.10.25 get the user information and query, Sensors.objects；
    # def get_queryset(self):
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        # 2023.10.25 This case of self.request.user is logged in user
        login_user = self.request.user
        locations =Location.objects
        location_key = 1
        sensors = Sensors.objects
        sensors_list = sensors.all()
        message = " "

        if login_user.is_authenticated:
            if "fujico@kfjc.co.jp" in login_user.email: # type: ignore
                if sensors_list.first() is not None:
                    # 2023.10.25 If logged in user is administrator, set all of Sensors.objects
                    sensors_list = sensors_list.order_by("sensors.pk").order_by("site")
                    message = "センサー全体一覧(登録順)"
                else:
                    sensors_list = sensors.none()
                    message = "まだ、センサー設定されていません。センサーを設定してください。"
            else:
                if sensors_list.first() is not None:
                    # 2023.10.25 Select the location.pk from Location objects which belongs to logged in user.
                    location_key = locations.filter(name = login_user.profile.belongs).first().id # type: ignore
                    sensors_list = sensors_list.filter(site = location_key)
                    message = "センサー一覧(登録順)"
                else:
                    sensors_list = sensors.none()
                    message = "まだ、センサー設定されていません。センサーを設定してください。"

        context = {
            'sensors_list': sensors_list,
            'message': message,
            'location': locations.get(id = location_key),
            'location_key': location_key,
        }
        # return sensors_list.order_by("site")
        return context
    
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
    
#     # Queryを取得する
#     # def get_queryset(self, **kwargs): 
#     #     context = super().get_context_data(**kwargs)
#     #     pk = self.kwargs['pk']
#     #     print("pk = ", pk)
#     #     object_list = Sensors.objects.filter(id = pk)
#     #     login_user = self.request.user
#     #     print("login_user =", login_user)
        
#     #     if object_list is None:
#     #         print("オブジェクトが登録されていません\r\n代わりにすべて表示します。")
            
#     #     else:
#     #         print("なぜかオブジェクトがあります")
        
#     #     # # ユーザーがログインしていれば、リストを表示する
#     #     # if self.request.user.is_authenticated:
#     #     #     # print("site =", Sensors.site(user.id))  
#     #     #     qs = qs.filter(id = context['pk'])
#     #     #     print("qs =", qs)
#     #     #     # qs = qs.filter(Q(public=True)|Q(user=self.request.user))
#     #     # else:
#     #     #     print("user =", self.request.user)
#     #     #     # print("Sensors.site =", Sensors.site.location)
#     #     #     # qs = qs.filter(public=True)
#     #     # # # the selected records are re-ordered  by "created_date"         
#     #     # qs = qs.order_by("created_date")[:7]
#     #     qs = Sensors.objects.all()
#     #     return qs

# --- sensor create view --------------------------------------------------------------
# Create sensor'
class SensorsCreateModelFormView(LoginRequiredMixin, generic.CreateView):
    template_name = "main/sensors_create.html"
    form_class = SensorsForm
    # SensorsForm.fields['site'].queryset = Sensors.objects.filter(pk=3)
    success_url = reverse_lazy("main:sensors_all_list")
    
    # 2023.10.11　site情報をview関数から取得する必要がある
    # place/user情報を取得する
    # def get_form_kwargs(self, place = None, **kwargs):
    def get_form_kwargs(self, *args, **kwargs):
        kwgs=super().get_form_kwargs(*args, **kwargs)
        login_user = self.request.user
        kwgs['login_user'] = login_user
        
        if 'fujico@kfjc.co.jp' not in login_user.email: # type: ignore
            # 2023.10.26 The number of location where request user is belonging. 
            location_id = Location.objects.filter(name = login_user.profile.belongs).first().id # type: ignore
            # 2023.10.26 Initialize site form with the above location_id number.
            kwgs['initial'] = {'site': location_id} # type: ignore

        return kwgs
    
    def get_context_data(self, **kwargs):
        # Add user information for page context.
        context = super().get_context_data(**kwargs)
        context['login_user'] = self.request.user
        return context
    
# --- Sensors' detail view  --------------------------------------------------------------
# You can view the each site' sensors detail
class SensorsDetailView(generic.DetailView):
    template_name='main/sensors_detail.html'
    model=Sensors

    def get_object(self):
        sensors = super().get_object()
        return sensors
        
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
    
    def get_form_kwargs(self, *args, **kwargs):
        kwgs=super().get_form_kwargs(*args, **kwargs)
        login_user = self.request.user
        kwgs['login_user'] = login_user
        
        if 'fujico@kfjc.co.jp' not in login_user.email: # type: ignore
            # 2023.10.26 The number of location where request user is belonging. 
            location_id = Location.objects.filter(name = login_user.profile.belongs).first().id # type: ignore
            # 2023.10.26 Initialize site form with the above location_id number.
            kwgs['initial'] = {'site': location_id} # type: ignore

        return kwgs
    
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

# 2023.11.1 The chart drawing function was relocated in external application file named drawChart.py  

