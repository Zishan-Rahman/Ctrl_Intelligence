from django.db import models

# Create your models here.
class Club(models.Model):
    name = models.CharField(unique=True, blank=False, max_length=50)
    description = models.CharField(blank=True, max_length=500)
    favourite_genre = models.CharField(blank=True, max_length=100)
    location = models.CharField(blank=False, max_length=100)
    members = models.ManyToManyField(User, related_name='member_of')
    organisers = models.ManyToManyField(User, related_name='organiser_of')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owner_of')
