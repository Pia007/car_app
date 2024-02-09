import re
from decimal import Decimal
from django.db import models
from django.forms import ValidationError
from django.urls import reverse
from django.core.validators import RegexValidator, validate_email

class Salespeople(models.Model):
    """
    Model for Salespeople instances.
    
    Salespeople instance represents a salesperson in the database. It contains information about the salesperson, including first name, last name, email, phone number, and cars sold by the salesperson.
    
    Attributes:
        first_name (str): The first name of the salesperson.
        last_name (str): The last name of the salesperson.
        email (str): The email address of the salesperson.
        phone_number (str): The phone number of the salesperson.
        sold_cars (list): The list of cars sold by the salesperson.
        
    Methods:
        total_commission: Returns the total commission of the salesperson.
        formatted_commission: Returns the formatted commission of the salesperson.
        total_sales: Returns the total sales of the salesperson.
        total_cars_sold: Returns the total cars sold by the salesperson.
        clean: Validates the salesperson data.
        save: Saves the salesperson data.
        __str__: Returns the string representation of the salesperson.
        get_absolute_url: Returns the absolute URL of the salesperson.
    """
    
    phone_regex = RegexValidator(
        regex = r'^((\d{3}-){2}\d{4})|\d{10}$'
    )

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=17, blank=True)

    def total_commission(self):
        """ Loops through the cars sold and formats each as a decimal. If there is no commision then sets the value as 0.00 ."""
        total = sum(Decimal(car.calculate_commission())
                for car in self.sold_cars.all() if car.sold)
        return total.quantize(Decimal('0.00')) if total != 0 else Decimal('0.00')

    def formatted_commission(self):
        # add commas and format to 2 decimal places
        return "{:,.2f}".format(self.total_commission())

    def total_sales(self):
        """ Loops through the cars sold and formats each price as a decimal and calculates the totals sales. If there is no price then sets the value as 0.00 .  """
        total = sum(Decimal(car.price)
                    for car in self.sold_cars.all() if car.sold)
        return total.quantize(Decimal('0.00')) if total != 0 else Decimal('0.00')
    
    def total_cars_sold(self):
        total = sum(1 for car in self.sold_cars.all() if car.sold)
        return total
    
    def clean(self):
        """
        Validates the Salespeople attributes before saving it to the database. The following validation rules are used:

        Validation Rules:
        1. First and Last name must be unique: 
            - If the first name and last name are already in the database, then raise a validation error.
        2. Email must be unique and correctly formatted.
            - If the email is already in the database, then raise a validation error.
            - If the email is not correctly formatted, then raise a validation error.
        3. Phone number must be unique and correctly formatted.
            - If the phone number is already in the database, then raise a validation error.
            - If it is not in the database, check if it is correctly format and raise and error if it is not.
            
        Args:
            self: The Salespeople instance.
            
        Raises:
            ValidationError: If the validation rules are not met.
        """
        if self.first_name and self.last_name:
            if Salespeople.objects.filter(first_name__iexact=self.first_name, last_name__iexact=self.last_name).exclude(id=self.id).exists():
                raise ValidationError("Salesperson already exists")
            
        if self.email:
            if Salespeople.objects.filter(email__iexact=self.email).exclude(id=self.id).exists():
                raise ValidationError("Email already exists")

            try:
                validate_email(self.email)
            except ValidationError:
                raise ValidationError("Invalid email format")

        if self.phone_number:
            if Salespeople.objects.filter(phone_number__iexact=self.phone_number).exclude(id=self.id).exists():
                raise ValidationError("Phone number already exists")

            try:
                validate_phone_number = self.phone_regex(self.phone_number)
            except ValidationError:
                raise ValidationError("Invalid phone number format. Please use 9192129999 or 999-999-9999 format")
            
    def save(self, *args, **kwargs):
        """
        Saves the Salespeople instance to the database.
        
        This method calls the clean() method to validate the salespeople data. If the data is valid it capitalizes the first and last names and saves the Salespeople instance by calling the save() 
        method of the superclass and passing in *args and **kwargs to ensure that the custom logic and default saving behavior are applied when saving a Salespeople instance. If the data contains a
        hyphen it will split the string on hyphens and spaces, capitalize the first letter of each part, and join them back together. And handles instances where the last name starts with 'Mc'.
        
        Args:
            self: The Salespeople instance.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
            
        Returns:
            None
        """
        self.clean()

    def custom_capitalize(self, s):
        # Function to handle 'Mc' names
        def mc_name(name):
            if name.lower().startswith('mc') and len(name) > 2:
                return 'Mc' + name[2].upper() + name[3:].lower()
            else:
                return name.capitalize()

        # Split on hyphens and spaces for regular capitalization
        parts = re.split(r'[-\s]', s)
        capitalized_parts = [mc_name(part) for part in parts]
        return '-'.join(capitalized_parts) if '-' in s else ' '.join(capitalized_parts)

    def save(self, *args, **kwargs):
        for field_name in ['first_name', 'last_name']:
            val = getattr(self, field_name, "").strip()
            if val:
                setattr(self, field_name, self.custom_capitalize(val))

        super(Salespeople, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    """ Update the salesperson detail view to show the cars sold by the salesperson """
    def get_absolute_url(self):
        return reverse('salespeople_new', args=[str(self.id)])
