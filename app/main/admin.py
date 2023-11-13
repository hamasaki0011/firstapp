from django.contrib import admin
from .models import Location,Sensors,Result
# from django.contrib import SensorsAdmin

class SensorsInline(admin.TabularInline):
    model=Sensors
    # exclude=['note']
    extra=0

class LocationAdmin(admin.ModelAdmin):
    # fields = ['id', 'name', 'memo',]
    fields = ['name', 'memo',]
    inlines=[SensorsInline]
    # list_display = ('id', 'name', 'memo',)
    list_display = ('name', 'memo',)
    list_filter=['name']
    # search_fields=['name']

admin.site.register(Location, LocationAdmin)
# admin.site.register(Location)

admin.site.register(Sensors)
# class SensorsAdmin(admin.ModelAdmin):
#     fields = ['id', 'site', 'device',]
#     list_display = ('id', 'site', 'device',)
#     list_filter=['id']
#     # search_fields=['name']

class ResultInline(admin.TabularInline):
    model=Result
    extra=0

class ResultAdmin(admin.ModelAdmin):
    fields = ['place','point', 'measured_value', 'measured_date',]
    # fieldsets = [
    #     ('現場', {'fields': ['place']}),
    #     ('センサー', {'fields': ['point']}),
    #     ('測定日時', {'fields': ['measured_at']}),
    #     ('測定値', {'fields': ['data_value']}),
    # ]
    # inlines=[MeasureDataInline]
    list_display = ('place','point', 'measured_date', 'measured_value', 'created_date', 'was_measured_recently')
    list_filter=['measured_date', 'point',]
    # search_fields=['site']

admin.site.register(Result, ResultAdmin)