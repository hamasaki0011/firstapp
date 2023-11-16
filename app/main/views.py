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

# 2023.11.15 Show disk capacity
import shutil

# import dateutil
# from dateutil import tz
# from dateutil.relativedelta import relativedelta
# from django.http import Http404
# from django.shortcuts import get_object_or_404
# from django.http import HttpResponseRedirect
# from .application import data_rw
# from django.http import HttpResponse 
# from sensor.forms import FileUploadForm
# import sys
# import time

# directory to store the uploading files
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), 'static/uploads/')
# Define debug log-file
logger = logging.getLogger('development')
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)
# handler = logging.FileHandler("./test.log")
# handler.setLevel(logging.DEBUG)
# formatter = logging.Formatter('%(levelname)s  %(asctime)s  [%(name)s] %(message)s')
# handler.setFormatter(formatter)
# logger.addHandler(handler)

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
        messages.error(self.request,f"情報の更新および削除ができるのは所有者のみです！: {pk}") # type: ignore
        # return redirect("main:location_detail", pk=self.kwargs["pk"])  # type: ignore
        return redirect("main:location_detail", pk)

def disk_chk():
    disk_total, disk_used, disk_free = shutil.disk_usage('./')
    
    total = f'総容量: {int(disk_total / (2**30))} GiB'
    used = f'使用済み: {int(disk_used / (2**30))} GiB'
    free = f'空き容量: {int(disk_free / (2**30))} GiB'
    
    return (total, used, free)

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
        
        # 2023.11.6 Is it ok to use "location.id" for the display site list with ordering?
        return location_list.order_by('location.id')

def set_latest_table(results, sensors):
    table_data = []
    recent_data = None
    no_data_list = []
    
    comment = "※ 1分毎に更新します。(工事中は30分毎に設定)"    
    
    # 2023.11.2 In order to get the latest results, set the time which it go back in time for a time difference. 
    today = datetime.datetime.now()
    start_date=today - datetime.timedelta(minutes = 10)
    # 2023.11.6 Pick up the data which get within 1 minutes. 
    latest_group = results.filter(created_date__range = (start_date,today))
    
    for sensor in sensors:
        # 2023.11.14 Pick up the latest data.
        latest = latest_group.filter(point_id = sensor.pk).order_by('-measured_date')
        
        if latest.first() is None:
            # 2023.11.7 If the latest data does Not exist
            recent_data = results.filter(point_id = sensor.pk).order_by('-measured_date').first()
            
            if recent_data is None:
                recent_data = None
                no_data_list.append(sensor.device)
                # 2023.11.7 This subject would be solved in the future.
                comment = f"【警告】{', '.join(map(str, no_data_list))}のデータが取れていません。"
        
        else:
            # 2023.11.7 If the latest data does exist  
            recent_data = latest.first()
        
        # 2023.11.7 Finally, get the latest data array as recent_result     
        table_data.append(recent_data)
        
    return (table_data, comment)

def set_chart_data(results, sensors):
    # 2023.11.7 Prepare the chart drawing data.
    xdata = []
    index_key = []
    sensor_name = []
    data_value =[]
    data_unit = []
    
    # 2023.11.15 将来、グラフ描画点数を制御するためにX_MAXをキープ
    X_MAX = 30

    # 2023.11.15 将来、別の方法でグラフの描画点数を決める
    dot_max = 0
    for sensor in sensors:
        result_list = results.filter(point_id = sensor.pk)
        if dot_max < len(result_list):
            dot_max = len(result_list)

    sensor_index = 0    
    for sensor in sensors:
        index_key.append(sensor_index)
        sensor_name.append(sensor.device)
        # 2023.11.15 unitデータの取得方法はデータベース改造を含めて再考要
        data_unit.append(sensor.measure_unit)
        
        # 2023.11.8 Generate a xdata from all sensors at the location.
        result_list = results.filter(point_id = sensor.pk)
        d_arry = [0.0 for i in range(dot_max)]
        for data in result_list:
            if data.measured_date not in xdata:
                xdata.append(data.measured_date)
                            
            dot_num = 0
            for date in xdata:                
                if data.measured_value is not None and date == data.measured_date:
                    d_arry[dot_num] = data.measured_value
                dot_num += 1

        data_value.append(d_arry)
        sensor_index += 1

    legend = dict(zip(index_key, sensor_name))
    units = dict(zip(index_key, data_unit))
    ydata = dict(zip(index_key, data_value))
    
    context = {
        'unit': units,
        "plot":drawChart.line_charts(xdata, ydata, 0, len(legend), legend), 
        }
    
    return context 

