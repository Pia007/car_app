from django.utils import timezone
from django import forms
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from cars.models import Car
from .models import Salespeople
from django.db.models import Case, When, Value, Sum, BooleanField, Count

class SalespersonForm(forms.ModelForm):
    """
    Form for creating and updating Salespeople instances.

    This class creates a form for creating and updating Salespeople instances. It contains fields for the first name, last name, email, phone number, and unsold cars of the salesperson.
    """

    unsold_cars = forms.ModelChoiceField(
        queryset=Car.objects.filter(sold=False),
        required=False,
        label='Unsold Cars'
    )
    class Meta:
        """
        Meta class for SalespersonForm.

        Contains the metadata for the SalespersonForm class. It specifies the model and fields for the form.
        """
        model = Salespeople
        fields = [
            'first_name', 'last_name', 'email', 'phone_number', 'unsold_cars'
        ]

class SalespeopleListView(ListView):
    """
    Displays a list of salespeople.

    This class extends Django's built-in ListView and is used to display a list of salespeople in a web application. It retrieves a queryset of salespeople from the database and renders them using a specified template.

    Attributes:
        model (Salespeople): The model for the view.
        template_name (str): The template for the view.
        context_object_name (str): The context object name for the view.
        paginate_by (int): The number of items per page.

    Methods:
        get_queryset: Returns the queryset for the view.
        get_context_data: Returns the context data for the view.
    """
    model = Salespeople
    template_name = 'salespeople/salespeople_list.html'
    context_object_name = 'salespeople'
    paginate_by = 7

    def get_queryset(self):
        """
        Overrides the default get_queryset method of the ListView class. It returns an ordered queryset of the Salespeople instances. The queryset is ordered by the total sales amount and the number of cars sold by the salespeople.
        """
        queryset = super().get_queryset()
        order = self.request.GET.get('order')

        if order in ['total_sales_amount', '-total_sales_amount']:
            """
            Checks if the provided 'order' parameter is 'total_sales_amount' or '-total_sales_amount'. Depending on the order,
            it annotates the queryset with 'total_sales_amount', which represents the sum of prices of sold cars associated with each instance.

            It also annotates the queryset with 'has_sales' as a boolean field, indicating whether there are any sales associated with each instance.

            - `total_sales_amount`: The annotation field storing the total sales amount.
            - `has_sales`: The annotation field indicating whether the instance has any sales.

            Parameters:
                order (str): The sorting order, either 'total_sales_amount' or '-total_sales_amount'.

            Returns:
                QuerySet: The annotated and sorted queryset based on the specified order.
            """
            queryset = queryset.annotate(
                total_sales_amount=Sum('sold_cars__price')
            )

            """ Takes the queryset and annotates it with 'has_sales' as a boolean field, indicating whether there are any sales associated with each instance. """
            queryset = queryset.annotate(
                has_sales=Case(
                    When(total_sales_amount__gt=0, then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField(),
                )
            )

            if order.startswith('-'):
                queryset = queryset.order_by(
                    '-has_sales', '-total_sales_amount')
            else:
                queryset = queryset.order_by('has_sales', 'total_sales_amount')
                queryset = queryset.annotate(
                    total_sales_amount=Sum('sold_cars__price')
                )

                queryset = queryset.annotate(
                    has_sales=Case(
                        When(total_sales_amount__gt=0, then=Value(True)),
                        default=Value(False),
                        output_field=BooleanField(),
                    )
                )

            if order.startswith('-'):
                queryset = queryset.order_by(
                    '-has_sales', '-total_sales_amount')
            else:
                queryset = queryset.order_by('has_sales', 'total_sales_amount')

        elif order in ['cars_sold_count', '-cars_sold_count']:
            """
            Checks if the provided 'order' parameter is 'cars_sold_count' or '-cars_sold_count'.
            If so, it annotates the queryset with 'cars_sold_count', representing the count of sold cars associated with each instance.
            """
            queryset = queryset.annotate(
                cars_sold_count=Count('sold_cars')
            ).order_by(order)

        return queryset

    def get_context_data(self, **kwargs):
        """ 
        Adds the order to the context data and adds pagination to allow the user to navigate through the pages of the list of salespeople.
        """
        context = super().get_context_data(**kwargs)
        
        # Create a Paginator object
        paginator = Paginator(self.get_queryset(), self.paginate_by)  
        page = self.request.GET.get('page')

        try:
            salespeople = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page
            salespeople = paginator.page(1)
        except EmptyPage:
            # If page is out of range, deliver last page of results
            salespeople = paginator.page(paginator.num_pages)

        context['page_obj'] = salespeople
        
        return context

class SalespeopleDetailView(DetailView):
    """
    Displays the details of a Salespeople instance.

    This class extends Django's built-in DetailView and is used to display the details of a salesperson in a web application. It retrieves a Salespeople instance from the database and renders it using a specified template. It also calculates the total commission earned by the salesperson and adds it to the context data.

    Attributes:
        model (Salespeople): The model for the view.
        template_name (str): The template for the view.
        context_object_name (str): The context object name for the view.

    Methods:
        get_context_data: Returns the context data for the view.

    """
    model = Salespeople
    template_name = 'salespeople/salespeople_detail.html'
    context_object_name = 'salespeople'

    def get_context_data(self, **kwargs):
        """
        Overrides the default implementation to include additional context data.
        It calculates the total commission earned by the current salesperson and adds it to the context.

        Returns:
            dict: A dictionary containing the context data with 'total_commission' as a key.
        """
        context = super().get_context_data(**kwargs)
        salesperson = self.get_object()
        context['total_commission'] = salesperson.total_commission()
        return context

@method_decorator(csrf_exempt, name='dispatch')
class SalespeopleCreateView(CreateView):
    """
    Creates a Salespeople instance.

    Extends CreateView to create a Salespeople instance. When the salesperson is created, if there was a car selected, the car object is automatically validated. If valid, the car is marked as sold, assigned the current date as the date_sold and is assigned it to the salesperson. It utilizes Django's reverse_lazy() function to redirect to the salespeople list page after a successful creation. The decorator is used to exempt the view from the CSRF token requirement.

    Attributes:
        model (Salespeople): The model for the view.
        form_class (SalespersonForm): The form class for the view.
        template_name (str): The template for the view.
        success_url (str): The URL to redirect to after a successful form submission.

    Methods:
        form_valid: Validates the form data.

    """
    model = Salespeople
    form_class = SalespersonForm
    template_name = 'salespeople/salespeople_form.html'
    success_url = reverse_lazy('salespeople_list')

    def form_valid(self, form):
        """
        Validates the data submitted when creating a Salespeople instance.

        This method overrides the default implementation to validate the Salesperson form data. It also marks the selected car as sold, assigns the current date as the date_sold and assigns it to the salesperson.

        Args:
            form (SalespersonForm): The form instance to validate.

        Returns:
            HttpResponseRedirect: A redirect to the success URL.
            messages (Message): The messages for a valid form.
        """
        response = super().form_valid(form)
        messages.success(self.request, 'Salesperson created successfully.')
        return response


@method_decorator(csrf_exempt, name='dispatch')
class SalespeopleUpdateView(UpdateView):
    """
    Updates a Salespeople instance.

    This class extends UpdateView class and updates a Salespeople instance. It utilizes Django's reverse_lazy() function to redirect to the salespeople list page after a successful update. It also allows the user to select and unsold car and assign it to the salesperson. The decorator is used to exempt the view from the CSRF token requirement.

    Attributes:
        model (Salespeople): The model for the view.
        form_class (SalespersonForm): The form class for the view.
        template_name (str): The template for the view.
        success_url (str): The URL to redirect to after a successful form submission.
    """
    model = Salespeople
    form_class = SalespersonForm
    template_name = 'salespeople/salespeople_form.html'
    success_url = reverse_lazy('salespeople_list')

    def get_context_data(self, **kwargs):
        """
        Returns context data for the view.
        """
        context = super().get_context_data(**kwargs)
        # Add this line to include the is_edit flag in the context
        context['is_edit'] = True
        return context

    def form_valid(self, form):
        """
        This method overrides the default implementation to validate the Salespeople form data. If there is a car selected, the car object is automatically validated. If valid, the car is marked as sold, assigned the current date as the date_sold and is assigned it to the salesperson.

        Args:
            form (SalespersonForm): The form instance to validate.

        Returns:
            HttpResponse: The HTTP response for a valid form.
            messages: The messages for a valid form.
        """
        salesperson = form.save(commit=False)

        # Get the selected car object from the form
        selected_car = form.cleaned_data.get('unsold_cars')

        if selected_car:
            selected_car.sold = True
            selected_car.date_sold = timezone.now()
            selected_car.salesperson = salesperson
            selected_car.save()

        salesperson.save()
        messages.success(self.request, 'Salesperson updated successfully.')
        return super().form_valid(form)

class SalespeopleDeleteView(DeleteView):
    """
    Deletes an existing Salespeople instance.

    This extends DeleteView class and deletes a Salespeople instance. When the salesperson is deleted, if there is a list of cars sold by the salesperson, the cars remain marked as sold but are no longer associated with the salesperson. The user is asked to confirm the deletion of the salesperson. If the user confirms the deletion, the salesperson is deleted and the user is redirected to the salespeople list page. If the user cancels the deletion, the user is redirected to the salespeople detail page.

    Attributes:
        model (Salespeople): The model for the view.
        template_name (str): The template for the view.
        success_url (str): The URL to redirect to after a successful form submission.

    Methods:
        delete(): Deletes the Salespeople instance.
    """
    model = Salespeople
    template_name = 'salespeople/salespeople_confirm_delete.html'
    success_url = reverse_lazy('salespeople_list')

    def delete(self, request, *args, **kwargs):
        """
        Overrides the default delete() method of the DeleteView class. It deletes the Salespeople instance, redirects to the success URL and displays a success message.
        """
        response = super().delete(request, *args, **kwargs)
        messages.success(self.request, 'Salesperson deleted successfully.')
        return response
