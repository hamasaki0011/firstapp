from django import forms
from .models import Location, Sensors, Result
from accounts.models import User, Profile
import os
# import io, csv
from django.core.exceptions import ValidationError

VALID_EXTENSIONS=['.csv']

# Location model form
class LocationForm(forms.ModelForm):
    class Meta:
        model=Location
        # fields="__all__"
        # fields=('name','memo',)
        exclude=["user"]
    
    # viewで取得したuser情報を受け取る    
    def __init__(self, user = None, *args, **kwargs):
        for field in self.base_fields.values():
            # 2023.10.24 Expand the field data as location.name, location.memo and location.updated_date
            # In case of "all", User(login_user?) and as same as the above.
            field.widget.attrs.update({"class":"form-control"})
        # 2023.10.24 user = None, because the view function didn't get the user
        self.user=user
        super().__init__(*args, **kwargs)
    
    def save(self, commit=True):
        # 2023.10.24 save the location object which get from ~.
        location_obj=super().save(commit=False) 
        if self.user:
            # 2023.10.24 if the objects are belong to logged in user
            location_obj.user=self.user
            # 2023.10.24 add phrase
            # location_obj.name=self.user.belongs
        if commit:
            location_obj.save()
        return location_obj

# LocationForm class        
# 2023.10.24 Is this necessary?
class LocationFormClass(forms.Form):
    name = forms.CharField()
    memo = forms.CharField(widget=forms.Textarea())

# Sensors model form
class SensorsForm(forms.ModelForm):
    class Meta:
        model=Sensors
        # fields=('device', 'note',)
        # fields=('site', 'device', 'note',)
        fields="__all__"
        # exclude=["site"]
        
        site = forms.ModelChoiceField(
            queryset=Sensors.objects.none(), #空のクエリセット
        widget=forms.widgets.Select
        )

    # 2023.10.27 Receive the login_user information which view function gets.
    # def __init__(self, place=None, *args, **kwargs):
    def __init__(self, login_user = None, *args, **kwargs):    
        for field in self.base_fields.values():
            field.widget.attrs.update({"class":"form-control"})
        self.user = login_user
        # print('form#66_self.user', login_user)
        
        super().__init__(*args, **kwargs)
        if 'fujico@kfjc.co.jp' not in login_user.email: # type: ignore
            #2023.10.26 Except for admin user does not edit the location field.
            self.fields['site'].widget.attrs['readonly'] = 'readonly'
            # self.fields['site'].widget.attrs['disabled'] = 'disabled'

class SensorsFormClass(forms.Form):
    name = forms.CharField()
    memo = forms.CharField(widget=forms.Textarea())

class SensorsLocationForm(forms.ModelForm):
    class Meta:
        model=Sensors
        # fields=('device', 'note',)
        # fields=('site', 'device', 'note',)
        fields="__all__"
        # exclude=["site"]
                
        # site = forms.ModelChoiceField(
        #     queryset=Sensors.objects.none(), #空のクエリセット
        # widget=forms.widgets.Select
        # )

    # # viewで取得したplace情報を受け取る
    def __init__(self, place=None, *args, **kwargs):    
        # print("fields = ", self.base_fields.values())
        for field in self.base_fields.values():
            field.widget.attrs.update({"class":"form-control"})
        self.place=place
        super().__init__(*args, **kwargs)

class ResultForm(forms.ModelForm):
    class Meta:
        model=Result
        fields=(
            'place','point', 'measured_date', 'measured_value',
        )

# 2022/11/8 generate a button for CSV file uploading
class FileUploadForm(forms.Form):  
    file = forms.FileField(
        label='アップロードするファイルを選択'
    )

    # receive the variables which passed by views
    def __init__(self, *args, **kwargs):
        self.variables=kwargs.pop('variables',None) # get variables
        super(FileUploadForm, self).__init__(*args,**kwargs)

    # Add file validation feature at 2022/11/11 
    def clean_file(self):
        file=self.cleaned_data['file']
        extension=os.path.splitext(file.name)[1]    # get file' extension
        # is it csv file or not?
        if not extension.lower() in VALID_EXTENSIONS:
            raise forms.ValidationError('csvファイルを選択して下さい')
        # is it correct csv file or not?
        if not file.name.startswith(self.variables):
            raise forms.ValidationError('間違った名前のcsvファイルです。''（'+ self.variables + 'で始まるcsvファイルを選択してください。）')