# --- Main detail view --------------------------------------------------------------
# 2023.11.13 Detail information view for each location's. 
class DetailView(LoginRequiredMixin, generic.ListView):
    template_name='main/detail.html'
    model=Result

    def get(self, request, *args, **kwargs):
        # 2023.11.2 Solve the selected location and registered_user information from url.
        location=Location.objects.get(pk = self.kwargs['pk'])
        login_user = self.request.user
        login_user_group = login_user.profile.belongs # type: ignore
        # 2023.11.14 Get all sensor devices data at this location. 
        sensors = Sensors.objects.filter(site_id = location.pk).order_by('pk')
        # print(f'view#100_sensors = {sensors}')
        
        # 2023.11.15 Keep status variable as string and latest data table array. 
        latest_data = []
        status = ""
        message = "" 
        context = {"error": status, "location": location, "message": message,}
        if login_user.is_authenticated:
            status = 'registered_user'
            
            if('fujico@kfjc.co.jp' in login_user.email) or login_user_group in location.name: # type: ignore
                status = "allowed_user"
            
                # 2023.11.7 Firstly, check whether at least one of Sensors.objects' data is valid or not.
                if sensors.first() is not None:
                    
                    # 2023.11.7 Choose the satisfied data for the selected location
                    results = Result.objects.filter(place_id = location.pk)
                    
                    if results.first() is None:
                        message="【状況】まだ、測定データの取得ができていません！"
                        latest_data = None
                    
                    else: 
                        latest_data, message = set_latest_table(results, sensors)
                    
                    ctx = {
                        # 2023.11.6 Judge to display alert or not
                        "error": status,
                        "location": location,
                        "message":message,
                        
                        "results": latest_data,
                        "total": disk_chk()[0],
                        "used": disk_chk()[1],
                        "free": disk_chk()[2],
                        
                        } | set_chart_data(results, sensors)
                    context = context | ctx 
            
                else:
                    # 2023.11.6 No sensor settings
                    status = "allowed_user_but_no_data"
                    # sensors = Sensors.objects.none()
                    # 2023.11.7 Put the alert message there are no sensor settings' data.
                    message = "【注意】まだ、センサーデバイスの設定ができていません！"
            
                    ctx = {
                        "error":status,
                        "location":location,
                        "message" :message,
                    }
                    context = context | ctx

            else:
                status = "not_allowed_user"
                # sensors = Sensors.objects.none()
                # 2023.11.7 Put the alert message there are no sensor settings' data.
                message = "【警告】このページを閲覧することはできません！"

                ctx = {
                    "error":status,
                    "location":location,
                    "message" :message,
                    
                    "login_user": login_user.profile.username, # type: ignore
                }
                context = context | ctx
        else:
            # 2023.11.15 It 
            status = 'not_authenticated_user'
            message = 'ユーザー登録とログインが必要です。'
            context = context
            
        return render(request, "main/detail.html", context)

# --- Location List view --------------------------------------------------------------
# 2023.11.9 Locations' list view 
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
# 2023.11.8 The location's detail information view.
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
# 2023.11.9 Update location's information
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

# --- Location delete view --------------------------------------------------------------
# 2023.11.9 Delete location' information view
class LocationDeleteView(OwnerOnly,generic.DeleteView):
    template_name = 'main/location_delete.html'
    model = Location
    # form_class=LocationForm
    success_url = reverse_lazy('main:location_list')

# --- Location create view --------------------------------------------------------------
# 2023.11.9 Create a new location's information
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

        return context
    
# --- Sensors' detail view  --------------------------------------------------------------
# 2023.11.9 The sensor's detail view.
class SensorsDetailView(generic.DetailView):
    template_name='main/sensors_detail.html'
    model=Sensors

    def get_object(self):
        sensors = super().get_object()
        return sensors
        
# --- Sensor update view --------------------------------------------------------------
# 2023.11.9 Update sensor' information
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
# 2023.11.9 Delete Sensor information
class SensorsDeleteView(generic.DeleteView):
    template_name = 'main/sensors_delete.html'
    model = Sensors
    # form_class=LocationForm
    success_url = reverse_lazy('main:sensors_all_list')

# --- sensor create view --------------------------------------------------------------
# 2023.11.9 Create sensor'
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
            # 2023.11.13
            # chunk = b'measured_date,measured_value,point_id,place_id\r\n
            # 2023-3-20 15:01:00,18.0,19,1\r\n
            # 2023-3-20 15:01:00,22.5,22,1\r\n
            # 2023-3-20 15:01:00,120.5,27,1\r\n
            # 2023-3-20 15:01:00,25.2,18,2\r\n
            # 2023-3-20 15:01:00,15.6,24,2\r\n
            # 2023-3-20 15:01:00,14.0,26,2\r\n
            # 2023-3-20 15:01:00,20.0,25,4\r\n'
            destination.write(chunk)
            # 2023.11.13 destination is upload path and file name 
            # destination = <_io.BufferedRandom name='/usr/src/app/main/static/uploads/testNew_14.csv'> 
    
    try:
        addCsv.insert_csv_data(path)        # register the contents of csv file' to DB
    except Exception as exc:
        logger.error(exc)
    # Delete the uploaded file after uploading.
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
        # return redirect('main:upload_complete')
        return redirect('main:index')

# --- Upload complete view --------------------------------------------------------------
# 2023.11.14 Complete the file uploading
class UploadComplete(generic.FormView):
    template_name = 'main/upload_complete.html'
    form_class = FileUploadForm

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
        
        return user_list

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