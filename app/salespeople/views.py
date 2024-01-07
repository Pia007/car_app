from django import forms
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from cars.models import Car
from .models import Salespeople
from django.db.models import Count, Sum, Value, DecimalField


class SalespersonForm(forms.ModelForm):
    unsold_cars = forms.ModelChoiceField(
        queryset=Car.objects.filter(sold=False),
        required=False,
        label='Unsold Cars'
    )
    class Meta:
        model = Salespeople
        fields = [
            'first_name', 'last_name', 'email', 'phone_number', 'unsold_cars'
        ] 

#Filter
class SalespeopleFilterForm(forms.Form):
    min_commission = forms.DecimalField(required=False)
    max_commission = forms.DecimalField(required=False)
    min_total_sales = forms.DecimalField(required=False)
    max_total_sales = forms.DecimalField(required=False)
    min_cars_sold = forms.IntegerField(required=False)
    max_cars_sold = forms.IntegerField(required=False)

class SalespeopleListView(ListView):
    model = Salespeople
    template_name = 'salespeople/salespeople_list.html'
    context_object_name = 'salespeople'

    def get_queryset(self):
        queryset = super().get_queryset()
        order = self.request.GET.get('order')

        if order in ['total_sales_amount', '-total_sales_amount']:
            # Annotate with total sales, defaulting to 0.00 if there are no sales
            queryset = queryset.annotate(
                total_sales_amount=Sum('sold_cars__price', default=Value(0.00), output_field=DecimalField())
            ).order_by(order)
        elif order in ['cars_sold_count', '-cars_sold_count']:
            # Annotate with count of sold cars
            queryset = queryset.annotate(
                cars_sold_count=Count('sold_cars')
            ).order_by(order)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = SalespeopleFilterForm(self.request.GET or None)
        return context

class SalespeopleDetailView(DetailView):
    model = Salespeople
    template_name = 'salespeople/salespeople_detail.html'
    context_object_name = 'salespeople'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        salesperson = self.get_object()
        context['total_commission'] = salesperson.total_commission()
        return context

@method_decorator(csrf_exempt, name='dispatch')
class SalespeopleCreateView(CreateView):
    model = Salespeople
    form_class = SalespersonForm
    template_name = 'salespeople/salespeople_form.html'
    success_url = reverse_lazy('salespeople_list')

class SalespeopleUpdateView(UpdateView):
    model = Salespeople
    form_class = SalespersonForm
    template_name = 'salespeople/salespeople_form.html'
    success_url = reverse_lazy('salespeople_list')

    def form_valid(self, form):
        salesperson = form.save(commit=False)

        selected_car = form.cleaned_data.get('unsold_cars')
        if selected_car:
            # Mark the car as sold and associate it with this salesperson
            selected_car.sold = True
            selected_car.salesperson = salesperson
            selected_car.save()

        salesperson.save()

        messages.success(self.request, 'Salesperson updated successfully.')
        return super().form_valid(form)

class SalespeopleDeleteView(DeleteView):
    model = Salespeople
    template_name = 'salespeople/salespeople_confirm_delete.html'
    success_url = reverse_lazy('salespeople_list')