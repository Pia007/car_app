from django import forms
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from cars.models import Car
from .models import Salespeople


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
        ]  # other fiel

class SalespeopleListView(ListView):
    model = Salespeople
    template_name = 'salespeople/salespeople_list.html'
    context_object_name = 'salespeople'

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