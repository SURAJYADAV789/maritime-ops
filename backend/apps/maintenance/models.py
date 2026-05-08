from django.db import models
from django.utils import timezone

# Create your models here.

class MaintenanceTask(models.Model):

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        IN_PROGRESS = 'in_progress', 'In Progress'
        COMPLETED = 'completed', 'Completed'
        OVERDUE = 'overdue', 'Overdue'

    class Priority(models.TextChoices):
        LOW = 'low', 'Low'
        MEDIUM = 'medium', 'Medium'
        HIGH = 'high', 'High'
        CRITICAL = 'critical', 'Critical'

    title = models.CharField(max_length=300)
    description = models.TextField()
    ship = models.ForeignKey('ships.ship', on_delete=models.CASCADE, related_name='maintenance_tasks')
    assigned_to = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    created_by  = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='created_tasks')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)
    due_date = models.DateField()
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'maintenance_tasks'
        ordering = ['due_date', '-priority']

    def __str__(self):
        return f"{self.title} {self.ship.name}"
    
    @property
    def is_overdue(self):
        if self.status == self.status.COMPLETED:
            return False
        return self.due_date < timezone.now().date()
    
    def save(self, *args, **kwargs):
        if self.status == self.Status.COMPLETED and not self.completed_at:
            self.completed_at = timezone.now()
        super().save(*args, **kwargs)




class TaskComment(models.Model):
    task       = models.ForeignKey(MaintenanceTask, on_delete=models.CASCADE, related_name='comments')
    author     = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True)
    content    = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'task_comments'
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author} on {self.task.title}"

    
