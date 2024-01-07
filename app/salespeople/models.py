from decimal import Decimal
import locale
from django.db import models
from django.forms import ValidationError
from django.urls import reverse
from django.core.validators import RegexValidator, validate_email


class Salespeople(models.Model):

    # email_regex = RegexValidator(
    #     regex=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', message="Invalid email format")
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$', 
        message="Phone number must be entered in the format: '999-999-9999'. Up to 15 digits allowed."
    )

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=17, blank=True)  # Adjust max_length as needed

    def total_commission(self):
        total = sum(Decimal(car.calculate_commission())
                    for car in self.sold_cars.all() if car.sold)
        return total.quantize(Decimal('0.00')) if total != 0 else Decimal('0.00')

    def formatted_commission(self):
        # Set locale, e.g., 'en_US.UTF-8'
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        return locale.format_string("%d", self.total_commission(), grouping=True)

    # calculate total sales for saleperson
    def total_sales(self):
        total = sum(Decimal(car.price)
                    for car in self.sold_cars.all() if car.sold)
        return total.quantize(Decimal('0.00')) if total != 0 else Decimal('0.00')
    
    # calculate total cars sold by saleperson
    def total_cars_sold(self):
        total = sum(1 for car in self.sold_cars.all() if car.sold)
        return total
    
    def clean(self):
        #check if first name and lad name is already in database, if they are then raise validation error
        if self.first_name and self.last_name:
            if Salespeople.objects.filter(first_name__iexact=self.first_name, last_name__iexact=self.last_name).exclude(id=self.id).exists():
                raise ValidationError("Salesperson already exists")
            
        
        if self.email:
            if Salespeople.objects.filter(email__iexact=self.email).exclude(id=self.id).exists():
                raise ValidationError("Email already exists")

            # Validate email format
            try:
                validate_email(self.email)
            except ValidationError:
                raise ValidationError("Invalid email format")

        #check if the phone number is already in database, if it not not then check if it is format matche phone_regex
        if self.phone_number:
            if Salespeople.objects.filter(phone_number__iexact=self.phone_number).exclude(id=self.id).exists():
                raise ValidationError("Phone number already exists")

            # Validate phone number matches phone_regex format
            try:
                validate_phone_number = self.phone_regex(self.phone_number)
            except ValidationError:
                raise ValidationError("Invalid phone number format. Please use 999999999 format")
            
    
    def save(self, *args, **kwargs):
        self.clean()

        for field_name in ['first_name', 'last_name']:
            val = getattr(self, field_name, False)

            if val:
                setattr(self, field_name, val.capitalize())

        super(Salespeople, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    # Update the salesperson detail view to show the cars sold by the salesperson
    def get_absolute_url(self):
        return reverse('salespeople_new', args=[str(self.id)])
