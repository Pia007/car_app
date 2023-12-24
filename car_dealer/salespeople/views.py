from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Salespeople

class SalespeopleListView(ListView):
    model = Salespeople
    template_name = 'salespeople/salespeople_list.html'
    context_object_name = 'salespeople'

class SalespeopleDetailView(DetailView):
    model = Salespeople
    template_name = 'salespeople/salespeople_detail.html'
    context_object_name = 'salespeople'

class SalespeopleCreateView(CreateView):
    model = Salespeople
    template_name = 'salespeople/salespeople_form.html'
    fields = ['first_name', 'last_name']

class SalespeopleUpdateView(UpdateView):
    model = Salespeople
    template_name = 'salespeople/salespeople_form.html'
    fields = ['first_name', 'last_name']

class SalespeopleDeleteView(DeleteView):
    model = Salespeople
    template_name = 'salespeople/salespeople_confirm_delete.html'
    success_url = reverse_lazy('salespeople_list')

