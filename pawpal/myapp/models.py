from django.db import models


class Pet(models.Model):
    PET_TYPE_CHOICES = [
        ('dog', 'Dog'),
        ('cat', 'Cat'),
    ]
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]

    name = models.CharField(max_length=100)
    breed = models.CharField(max_length=100)
    age = models.CharField(max_length=100,default=False)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    personality = models.CharField(max_length=200)
    story = models.TextField(blank=True)
    vaccinated = models.BooleanField(default=False)
    disability = models.CharField(max_length=100, blank=True)
    photo = models.ImageField(upload_to='pets/', blank=True, null=True)
    pet_type = models.CharField(max_length=10, choices=PET_TYPE_CHOICES)
    detail = models.CharField(max_length=200, blank=True)
    

    def __str__(self):
        return self.name

class DonationCase(models.Model):
    case_id = models.CharField(max_length=10, unique=True)  # e.g., "No. D07"
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='donation_cases')
    title = models.CharField(max_length=255)
    description = models.TextField()
    hospital = models.CharField(max_length=100, blank=True)
    amount_needed = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount_raised = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    image = models.ImageField(upload_to='donations/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.case_id} - {self.title}"
    


class Product(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='products/')
