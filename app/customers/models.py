from django.db import models
from django.core.validators import EmailValidator
from phonenumber_field.modelfields import PhoneNumberField

class Customer(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True, validators=[EmailValidator()])
    phone_number = PhoneNumberField(blank=True, null=True)  # Updated field
    address = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    zip_code = models.CharField(max_length=10, blank=True, null=True)
    purchased_cars = models.ManyToManyField('cars.Car', blank=True, related_name='customers_purchased')
    handled_by = models.ForeignKey('salespeople.Salespeople', on_delete=models.SET_NULL, null=True, blank=True, related_name='handled_customers')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

