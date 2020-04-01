from django.db import models
from django import forms

class Registration(models.Model):
    
    name = models.CharField(max_length = 100)
    username = models.CharField(max_length = 100)
    email = models.EmailField()
    password = models.CharField(max_length = 100)
    password1 = models.CharField(max_length = 100)

    
    def __str__(self):
        return str(self.id)