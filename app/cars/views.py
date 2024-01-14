from django import forms
from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Car
from salespeople.models import Salespeople
from django.db.models import Count, Sum, Value, DecimalField

class CarForm(forms.ModelForm):
    """     
    Form for creating and updating Car instances.

    This form is used to gather data for a Car object, including the associated
    salesperson. The salesperson field is optional and can be dynamically updated 
    on the client side using JavaScript.
    """
    salesperson = forms.ModelChoiceField(
        queryset=Salespeople.objects.all(),
        required=False,  # Make it optional
        widget=forms.Select(attrs={'onchange': 'updateSalespersonDetails();'})  
    )
    class Meta:
        """
        Meta class for CarForm.

        Specifies the model to which the form is linked and the fields that are
        included in the form.
        """
        model = Car
        fields = [
            'id', 'make', 'model', 'year', 'color', 'price', 'mileage', 'sold', 'date_sold',
            'car_type', 'salesperson'
        ]
class HomePageView(TemplateView):
    """
    Displays the main landing page for the Car app.

    This view is the home page for the Car app. This class extends Django's generic class-based view, TemplateView, to render a static home page.

    Attributes:
        - `template_name`: The associated template 'cars/index.html' is used for rendering the home page.

    The resulting home page will display relevant information or content related to the Car app.
    """
    template_name = 'cars/index.html'
    
class CarListView(ListView):
    """     
    Displays a list of Car instances with filtering and ordering options.
    
    This class utilizes the Django generic class-based view, ListView, to create a view to handle the list of car objects from a queryset. It defines the model, template, and context_object_name attributes. A template associated with 'cars/list.html' is used to render with a list of car objects. The context_object_name attribute specifies the name of the context variable that will be used in the template. By default, the context variable is named after the model, in lowercase. In this case, the context variable will be named 'cars'.

    Attributes:
        - `model`: The model associated with this view is the Car model.
        - `template_name`: The associated template 'cars/list.html' is used for rendering the list of cars.
        - `context_object_name`: The context variable name is 'cars'.

    Methods:
        - `get_queryset()`: Returns a filtered and ordered queryset of Car instances.
        - `get_context_data()`: Adds filter options to the context.
    """
    model = Car
    template_name = 'cars/car_list.html'
    context_object_name = 'cars'

    def get_queryset(self):
        """     
        Returns a filtered and ordered queryset of Car instances.
        
        This method overrides the default get_queryset() method of the ListView class. It returns a filtered and ordered queryset of Car instances based on the query parameters in the request. 
        
        The queryset is filtered by the following query parameters:
            - `color_filter`: The color of the car.
            - `make_filter`: The make of the car.
            - `model_filter`: The model of the car.
            - `year_filter`: The year of the car.
            - `car_type_filter`: The type of the car.

        The queryset is ordered by the following query parameters:
            - `order`: The field to order by. The default ordering is by id.
            - `price_filter`: The price of the car.
            - `mileage_filter`: The mileage of the car.
        
        """
        queryset = super().get_queryset()
        order = self.request.GET.get('order')
        color_filter = self.request.GET.get('color_filter') 
        make_filter = self.request.GET.get('make_filter')
        model_filter = self.request.GET.get('model_filter')
        year_filter = self.request.GET.get('year_filter')
        car_type_filter = self.request.GET.get('car_type_filter')

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
        
        if order in ['mileage', '-mileage']:
            """
            Annotates the queryset with total mileage and orders it by mileage.

            The sum of 'mileage' values is calculated for Car instances in the queryset. If the car has no mileage, the value is defaulted to 0.00. The data type of the field is a decimal number. Then the sum is annotated to each car as 'total_sales_mileage'. The list of cars can then be ordered by mileage, either in ascending or descending order.

            Parameters:
                - order (str): The sorting order, either 'mileage' (ascending) or '-mileage' (descending).
            """
            queryset = queryset.annotate(
                total_sales_mileage=Sum('mileage', default=Value(0.00), output_field=DecimalField())
            ).order_by(order)

        if order in ['price', '-price']:
            """
            Annotates the queryset with total price and orders it by price.
            
            The sum of 'price' values is calculated for Car instances and each car is annotated with 'total_sales_price'. If the price is not available, the value is defaulted to 0.00. The data type of the field is a decimal number. The list of cars can then be ordered by price, either in ascending or descending order.
            
            Parameters:
                - order (str): The sorting order, either 'price' (ascending) or '-price' (descending).
            """
            queryset = queryset.annotate(
                total_sales_price=Sum('price', default=Value(0.00), output_field=DecimalField())
            ).order_by(order)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        """     
        Adds filter options to the context.

        This method retrieves distinct values for various car attributes (makes, models, colors, years, and car types) and adds them to the context dictionary. These values are used to provide filter options on the webpage.
        
        Args:
            **kwargs: Arbitrary keyword arguments.

        Returns:
            dict: A dictionary containing filter options for makes, models, colors, years, and car types added to the context.
        """
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
    """     
    Displays the details of a Car instance.
    
    This class utilizes the Django generic class-based view, DetailView, to create a view to handle the details of a car object from a queryset. It defines the model, template, and context_object_name attributes. A template associated with 'cars/detail.html' is used to render with a car object. The context_object_name attribute specifies the name of the context variable that will be used in the template. By default, the context variable is named after the model, in lowercase. In this case, the context variable will be named 'car'.
    
    Attributes:
        - `model`: The model associated with this view is the Car model.
        - `template_name`: The associated template 'cars/detail.html' is used for rendering the details of a car.
        - `context_object_name`: The context variable name is 'car'.
    """
    model = Car
    template_name = 'cars/car_detail.html'
    context_object_name = 'car'

