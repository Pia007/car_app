from django import forms
from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Car
from salespeople.models import Salespeople
from django.db.models import Count, Sum, Value, DecimalField

class CarForm(forms.ModelForm):
    salesperson = forms.ModelChoiceField(
        queryset=Salespeople.objects.all(),
        required=False,  # Make it optional
        widget=forms.Select(attrs={'onchange': 'updateSalespersonDetails();'})  
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

    def get_queryset(self):
        queryset = super().get_queryset()
        order = self.request.GET.get('order')
        color_filter = self.request.GET.get('color_filter') 
        make_filter = self.request.GET.get('make_filter')
        model_filter = self.request.GET.get('model_filter')
        year_filter = self.request.GET.get('year_filter')
        car_type_filter = self.request.GET.get('car_type_filter')
        price_filter = self.request.GET.get('price_filter')

        # Apply color filter if a color is selected
        if color_filter:
            queryset = queryset.filter(color=color_filter)

        if make_filter:
            queryset = queryset.filter(make=make_filter)

        if model_filter:
            queryset = queryset.filter(model=model_filter)

        if year_filter:
            queryset = queryset.filter(year=year_filter)

        if car_type_filter:
            queryset = queryset.filter(car_type=car_type_filter)
        
        if price_filter:
            queryset = queryset.filter(price=price_filter)
            
        #order by mileage without decimals
        if order in ['mileage', '-mileage']:
            # Annotate with total sales, defaulting to 0.00 if there are no sales
            queryset = queryset.annotate(
                total_sales_mileage=Sum('mileage', default=Value(0.00), output_field=DecimalField())
            ).order_by(order)

        if order in ['price', '-price']:
            # Annotate with total sales, defaulting to 0.00 if there are no sales
            queryset = queryset.annotate(
                total_sales_price=Sum('price', default=Value(0.00), output_field=DecimalField())
            ).order_by(order)
            

    
        return queryset
    
    def get_context_data(self, **kwargs):   
        context = super().get_context_data(**kwargs)
        
        makes = Car.objects.values_list('make', flat=True).distinct()
        models = Car.objects.values_list('model', flat=True).distinct()
        colors = Car.objects.values_list('color', flat=True).distinct()
        years = Car.objects.values_list('year', flat=True).distinct()
        car_types = Car.objects.values_list('car_type', flat=True).distinct()
        
        context['makes'] = makes
        context['models'] = models
        context['colors'] = colors
        context['years'] = years
        context['car_types'] = car_types
        
        return context

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
        
        if selected_salesperson:
            selected_salesperson.first_name = form.cleaned_data['salesperson'].first_name
            selected_salesperson.last_name = form.cleaned_data['salesperson'].last_name
            
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

def mark_car_as_not_sold(request, car_id):
    car = get_object_or_404(Car, pk=car_id)

    # Update the car status
    car.sold = False
    car.date_sold = None  # Clear the date_sold field
    car.salesperson = None  # Clear the salesperson field

    # Save the car instance
    try:
        car.save()
        messages.success(request, 'Car marked as not sold successfully.')
    except forms.ValidationError as e:
        messages.error(request, 'Error: ' + str(e))

    # Redirect back to a relevant page, such as the car list or salesperson detail
    return redirect('salespeople_detail', salesperson_id=car.salesperson_id) if car.salesperson_id else redirect('car_list')
