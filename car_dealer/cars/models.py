from django.db import models
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
    salespeople = models.ManyToManyField('salespeople.Salespeople', blank=True, related_name='cars_sold_by') 
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

    def _generate_vin(self):
        """
        Generate a random 17-character VIN.
        Note: This is a simplified example and doesn't follow the actual VIN standards.
        """
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=17))

    def save(self, *args, **kwargs):
        if not self.vin:
            # Generate VIN only if it doesn't exist
            self.vin = self._generate_vin()
        super(Car, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.year} {self.make} {self.model} - {self.car_type}'
