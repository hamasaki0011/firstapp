from django import forms
from .models import Record

class RecordForm(forms.ModelForm):
    class Meta:
        model=Record
        fields=('title', 'text',)
#        widgets={
#            'date' : forms.DateInput(attrs={'class' : 'form-control'}),
#            'title' : forms.TextInput(attrs={'class' : 'form-control'}),
#            'text' : forms.TextInput(attrs={'class' : 'form-control'}),
#        }