@method_decorator(csrf_exempt, name='dispatch')
class CarCreateView(CreateView):
    """
    Creates a Car instance.
    
    This class utilizes the Django generic class-based view, CreateView, to create a view to handle the creation of a car object. It defines the model, template, form_class, and success_url attributes. A template associated with 'cars/car_form.html' is used to create a car object. The form_class attribute specifies the form to use for creating a car object. The success_url attribute specifies the URL to redirect to after a successful form submission. The decorator is used to exempt the view from the CSRF token requirement.
    
    Attributes:
        - `model`: The model associated with this view is the Car model.
        - `template_name`: The associated template 'cars/car_form.html' is used for rendering the form for creating a car.
        - `form_class`: The form used for creating a car is the CarForm.
        - `success_url`: The URL to redirect to after a successful form submission is the car list page.
        
    Methods:
        - `form_valid()`: Handles the form submission when creating a new Car instance.
    """
    model = Car
    form_class = CarForm  # Use the modified CarForm
    template_name = 'cars/car_form.html'
    success_url = reverse_lazy('car_list')

    def form_valid(self, form):
        """     
        Handles the form submission when creating a new Car instance.
        
        This method overrides the default form_valid() method of the CreateView class. It handles the form submission when creating a new Car instance. If there is a salesperson selected, first name and last name values are automatically validated by Django. If valid, the data is stored in the cleaned_data dictionary and saved. The Car object is saved.
        
        Args:
            form (CarForm): The form used for creating a car.
            
        Returns:
            HttpResponseRedirect: A redirect to the success URL.
            messages (Message): A success message is displayed.
        """
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
    """     
    Updates an existing Car instance.

    This class utilizes the Django generic class-based view, UpdateView, to create a view
    for updating an existing Car instance. It defines the model, template, fields, and
    success_url attributes.

    Attributes:
        - `model`: The model associated with this view is the Car model.
        - `template_name`: The associated template 'cars/car_form.html' is used for rendering the form for updating a car.
        - `fields`: The fields that can be updated in the Car instance. In this case, it includes:
            'id', 'make', 'model', 'year', 'color', 'price', 'mileage', 'sold', 'date_sold',
            'salesperson', and 'car_type'.
        - `success_url`: The URL to redirect to after a successful update, in this case, the car list.

    Methods:
        - `form_valid()`: Handles the form submission when updating a Car instance.
    """
    model = Car
    template_name = 'cars/car_form.html'
    fields = ['id', 'make', 'model', 'year', 'color', 'price', 'mileage', 'sold', 'date_sold', 'salesperson', 'car_type']  # Added 'car_type'
    success_url = reverse_lazy('car_list')

    def form_valid(self, form):
        """
        Handles the form submission when updating a Car instance.

        This method overrides the default form_valid() method of the UpdateView class.
        It handles the form submission when updating a Car instance. If the car is marked
        as sold and not already marked as sold with a salesperson, it calls the 'mark_as_sold'
        method to update the car's status. It saves the Car object. 

        Args:
            form (CarForm): The form used for updating a car.

        Returns:
            HttpResponseRedirect: A redirect to the success URL
            messages (Message): A success message is displayed.
        """
        car = form.save(commit=False)

        """Check if the car is being marked as sold and not already marked"""
        if car.sold and not car.date_sold and car.salesperson:
            car.mark_as_sold(car.salesperson)

        car.save()
        messages.success(self.request, 'Car updated successfully.')
        return super().form_valid(form)

