from django.db import models
from django.urls import reverse
from django.core.validators import EmailValidator, RegexValidator
from phonenumber_field.modelfields import PhoneNumberField

class Salespeople(models.Model):

    email_regex = RegexValidator(regex=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', message="Invalid email format")
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.CharField(validators=[email_regex], max_length=100)
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)  # Adjust max_length as needed
    # email = models.EmailField(unique=True, validators=[EmailValidator()])  # Email field
    # phone_number = PhoneNumberField(blank=True, null=True)  # Phone number field
    customers = models.ManyToManyField('customers.Customer', blank=True, related_name='salespeople_customers')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    #update the salesperson detail view to show the cars sold by the salesperson
    def get_absolute_url(self):
        return reverse('salespeople_detail', args=[str(self.id)])



