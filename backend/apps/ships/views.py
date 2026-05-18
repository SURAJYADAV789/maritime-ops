from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Ship
from apps.maintenance.models import MaintenanceTask
from apps.drills.models import SafetyDrill
from django.utils import timezone


@login_required
def ship_list(request):
    ships = Ship.objects.all()
    context = {"ships": ships}
    return render(request, "ships/list.html", context)


@login_required
def ship_detail(request, pk):
    ship = get_object_or_404(Ship, pk=pk)
    today = timezone.now().date()
    now = timezone.now()

    tasks = MaintenanceTask.objects.filter(ship=ship)
    drills = SafetyDrill.objects.filter(ship=ship)

    total_tasks = tasks.count()
    completed_tasks = tasks.filter(status="completed").count()
    overdue_tasks = tasks.filter(due_date__lt=today).exclude(status="completed").count()

    total_drills = drills.count()
    completed_drills = drills.filter(status="completed").count()
    missed_drills = drills.filter(status="missed").count()

    maintenance_score = (completed_tasks / total_tasks * 100) if total_tasks else 100
    drill_score = (completed_drills / total_drills * 100) if total_drills else 100
    overall = round(maintenance_score * 0.6 + drill_score * 0.4, 1)

    if overall >= 80:
        risk = "low"
    elif overall >= 60:
        risk = "medium"
    else:
        risk = "high"

    context = {
        "ship": ship,
        "crew": ship.crew_members.all(),
        "tasks": tasks.order_by("due_date")[:5],
        "drills": drills.order_by("scheduled_date")[:5],
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "overdue_tasks": overdue_tasks,
        "total_drills": total_drills,
        "completed_drills": completed_drills,
        "missed_drills": missed_drills,
        "overall_score": overall,
        "risk": risk,
    }
    return render(request, "ships/detail.html", context)


@login_required
def ship_create(request):
    if not request.user.is_admin:
        messages.error(request, "Only admins can register ships.")
        return redirect('ships:ship-list')

    if request.method == "POST":
        ship = Ship(
            name=request.POST["name"],
            imo_number=request.POST["imo_number"],
            vessel_type=request.POST["vessel_type"],
            flag=request.POST["flag"],
            port_of_registry=request.POST["port_of_registry"],
            year_built=request.POST.get("year_built") or None,
            status="active",
        )
        ship.save()
        messages.success(request, f'Ship "{ship.name}" registered.')
        return redirect('ships:ship-list')

    return render(request, "ships/create.html")
