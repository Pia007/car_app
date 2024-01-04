from django import forms
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Car
from salespeople.models import Salespeople

class CarForm(forms.ModelForm):
    salesperson = forms.ModelChoiceField(
        queryset=Salespeople.objects.all(),
        required=False,  # Make it optional
        widget=forms.Select(attrs={'onchange': 'updateSalespersonDetails();'})  # Add JavaScript to trigger an update
    )
    class Meta:
        model = Car
        fields = [
            'make', 'model', 'year', 'color', 'price', 'mileage', 'sold', 'date_sold',
            'car_type', 'salesperson'  # Include the salesperson field
        ]

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
    form_class = CarForm  # Use the modified CarForm
    template_name = 'cars/car_form.html'
    success_url = reverse_lazy('car_list')

    def form_valid(self, form):
        # Get the selected salesperson from the form
        selected_salesperson = form.cleaned_data['salesperson']
        
        # Update the salesperson's details (modify this based on your needs)
        if selected_salesperson:
            selected_salesperson.first_name = form.cleaned_data['salesperson'].first_name
            selected_salesperson.last_name = form.cleaned_data['salesperson'].last_name
            # Add more fields as needed
            
            selected_salesperson.save()
        
        # Save the Car object
        response = super().form_valid(form)
        messages.success(self.request, 'Car created successfully.')
        return response

@method_decorator(csrf_exempt, name='dispatch')
class CarUpdateView(UpdateView):
    model = Car
    template_name = 'cars/car_form.html'
    fields = ['make', 'model', 'year', 'color', 'price', 'mileage', 'sold', 'date_sold', 'salesperson', 'car_type']  # Added 'car_type'
    success_url = reverse_lazy('car_list')

    def form_valid(self, form):
        car = form.save(commit=False)

        # Check if the car is being marked as sold and not already marked
        if car.sold and not car.date_sold and car.salesperson:
            car.mark_as_sold(car.salesperson)

        car.save()
        messages.success(self.request, 'Car updated successfully.')
        return super().form_valid(form)

class CarDeleteView(DeleteView):
    model = Car
    template_name = 'cars/car_confirm_delete.html'
    success_url = reverse_lazy('car_list')
