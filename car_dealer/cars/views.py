from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Car


class CarIndexView(ListView):
    model = Car
    template_name = 'cars/index.html'
    context_object_name = 'cars'

class CarListView(ListView):
    model = Car
    template_name = 'cars/car_list.html'
    context_object_name = 'cars'

class CarDetailView(DetailView):
    model = Car
    template_name = 'cars/car_detail.html'
    context_object_name = 'car'

@method_decorator(csrf_exempt, name='dispatch')
class CarCreateView(CreateView):
    model = Car
    template_name = 'cars/car_form.html'
    fields = ['make', 'model', 'year', 'color', 'price', 'mileage', 'sold', 'date_sold', 'salespeople']
    success_url = reverse_lazy('car_list')  # Redirect to the car list after creation

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Car created successfully.')
        return response

class CarUpdateView(UpdateView):
    model = Car
    template_name = 'cars/car_form.html'
    fields = ['make', 'model', 'year', 'color', 'price', 'mileage', 'sold', 'date_sold', 'salespeople']

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Car updated successfully.')
        return response

class CarDeleteView(DeleteView):
    model = Car
    template_name = 'cars/car_confirm_delete.html'
    success_url = reverse_lazy('car_list')  # Ensure this matches your URL name for car list

