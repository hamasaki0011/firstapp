from django.shortcuts import render,redirect,get_object_or_404
# Create your views here.
# from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, CreateView, ListView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Record
from .forms import RecordForm
from django.utils import timezone

# Record list view
class RecordListView(ListView):
    template_name='record/record_list.html'
    model=Record
    
    # the selected records are reordered  by "published_date"
    def get_queryset(self):
        qs = Record.objects.all()
        # ユーザーがログインしていれば、リストを表示する
        # q = self.request.GET.get("search")
        # qs = Record.objects.search(query=q)
        # if self.request.user.is_authenticated:
        #     qs = qs.filter(Q(public=True)|Q(user=self.request.user))
        # else:
        #     qs = qs.filter(public=True)
        # qs = qs.order_by("-published_date")[:7]
        qs = qs.order_by("-published_date")
        return qs

# Detail view of record    
class RecordDetailView(DetailView):
    template_name='record/record_detail.html'
    model=Record

# Updating vew of record
# class RecordUpdateView(LoginRequiredMixin,UpdateView):
class RecordUpdateView(UpdateView):
    template_name = 'record/record_update.html'
    model = Record
    #form_class=RecordForm
    fields = ('title', 'text',)
    success_url = reverse_lazy('record:record_list')
 
    def form_valid(self, form):
        record = form.save(commit=False)
        # record.author = self.request.user
        record.published_date = timezone.now()
        record.save()
        return super().form_valid(form)

# Creating view of a new record
# class RecordCreateView(LoginRequiredMixin,CreateView):
class RecordCreateView(CreateView):
    template_name='record/record_create.html'
    form_class=RecordForm
    success_url=reverse_lazy('record:record_list')
    
    def form_valid(self, form):
        record = form.save(commit=False)
        # record.author = self.request.user
        record.published_date = timezone.now()
        record.save()
        return super().form_valid(form)
 
# class RecordDeleteView(LoginRequiredMixin,DeleteView):
class RecordDeleteView(DeleteView):
    template_name = 'record/record_delete.html'
    model = Record
    # form_class=RecordForm
    success_url = reverse_lazy('record:record_list')
    
class RecordArticleView(TemplateView):
    template_name='record/record_article.html'
    
class RecordPythonView(TemplateView):
    template_name='record/record_python.html'
    
class RecordServerView(TemplateView):
    template_name='record/record_server.html'
