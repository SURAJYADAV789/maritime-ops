from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import SafetyDrill, DrillAttendance
from apps.ships.models import Ship
from apps.users.models import User


@login_required
def drill_list(request):
    user = request.user
    if user.is_admin:
        drills = SafetyDrill.objects.select_related("ship").all()
    else:
        drills = SafetyDrill.objects.select_related("ship").filter(ship=user.ship)

    # Filters
    ship_filter = request.GET.get("ship")
    status_filter = request.GET.get("status")
    type_filter = request.GET.get("drill_type")

    if ship_filter:
        drills = drills.filter(ship_id=ship_filter)
    if status_filter:
        drills = drills.filter(status=status_filter)
    if type_filter:
        drills = drills.filter(drill_type=type_filter)

    # Auto mark missed
    now = timezone.now()
    for drill in drills:
        if drill.scheduled_date < now and drill.status == "scheduled":
            drill.status = "missed"
            drill.save(update_fields=["status"])

    context = {
        "drills": drills.order_by("scheduled_date"),
        "ships": Ship.objects.all(),
        "statuses": SafetyDrill.Status.choices,
        "drill_types": SafetyDrill.DrillType.choices,
        "selected_ship": ship_filter,
        "selected_status": status_filter,
        "selected_type": type_filter,
    }
    return render(request, "drills/list.html", context)


@login_required
def drill_detail(request, pk):
    drill = get_object_or_404(SafetyDrill, pk=pk)
    user = request.user

    user_attendance = None
    if user.is_crew:
        user_attendance = DrillAttendance.objects.filter(
            drill=drill, crew_member=user
        ).first()

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "mark_attended" and user_attendance:
            user_attendance.attended = True
            user_attendance.marked_at = timezone.now()
            user_attendance.save()
            messages.success(request, "Attendance marked!")

        elif action == "submit_completion" and user_attendance:
            user_attendance.attended = True
            user_attendance.completion_submitted = True
            user_attendance.notes = request.POST.get("notes", "")
            user_attendance.save()
            messages.success(request, "Completion submitted!")

        elif action == "complete_drill" and user.is_admin:
            drill.status = "completed"
            drill.completed_at = timezone.now()
            drill.save()
            messages.success(request, "Drill marked as completed.")

        elif action == "cancel_drill" and user.is_admin:
            drill.status = "cancelled"
            drill.save()
            messages.success(request, "Drill cancelled.")

        return redirect("drill-detail", pk=pk)

    context = {
        "drill": drill,
        "attendances": drill.attendances.select_related("crew_member").all(),
        "user_attendance": user_attendance,
    }
    return render(request, "drills/detail.html", context)


@login_required
def drill_create(request):
    if not request.user.is_admin:
        messages.error(request, "Only admins can schedule drills.")
        return redirect("drill-list")

    if request.method == "POST":
        drill = SafetyDrill(
            title=request.POST["title"],
            drill_type=request.POST["drill_type"],
            description=request.POST.get("description", ""),
            ship_id=request.POST["ship"],
            scheduled_date=request.POST["scheduled_date"],
            duration_minutes=request.POST.get("duration_minutes", 60),
            status="scheduled",
            created_by=request.user,
        )
        drill.save()

        # Auto create attendance for all crew on ship
        crew = User.objects.filter(ship=drill.ship, role="crew")
        DrillAttendance.objects.bulk_create(
            [DrillAttendance(drill=drill, crew_member=member) for member in crew]
        )

        messages.success(request, f'Drill "{drill.title}" scheduled.')
        return redirect("drill-list")

    context = {
        "ships": Ship.objects.all(),
        "drill_types": SafetyDrill.DrillType.choices,
    }
    return render(request, "drills/create.html", context)
