from django.db import models

# Create your models here.

class Ship(models.Model):
    
    class Status(models.TextChoices):
        ACTIVE = 'active','Active'
        DOCKED = 'docked','Docked'
        MAINTENANCE = 'maintenance',   'Under Maintenance'
        DECOMMISSIONED = 'decommissioned','Decommissioned'


    name = models.CharField(max_length=200)
    imo_number = models.CharField(max_length=20, unique=True)
    vessel_type = models.CharField(max_length=100)
    flag = models.CharField(max_length=100)
    port_of_registry = models.CharField(max_length=200)
    gross_tonnage = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    year_built = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ships'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} {self.imo_number}"
    
    