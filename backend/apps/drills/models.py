from django.db import models
from django.utils import timezone
from apps.ships.models import Ship
from apps.users.models import User


class SafetyDrill(models.Model):

    class DrillType(models.TextChoices):
        FIRE = "fire", "Fire Drill"
        EVACUATION = "evacuation", "Evacuation Drill"
        MAN_OVERBOARD = "man_overboard", "Man Overboard"
        ABANDON_SHIP = "abandon_ship", "Abandon Ship"
        OIL_SPILL = "oil_spill", "Oil Spill Response"
        FLOODING = "flooding", "Flooding Response"
        MEDICAL = "medical", "Medical Emergency"
        SECURITY = "security", "Security Drill"

    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        MISSED = "missed", "Missed"
        CANCELLED = "cancelled", "Cancelled"

    title = models.CharField(max_length=300)
    drill_type = models.CharField(max_length=30, choices=DrillType.choices)
    description = models.TextField(blank=True)
    ship = models.ForeignKey(Ship, on_delete=models.CASCADE, related_name="safety_drills")
    scheduled_date = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SCHEDULED)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_drills")
    completed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "safety_drills"
        ordering = ["scheduled_date"]

    def __str__(self):
        return f"{self.get_drill_type_display()} - {self.ship.name}"

    @property
    def is_missed(self):
        if self.status in (self.Status.COMPLETED, self.Status.CANCELLED):
            return False
        return self.scheduled_date < timezone.now()


class DrillAttendance(models.Model):
    drill = models.ForeignKey(SafetyDrill, on_delete=models.CASCADE, related_name="attendances")
    crew_member = models.ForeignKey(User, on_delete=models.CASCADE, related_name="drill_attendances")
    attended = models.BooleanField(default=False)
    marked_at = models.DateTimeField(null=True, blank=True)
    completion_submitted = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "drill_attendances"
        unique_together = ("drill", "crew_member")

    def __str__(self):
        status = "attended" if self.attended else "missed"
        return f"{self.crew_member} {status} {self.drill}"

    def mark_attended(self):
        self.attended = True
        self.marked_at = timezone.now()
        self.save(update_fields=["attended", "marked_at"])
