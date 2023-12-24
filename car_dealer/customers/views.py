# from django.shortcuts import render, get_object_or_404
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from rest_framework.parsers import JSONParser
# from rest_framework import status
# from rest_framework.response import 

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView  
from django.urls import reverse_lazy
from .models import Customer 

# from customers.models import Customer
# from customers.serializers import CustomerSerializer


class CustomerListView(ListView):
    model = Customer
    template_name = 'customers/customer_list.html'
    context_object_name = 'customers'

class CustomerDetailView(DetailView):
    model = Customer
    template_name = 'customers/customer_detail.html'
    context_object_name = 'customers'

class CustomerCreateView(CreateView):
    model = Customer
    template_name = 'customers/customer_form.html'
    fields = ['first_name', 'last_name']

class CustomerUpdateView(UpdateView):
    model = Customer
    template_name = 'customers/customer_form.html'
    fields = ['first_name', 'last_name']

class CustomerDeleteView(DeleteView):
    model = Customer
    template_name = 'customers/customer_confirm_delete.html'
    success_url = reverse_lazy('customer_list')


