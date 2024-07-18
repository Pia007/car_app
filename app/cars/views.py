import re
from django import forms
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Car
from salespeople.models import Salespeople
from django.db.models import Sum, Value, DecimalField

class CarForm(forms.ModelForm):
    """     
    Form for creating and updating Car instances.

    This class creates a form for creating and updating a Car object, including the associated
    salesperson. The salesperson field is optional and can be dynamically updated 
    on the client side using JavaScript.
    """
    salesperson = forms.ModelChoiceField(
        queryset=Salespeople.objects.all(),
        required=False,
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
            'id', 'make', 'model', 'year', 'car_color', 'price', 'mileage', 'sold', 'date_sold',
            'car_type', 'salesperson'
        ]

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price < 0:
            raise ValidationError('Price cannot be negative.')
        return price

    def clean_year(self):
        year = self.cleaned_data.get('year')
        if year is not None and year < 0:
            raise ValidationError('Year cannot be negative.')
        return year

    def clean_mileage(self):
        mileage = self.cleaned_data.get('mileage')
        if mileage is not None and mileage < 0:
            raise ValidationError('Mileage cannot be negative.')
        return mileage

    def clean_model(self):
        model = self.cleaned_data.get('model')
        if model:
            if not re.match(r'^[a-zA-Z0-9 ]*$', model):
                raise ValidationError(
                    'Model can only contain alphanumeric characters and spaces.')
            if len(model) > 12:
                raise ValidationError('Model cannot exceed 12 characters.')
        return model

    def clean_make(self):
        make = self.cleaned_data.get('make')
        if make:
            if not re.match(r'^[a-zA-Z0-9 ]*$', make):
                raise ValidationError(
                    'Make can only contain alphanumeric characters and spaces.')
            if len(make) > 12:
                raise ValidationError('Make cannot exceed 12 characters.')
        return make
        
class HomePageView(TemplateView):
    """
    Displays the main landing page for the Car app.

    This class is the home page for the Car app. It extends Django's generic class-based view, TemplateView, to render a static home page.

    Attributes:
        - template_name: The associated template 'cars/index.html' is used for rendering the home page.

    The resulting home page will display relevant information or content related to the Car app.
    """
    template_name = 'cars/index.html'
    
