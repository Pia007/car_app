from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView  
from django.urls import reverse_lazy
from .models import Customer 


class CustomerListView(ListView):
    model = Customer
    template_name = 'customers/customer_list.html'
    context_object_name = 'customers'

class CustomerDetailView(DetailView):
    model = Customer
    template_name = 'customers/customer_detail.html'
    context_object_name = 'customer'

@method_decorator(csrf_exempt, name='dispatch')
class CustomerCreateView(CreateView):
    model = Customer
    template_name = 'customers/customer_form.html'
    fields = ['first_name', 'last_name', 'email', 'phone_number', 'address', 'city', 'state', 'zip_code', 'handled_by', 'purchased_cars']  # Include 'handled_by' and 'purchased_cars'il', 'phone_number', 'address', 'city', 'state', 'zip_code']  # Updated fields
    success_url = reverse_lazy('customer_list')

@method_decorator(csrf_exempt, name='dispatch')
class CustomerUpdateView(UpdateView):
    model = Customer
    template_name = 'customers/customer_form.html'
    fields = ['first_name', 'last_name', 'email', 'phone_number', 'address', 'city', 'state', 'zip_code', 'handled_by', 'purchased_cars']  # Include 'handled_by' and 'purchased_cars'
    success_url = reverse_lazy('customer_list')

class CustomerDeleteView(DeleteView):
    model = Customer
    template_name = 'customers/customer_confirm_delete.html'
    success_url = reverse_lazy('customer_list')


