import locale
from django.db import models
from django.forms import ValidationError
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
import string
import random

class Car(models.Model):
    make = models.CharField(max_length=50, blank=False, null=False)
    model = models.CharField(max_length=50, blank=False, null=False)
    year = models.IntegerField(blank=False, null=False)
    color = models.CharField(max_length=20, blank=False, null=False)
    price = models.IntegerField(blank=False, null=False)
    mileage = models.IntegerField(blank=True, null=True)
    sold = models.BooleanField(default=False)
    date_sold = models.DateField(blank=True, null=True)
    salesperson = models.ForeignKey('salespeople.Salespeople', on_delete=models.SET_NULL, null=True, blank=True, related_name='sold_cars')
    vin = models.CharField(max_length=17, unique=True, blank=True)  # New field for VIN

    # New field for car type
    CONVERTIBLE = 'Convertible'
    COUPE = 'Coupe'
    HATCHBACK = 'Hatchback'
    SEDAN = 'Sedan'
    SUV = 'SUV'
    TRUCK = 'Truck'
    WAGON = 'Wagon'
    CAR_TYPE_CHOICES = [
        (CONVERTIBLE, 'Convertible'),
        (COUPE, 'Coupe'),
        (HATCHBACK, 'Hatchback'),
        (SEDAN, 'Sedan'),
        (SUV, 'SUV'),
        (TRUCK, 'Truck'),
        (WAGON, 'Wagon'),
    ]
    car_type = models.CharField(max_length=15, choices=CAR_TYPE_CHOICES, default=SEDAN)

    COMMISSION_RATE = 0.20 # 20% commission rate


    def calculate_commission(self):
        commission =  self.price * self.COMMISSION_RATE
        return round(commission, 2)

    def _generate_vin(self):
        """
        Generate a random 17-character VIN.
        Note: This is a simplified example and doesn't follow the actual VIN standards.
        """
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=17))
    
    def formatted_mileage(self):
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')  # Set locale, e.g., 'en_US.UTF-8'
        return locale.format_string("%d", self.mileage, grouping=True)
    
    def formatted_price(self):
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')  # Set locale, e.g., 'en_US.UTF-8'
        return locale.format_string("%d", self.price, grouping=True)
    
    def mark_as_not_sold(self):
        self.sold = False
        self.salesperson = None  # Set the salesperson to None
        self.save()

    def clean(self):
        # Validation logic
        #check if car make, model, year, year and mileage is alread in a car , if it is then raise validation error
        if self.make and self.model and self.year and self.color and self.mileage:
            if Car.objects.filter(make__iexact=self.make, model__iexact=self.model, year=self.year, color__iexact=self.color, mileage=self.mileage, car_type=self.car_type).exclude(id=self.id).exists():
                raise ValidationError("Car already exists")
            
        if self.sold and (not self.date_sold or not self.salesperson):
            raise ValidationError("Date sold and salesperson are required when the car is sold.")

        if self.salesperson and (not self.date_sold or not self.sold):
            raise ValidationError("Sold status and date sold are required when a Salesperson is assigned.")

        if self.date_sold and (not self.salesperson or not self.sold):
            raise ValidationError("Sold status and Salesperson are required when a sale date is set.")
    
    def save(self, *args, **kwargs):
        self.clean()
        # Generate VIN only if it doesn't exist
        if not self.vin:
            self.vin = self._generate_vin()

        for field_name in ['make', 'model', 'color']:
            val = getattr(self, field_name, False)
            # if make is BMW make it all uppercase
            if len(val) == 3:
                setattr(self, field_name, val.upper())
            else:
                setattr(self, field_name, val.capitalize())

        # Save the Car instance first to get an ID
        super(Car, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.vin} - {self.year} {self.make} {self.model} - {self.car_type}'
