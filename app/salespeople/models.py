from django.db import models
from django.urls import reverse
from django.core.validators import EmailValidator
from phonenumber_field.modelfields import PhoneNumberField

class Salespeople(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True, validators=[EmailValidator()])  # Email field
    phone_number = PhoneNumberField(blank=True, null=True)  # Phone number field
    customers = models.ManyToManyField('customers.Customer', blank=True, related_name='salespeople_customers')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    #update the salesperson detail view to show the cars sold by the salesperson
    def get_absolute_url(self):
        return reverse('salespeople_new', args=[str(self.id)])



