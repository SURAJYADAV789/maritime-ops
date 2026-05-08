from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):

    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        CREW = 'crew', 'Crew'

    role = models.CharField(max_length=10, choices=Role.choices, default=Role.CREW)
    employee_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    ship = models.ForeignKey('ships.Ship', on_delete=models.SET_NULL, null=True, blank=True, related_name='crew_members')

    class Meta:
        db_table = 'users'

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.role})"
    
    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN
    
    @property
    def is_crew(self):
        return self.role == self.Role.CREW
