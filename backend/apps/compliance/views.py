from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from apps.ships.models import Ship
from apps.maintenance.models import MaintenanceTask
from apps.drills.models import SafetyDrill


@login_required
def dashboard(request):
    today = timezone.now().date()
    now   = timezone.now()

    ships = Ship.objects.all()

    ship_data = []
    for ship in ships:
        tasks  = MaintenanceTask.objects.filter(ship=ship)
        drills = SafetyDrill.objects.filter(ship=ship)

        total_tasks     = tasks.count()
        completed_tasks = tasks.filter(status='completed').count()
        overdue_tasks   = tasks.filter(
            due_date__lt=today
        ).exclude(status='completed').count()

        total_drills     = drills.count()
        completed_drills = drills.filter(status='completed').count()
        missed_drills    = drills.filter(status='missed').count()

        maintenance_score = (completed_tasks / total_tasks * 100) if total_tasks else 100
        drill_score       = (completed_drills / total_drills * 100) if total_drills else 100
        overall           = maintenance_score * 0.6 + drill_score * 0.4

        if overall >= 80:
            risk = 'low'
        elif overall >= 60:
            risk = 'medium'
        else:
            risk = 'high'

        ship_data.append({
            'id':              ship.id,
            'name':            ship.name,
            'status':          ship.status,
            'total_tasks':     total_tasks,
            'completed_tasks': completed_tasks,
            'overdue_tasks':   overdue_tasks,
            'total_drills':    total_drills,
            'completed_drills':completed_drills,
            'missed_drills':   missed_drills,
            'risk':            risk,
        })

    context = {
        'ships':           ship_data,
        'total_ships':     ships.count(),
        'completed_tasks': MaintenanceTask.objects.filter(status='completed').count(),
        'overdue_tasks':   MaintenanceTask.objects.filter(
                               due_date__lt=today
                           ).exclude(status='completed').count(),
        'pending_tasks':   MaintenanceTask.objects.filter(status='pending').count(),
        'completed_drills':SafetyDrill.objects.filter(status='completed').count(),
        'missed_drills':   SafetyDrill.objects.filter(status='missed').count(),
        'upcoming_drills': SafetyDrill.objects.filter(
                               status='scheduled',
                               scheduled_date__gte=now
                           ).count(),
    }
    return render(request, 'dashboard/index.html', context)