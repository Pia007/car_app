from django.db import models
from django.core.validators import EmailValidator,  RegexValidator
from .constants import STATE_CHOICES

class Customer(models.Model):

    email_regex = RegexValidator(regex=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', message="Invalid email format")
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    zip_code_regex = RegexValidator(
    regex=r'^\d{5}(-\d{4})?$',
    message="Enter a valid ZIP code (e.g., 12345 or 12345-6789)."
)


    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.CharField(validators=[email_regex], max_length=100)
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    address1 = models.CharField(max_length=100, blank=True, null=True)
    address2 = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(choices=STATE_CHOICES, max_length=2)
    zip_code = models.CharField(validators=[zip_code_regex], max_length=10, blank=True, null=True)
    purchased_cars = models.ManyToManyField('cars.Car', blank=True, related_name='customers_purchased')
    handled_by = models.ForeignKey('salespeople.Salespeople', on_delete=models.SET_NULL, null=True, blank=True, related_name='handled_customers')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

