import locale
from django.db import models
from django.forms import ValidationError
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
import string
import random

class Car(models.Model):
    """
    Model for Car instances.
    
    A Car instance represents a car in the inventory. It contains information
    about the car, including the make, model, year, color, price, mileage,
    whether or not it is sold and a vehicle identification number. If it is sold, the date sold and the salesperson who sold it are also included.
    
    Attributes:
        make: A string representing the make of the car.
        model: A string representing the model of the car.
        year: An integer representing the year the car was made.
        color: A string representing the color of the car.
        price: An integer representing the price of the car.
        mileage: An integer representing the mileage of the car.
        sold: A boolean representing whether or not the car is sold.
        date_sold: A date representing the date the car was sold.
        salesperson: A Salesperson instance representing the salesperson who sold
            the car.
        vin: A string representing the VIN of the car.
        
    Methods:
        calculate_commission: Calculates the commission for the car.
        formatted_mileage: Returns the mileage of the car as a string with
            thousands separators.
        formatted_price: Returns the price of the car as a string with thousands
            separators.
        mark_as_not_sold: Marks the car as not sold.
        clean: Validates the Car instance.
        save: Saves the Car instance.
    """

    make = models.CharField(max_length=50, blank=False, null=False)
    model = models.CharField(max_length=50, blank=False, null=False)
    year = models.IntegerField(blank=False, null=False)
    color = models.CharField(max_length=20, blank=False, null=False)
    price = models.IntegerField(blank=False, null=False)
    mileage = models.IntegerField(blank=True, null=True)
    sold = models.BooleanField(default=False)
    date_sold = models.DateField(blank=True, null=True)
    salesperson = models.ForeignKey('salespeople.Salespeople', on_delete=models.SET_NULL, null=True, blank=True, related_name='sold_cars')
    vin = models.CharField(max_length=17, unique=True, blank=True) 

    """ Car Type """
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
        """ Calculates the commission of the car and rounds it to two decimal places."""
        commission =  self.price * self.COMMISSION_RATE
        return round(commission, 2)

    def _generate_vin(self):
        """
        Generate a random 17-character VIN (Vehicle Identification Number).

        This method generates a random 17-character string that simulates a VIN, which is used to uniquely
        identify vehicles. Please note that this is a simplified example for demonstration purposes
        and doesn't adhere to actual VIN standards.

        Args:
            self: An instance of the Car class.

        Returns:
            vin: A string representing the VIN of the car.
        """
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=17))
    
    def formatted_mileage(self):
        """
        Formats the mileage of the car to include thousands separators.

        This method uses the locale module to format the car's mileage attribute to a string. The mileage integer is initially formatted as a decimal number, using %d. Then the decimal is set to include thousands separators, using the grouping=True parameter. The decimal number is then formated to a string.
        
        Args:
            self: An instance of the Car class.

        Returns:
            mileage(str): The car's mileage with thousands separators.
        """
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')  
        return locale.format_string("%d", self.mileage, grouping=True)
    
    def formatted_price(self):
        """
        Formats the price of the car to include thousands separators.
        
        This method uses the locale module to format the car's price attribute to a string based on the locale of the user. The price integer is initially formatted as a decimal number, using %d. Then the decimal is set to include thousands separators, using the grouping=True parameter. The decimal number is then formated to a string.
        
        Args:
            self: An instance of the Car class.
            
        Returns:
            price(str): The car's price with thousands separators.
        """
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')  # Set locale, e.g., 'en_US.UTF-8'
        return locale.format_string("%d", self.price, grouping=True)
    
    def mark_as_not_sold(self):
        """
        Sets the sold attribute to false.
        
        This methods sets a previously sold car's sold attribute to false, sets the salesperson attribute to None and saves the car instance when the user marks the car as not sold.
        
        Args:
            self: An instance of the Car class.
            
        Returns:
            None
        """
        self.sold = False
        self.salesperson = None  # Set the salesperson to None
        self.save()

    def clean(self):
        """
        Performs data validation for the Car instance.

        This method is used to validate the attributes of a Car instance before saving it to the database.
        It checks for various validation rules and raises ValidationError if any of the rules are violated.

        Validation Rules:
        1. Car Existence Check:
            - Checks if a car with the same make, model, year, color, mileage, and car_type already exists in the database.
            - Uses iexact operator to make a case-insensitive comparison of the make, model, and color.
            - If a duplicate car is found (excluding the current instance by its ID), it raises a ValidationError.

        2. Sold Car Validation:
            - If the 'sold' attribute is True, it checks for the presence of 'date_sold' and 'salesperson'.
            - If 'date_sold' or 'salesperson' is missing when a car is marked as sold, it raises a ValidationError.

        3. Salesperson Assignment Validation:
            - If a 'salesperson' is assigned to the car, it checks for the presence of 'date_sold' and 'sold' status.
            - If 'date_sold' or 'sold' status is missing when a salesperson is assigned, it raises a ValidationError.

        4. Sale Date Validation:
            - If a 'date_sold' is specified, it checks for the presence of 'salesperson' and 'sold' status.
            - If 'salesperson' or 'sold' status is missing when a sale date is set, it raises a ValidationError.

        Args:
            self: An instance of the Car class.

        Raises:
            ValidationError: If any of the validation rules are violated.

        Note:
            This method is typically called automatically when saving a Car instance using Django's ModelForm,
            ensuring that the data conforms to the specified validation rules before it is persisted in the database.
        """
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
        """
        Saves the Car instance to the database.

        This method is used to save the Car instance to the database. It follows these steps:
        1. Validates the Car instance using the clean() method to ensure data integrity.
        2. Generates a Vehicle Identification Number (VIN) for the car if it doesn't already have one.
        3. Capitalizes the 'make' and 'model' fields for consistency.
        4. Saves the Car instance to the database by calling the save() method on the superclass and   passing in *args, **kwargs to ensure that the custom logic and default saving behavior are applied when saving a Car instance.

        Args:
            self: An instance of the Car class.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
            
        Returns:
            None

        Note:
            - The clean() method is called to validate the Car instance before saving.
            - If the 'vin' field is empty, a VIN is generated.
            - The 'make' and 'model' fields are capitalized for consistency.
            - Finally, the Car instance is saved to the database.
        """
        self.clean()
        # Generate VIN only if it doesn't exist
        if not self.vin:
            self.vin = self._generate_vin()

        for field_name in ['make', 'model', 'color']:
            val = getattr(self, field_name, False)
            # accounts for BMW, GMC, etc.
            if len(val) == 3:
                setattr(self, field_name, val.upper())
            else:
                setattr(self, field_name, val.capitalize())

        
        super(Car, self).save(*args, **kwargs)

    def __str__(self):
        """ Returns a string representation of the Car instance. """
        return f'{self.vin} - {self.year} {self.make} {self.model} - {self.car_type}'
