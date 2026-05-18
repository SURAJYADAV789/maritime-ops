from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import MaintenanceTask, TaskComment
from apps.ships.models import Ship
from apps.users.models import User


@login_required
def task_list(request):
    user = request.user
    if user.is_admin:
        tasks = MaintenanceTask.objects.select_related("ship", "assigned_to").all()
    else:
        tasks = MaintenanceTask.objects.select_related("ship", "assigned_to").filter(
            assigned_to=user
        )

    # Filters
    ship_filter = request.GET.get("ship")
    status_filter = request.GET.get("status")
    priority_filter = request.GET.get("priority")

    if ship_filter:
        tasks = tasks.filter(ship_id=ship_filter)
    if status_filter:
        tasks = tasks.filter(status=status_filter)
    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)

    context = {
        "tasks": tasks.order_by("due_date"),
        "ships": Ship.objects.all(),
        "statuses": MaintenanceTask.Status.choices,
        "priorities": MaintenanceTask.Priority.choices,
        "selected_ship": ship_filter,
        "selected_status": status_filter,
        "selected_priority": priority_filter,
    }
    return render(request, "maintenance/list.html", context)


@login_required
def task_detail(request, pk):
    task = get_object_or_404(MaintenanceTask, pk=pk)

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "update_status":
            new_status = request.POST.get("status")
            if new_status in dict(MaintenanceTask.Status.choices):
                task.status = new_status
                task.save()
                messages.success(request, "Status updated.")

        elif action == "add_comment":
            content = request.POST.get("content", "").strip()
            if content:
                TaskComment.objects.create(
                    task=task, author=request.user, content=content
                )
                messages.success(request, "Comment added.")

        return redirect("maintenance:task-detail", pk=task.pk)

    context = {
        "task": task,
        "comments": task.comments.all(),
        "statuses": MaintenanceTask.Status.choices,
    }
    return render(request, "maintenance/detail.html", context)


@login_required
def task_create(request):
    if not request.user.is_admin:
        messages.error(request, "Only admins can create tasks.")
        return redirect("maintenance:task-list")

    if request.method == "POST":
        task = MaintenanceTask(
            title=request.POST["title"],
            description=request.POST["description"],
            ship_id=request.POST["ship"],
            assigned_to_id=request.POST.get("assigned_to") or None,
            priority=request.POST["priority"],
            due_date=request.POST["due_date"],
            status="pending",
            created_by=request.user,
        )
        task.save()
        messages.success(request, f'Task "{task.title}" created.')
        return redirect("maintenance:task-detail", pk=task.pk)

    context = {
        "ships": Ship.objects.all(),
        "crew": User.objects.filter(role="crew"),
        "priorities": MaintenanceTask.Priority.choices,
    }
    return render(request, "maintenance/create.html", context)