class CarDeleteView(DeleteView):
    """
    Deletes an existing Car instance.
    
    This class utilizes the Django generic class-based view, DeleteView, to create a view to handle the deletion of a car object. It defines the model, template, and success_url attributes. A template associated with 'cars/car_confirm_delete.html' is used to confirm the deletion of a car object. The success_url attribute specifies the URL to redirect to after a successful deletion.
    
    Attributes:
        - `model`: The model associated with this view is the Car model.
        - `template_name`: The associated template 'cars/car_confirm_delete.html' is used for rendering the confirmation page for deleting a car.
        - `success_url`: The URL to redirect to after a successful deletion is the car list page.
    """
    model = Car
    template_name = 'cars/car_confirm_delete.html'
    success_url = reverse_lazy('car_list')
    
    def delete(self, request, *args, **kwargs):
        """     
        Deletes the Car instance.
        
        This method overrides the default delete() method of the DeleteView class. It deletes the Car instance, redirects to the success URL and displays a success message.
        
        Args:
            request (HttpRequest): The HTTP request.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
            
        Returns:
            HttpResponseRedirect: A redirect to the success URL.
            messages (Message): A success message is displayed.
        """
        messages.success(self.request, 'Car deleted successfully.')
        return super().delete(request, *args, **kwargs)

def mark_car_as_not_sold(request, car_id):
    """
    Sets the sold status of a car to False.
    
    This function sets the sold status of a car to False and clears the date_sold and salesperson fields. It is used to mark a car as not sold. It is called when the 'Mark as Not Sold' button is clicked on the salesperson detail page. The try block attempts to save the car instance. If successful, a success message is displayed. Otherwise, an error message is displayed.
    It redirects back to the salesperson detail page if the car was sold by a salesperson. Otherwise, it redirects back to the car list page.
    
    Args:
        request (HttpRequest): The HTTP request.
        car_id (int): The id of the car to mark as not sold.
        
    Returns:
        HttpResponseRedirect: A redirect to the car list or salesperson detail page. 
        messages (Message): A success or error message is displayed.
    """
    car = get_object_or_404(Car, pk=car_id)

    car.sold = False
    car.date_sold = None  
    car.salesperson = None 

    # Save the car instance
    try:
        car.save()
        messages.success(request, 'Car marked as "NOT SOLD".')
    except forms.ValidationError as e:
        messages.error(request, 'Error: ' + str(e))

    # Redirect back to a relevant page, such as the car list or salesperson detail
    return redirect('salespeople_detail', salesperson_id=car.salesperson_id) if car.salesperson_id else redirect('car_list')