class CarListView(ListView):
    """     
    Displays a list of Car instances with filtering and ordering options.
    
    This class extends ListView and is used to display a list of cars in the web application. It retrieves a queryset of cars from the database and renders it in a template. It also provides filtering and ordering options to filter.

    Attributes:
        - model (Car): The model associated with this view is the Car model.
        - template_name (str): The associated template 'cars/list.html' is used for rendering the list of cars.
        - context_object_name (str): The context variable name is 'cars'.
        - paginate_by (int): The number of items per page.

    Methods:
        - get_queryset(): Returns a filtered and ordered queryset of Car instances.
        - get_context_data(): Adds filter options to the context.
    """
    model = Car
    template_name = 'cars/car_list.html'
    context_object_name = 'cars'
    paginate_by = 7  # the number of items per page

    def get_queryset(self):
        """     
        Overrides the default get_queryset() method of the ListView class. It returns a filtered and ordered queryset of Car instances based on the query parameters in the request. 
        
        The queryset is filtered by the following query parameters:
            - car_color_filter: The color of the car.
            - make_filter: The make of the car.
            - model_filter: The model of the car.
            - year_filter: The year of the car.
            - car_type_filter: The type of the car.

        The queryset is ordered by the following query parameters:
            - order: The field to order by. The default ordering is by id.
            - price_filter: The price of the car.
            - mileage_filter: The mileage of the car.
        """
        queryset = super().get_queryset()
        order = self.request.GET.get('order')
        car_color_filter = self.request.GET.get('car_color_filter') 
        make_filter = self.request.GET.get('make_filter')
        model_filter = self.request.GET.get('model_filter')
        year_filter = self.request.GET.get('year_filter')
        car_type_filter = self.request.GET.get('car_type_filter')

        if car_color_filter:
            queryset = queryset.filter(car_color=car_color_filter)

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
            The sum of 'mileage' values is calculated for Car instances in the queryset. If the car has no mileage, the value is defaulted to 0.00. The data type of the field is a decimal number. Then the sum is annotated to each car as 'total_sales_mileage'. The list of cars can then be ordered by mileage, either in ascending or descending order.

            Parameters:
                order (str): The sorting order, either 'mileage' (ascending) or '-mileage' (descending).
                
            Returns:
                querySet: The annotated and sorted queryset based on the specified order.
            """
            queryset = queryset.annotate(
                total_sales_mileage=Sum('mileage', default=Value(0.00), output_field=DecimalField())
            ).order_by(order)

        if order in ['price', '-price']:
            """
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
        Retrieves distinct values for various car attributes (makes, models, car colors, years, and car types) and adds them to the context dictionary. These values are used to provide filter options on the webpage. Pagination is also added to allow for pagination of the list of cars.
        
        Args:
            **kwargs: Arbitrary keyword arguments.

        Returns:
            dict: A dictionary containing filter options for makes, models, car colors, years, and car types added to the context.
        """
        context = super().get_context_data(**kwargs)
        
        makes = Car.objects.values_list('make', flat=True).distinct()
        models = Car.objects.values_list('model', flat=True).distinct()
        car_colors = Car.objects.values_list('car_color', flat=True).distinct()
        years = Car.objects.values_list('year', flat=True).distinct()
        car_types = Car.objects.values_list('car_type', flat=True).distinct()
        
        context['makes'] = makes
        context['models'] = models
        context['car_colors'] = car_colors
        context['years'] = years
        context['car_types'] = car_types
        
        paginator = Paginator(self.get_queryset(), self.paginate_by)  # create a Paginator object
        page = self.request.GET.get('page')

        try:
            cars = paginator.page(page)
        except PageNotAnInteger:
            # if page is not an integer, deliver first page
            cars = paginator.page(1)
        except EmptyPage:
            # if page is out of range, deliver last page of results
            cars = paginator.page(paginator.num_pages)

        context['page_obj'] = cars
        
        return context

class CarDetailView(DetailView):
    """     
    Displays the details of a Car instance.
    
    This class extends DetailView and is used to display the details of a car in the web application. It retrieves a Car object from the database and renders it in a template. 
    
    Attributes:
        - model: The model associated with this view is the Car model.
        - template_name: The associated template 'cars/detail.html' is used for rendering the details of a car.
        - context_object_name: The context variable name is 'car'.
    """
    model = Car
    template_name = 'cars/car_detail.html'
    context_object_name = 'car'

@method_decorator(csrf_exempt, name='dispatch')
class CarCreateView(CreateView):
    """
    Creates a Car instance.
    
    This class extends CreateView to create a Car instance. It renders a form for creating a new Car object and handles the form submission. It also provides a success message upon successful form submission. It utilizes Django's reverse lookup function, reverse_lazy(), to retrieve the URL for the car list page and redirect to it after a successful creation. The decorator @method_decorator(csrf_exempt, name='dispatch') is used to exempt the view from the CSRF token requirement.
    
    Attributes:
        - model: The model associated with this view is the Car model.
        - template_name: The associated template 'cars/car_form.html' is used for rendering the form for creating a car.
        - form_class: The form used for creating a car is the CarForm.
        - success_url: The URL to redirect to after a successful form submission is the car list page.
        
    Methods:
        - form_valid(): Handles the form submission when creating a new Car instance.
    """
    model = Car
    form_class = CarForm
    template_name = 'cars/car_form.html'
    success_url = reverse_lazy('car_list')

    def form_valid(self, form):
        """     
        Overrides the default form_valid() method of the CreateView class. It handles the form submission when creating a new Car instance. If there is a salesperson selected, first name and last name values are automatically validated by Django. If valid, the data is stored in the cleaned_data dictionary and saved, then reverse_lazy() is used to retrieve the URL for the car list page and redirect to it after a successful creation. A success message is also displayed.
        
        Args:
            form (CarForm): The form used for creating a car.
            
        Returns:
            HttpResponse: A redirect to the success URL.
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
    Updates a Car instance.

    This class extends the UpdateView, to create a view for updating an existing Car instance. It utilizes Django's reverse lookup function, reverse_lazy(), to retrieve the URL for the car list page and redirect to it after a successful update. It overrides the form_valid() method to handle the form submission when updating a Car instance. It also provides a success message upon successful form submission. The decorator @method_decorator(csrf_exempt, name='dispatch') is used to exempt the view from the CSRF token requirement.

    Attributes:
        - model: The model associated with this view is the Car model.
        - template_name: The associated template 'cars/car_form.html' is used for rendering the form for updating a car.
        - fields: The fields that can be updated in the Car instance. In this case, it includes:
            'id', 'make', 'model', 'year', 'color', 'price', 'mileage', 'sold', 'date_sold',
            'salesperson', and 'car_type'.
        - success_url: The URL to redirect to after a successful update, in this case, the car list.

    Methods:
        - form_valid(): Handles the form submission when updating a Car instance.
    """
    model = Car
    template_name = 'cars/car_form.html'
    fields = ['id', 'make', 'model', 'year', 'car_color', 'price', 'mileage', 'sold', 'date_sold', 'salesperson', 'car_type']  
    success_url = reverse_lazy('car_list')

    def form_valid(self, form):
        """
        Overrides the default form_valid() method of the UpdateView class.
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
    
    This class extends DeleteView to create a view to handle the deletion of a car object. A template associated with 'cars/car_confirm_delete.html' is used to confirm the deletion of a car object. When a car is deleted, if it was sold by a salesperson, the car is removed from the salesperson's details. It also provides a success message upon successful deletion.
    The success_url attribute specifies the URL to redirect to after a successful deletion.
    
    Attributes:
        - model: The model associated with this view is the Car model.
        - template_name: The associated template 'cars/car_confirm_delete.html' is used for rendering the confirmation page for deleting a car.
        - success_url: The URL to redirect to after a successful deletion is the car list page.
        
    Methods:
        - delete(): Deletes the Car instance.
    """
    model = Car
    template_name = 'cars/car_confirm_delete.html'
    success_url = reverse_lazy('car_list')
    
    def delete(self, request, *args, **kwargs):
        """
        Overrides the default delete() method of the DeleteView class. It deletes the Car instance, redirects to the success URL and displays a success message.
        
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
    Sets the sold status of a car to False and clears the date_sold and salesperson fields when the 'Mark as Not Sold' button is clicked on the salesperson detail page. The try block attempts to save the car instance. If successful, a success message is displayed. Otherwise, an error message is displayed. It redirects back to the salesperson detail page if the car was sold by a salesperson. Otherwise, it redirects back to the car list page.
    
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
