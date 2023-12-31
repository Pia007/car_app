import locale
from django.db import models
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
    SEDAN = 'Sedan'
    SUV = 'SUV'
    TRUCK = 'Truck'
    WAGON = 'Wagon'
    CAR_TYPE_CHOICES = [
        (CONVERTIBLE, 'Convertible'),
        (COUPE, 'Coupe'),
        (SEDAN, 'Sedan'),
        (SUV, 'SUV'),
        (TRUCK, 'Truck'),
        (WAGON, 'Wagon'),
    ]
    car_type = models.CharField(max_length=15, choices=CAR_TYPE_CHOICES, default=SEDAN)

    COMMISSION_RATE = 0.15 # 15% commission rate

    def calculate_commission(self):
        commission =  self.price * self.COMMISSION_RATE
        return round(commission, 2)

    def _generate_vin(self):
        """
        Generate a random 17-character VIN.
        Note: This is a simplified example and doesn't follow the actual VIN standards.
        """
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=17))
    
    def formatted_price(self):
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')  # Set locale, e.g., 'en_US.UTF-8'
        return locale.format_string("%d", self.price, grouping=True)

    def save(self, *args, **kwargs):
        # Generate VIN only if it doesn't exist
        if not self.vin:
            self.vin = self._generate_vin()

        # Save the Car instance first to get an ID
        super(Car, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.vin} - {self.year} {self.make} {self.model} - {self.car_type}'
