from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Salespeople

class SalespeopleListView(ListView):
    model = Salespeople
    template_name = 'salespeople/salespeople_list.html'
    context_object_name = 'salespeople'

class SalespeopleDetailView(DetailView):
    model = Salespeople
    template_name = 'salespeople/salespeople_detail.html'
    context_object_name = 'salespeople'

@method_decorator(csrf_exempt, name='dispatch')
class SalespeopleCreateView(CreateView):
    model = Salespeople
    template_name = 'salespeople/salespeople_form.html'
    fields = ['first_name', 'last_name']
    success_url = reverse_lazy('salespeople_list')

class SalespeopleUpdateView(UpdateView):
    model = Salespeople
    template_name = 'salespeople/salespeople_form.html'
    fields = ['first_name', 'last_name']
    success_url = reverse_lazy('salespeople_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Salesperson updated successfully.')
        return response

class SalespeopleDeleteView(DeleteView):
    model = Salespeople
    template_name = 'salespeople/salespeople_confirm_delete.html'
    success_url = reverse_lazy('salespeople_list')

