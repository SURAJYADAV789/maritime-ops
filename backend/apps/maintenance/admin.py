from django.contrib import admin
from .models import MaintenanceTask,  TaskComment

# Register your models here.
admin.site.register(MaintenanceTask)
admin.site.register(TaskComment)

