from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.conf import settings
from django.utils import timezone

from apps.users.models import User
from apps.ships.models import Ship
from apps.maintenance.models import MaintenanceTask, TaskComment
from apps.drills.models import SafetyDrill, DrillAttendance

from .serializers import (
    RegisterSerializer, LoginSerializer,
    ShipSerializer,
    MaintenanceTaskSerializer, TaskCommentSerializer,
    SafetyDrillSerializer, DrillAttendanceSerializer,
)




class IsAdmin(IsAuthenticated):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.is_admin


def set_refresh_cookie(response, refresh_token):
    response.set_cookie(
        key='refresh_token',
        value=refresh_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite='Lax',
        max_age=7 * 24 * 60 * 60,
    )
    return response


# ── Auth Views ────────────────────────────────

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {'message': 'User registered successfully.', 'username': user.username},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)

            response = Response({
                'message': 'Login successful',
                'access': str(refresh.access_token),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role,
                }
            })
            return set_refresh_cookie(response, str(refresh))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response({'error': 'Refresh token not found.'}, status=401)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            response = Response({'message': 'Logout successful.'})
            response.delete_cookie('refresh_token')
            return response
        except TokenError:
            return Response({'error': 'Invalid token.'}, status=400)


class RefreshTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response({'error': 'Refresh token not found.'}, status=401)
        try:
            refresh = RefreshToken(refresh_token)
            return Response({'access': str(refresh.access_token)})
        except TokenError:
            return Response({'error': 'Invalid or expired token.'}, status=401)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'ship': user.ship.name if user.ship else None,
        })


# ── Ship Views

class ShipListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        ships = Ship.objects.all()
        serializer = ShipSerializer(ships, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not request.user.is_admin:
            return Response({'error': 'Admin only.'}, status=403)
        serializer = ShipSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class ShipDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Ship.objects.get(pk=pk)
        except Ship.DoesNotExist:
            return None

    def get(self, request, pk):
        ship = self.get_object(pk)
        if not ship:
            return Response({'error': 'Not found.'}, status=404)
        return Response(ShipSerializer(ship).data)

    def patch(self, request, pk):
        if not request.user.is_admin:
            return Response({'error': 'Admin only.'}, status=403)
        ship = self.get_object(pk)
        if not ship:
            return Response({'error': 'Not found.'}, status=404)
        serializer = ShipSerializer(ship, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


# ── Maintenance Views 

class TaskListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.is_admin:
            tasks = MaintenanceTask.objects.all()
        else:
            tasks = MaintenanceTask.objects.filter(ship=user.ship)

        # Filters
        ship_id  = request.query_params.get('ship')
        status_f = request.query_params.get('status')
        priority = request.query_params.get('priority')

        if ship_id:
            tasks = tasks.filter(ship_id=ship_id)
        if status_f:
            tasks = tasks.filter(status=status_f)
        if priority:
            tasks = tasks.filter(priority=priority)

        serializer = MaintenanceTaskSerializer(tasks, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not request.user.is_admin:
            return Response({'error': 'Admin only.'}, status=403)
        serializer = MaintenanceTaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class TaskDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return MaintenanceTask.objects.get(pk=pk)
        except MaintenanceTask.DoesNotExist:
            return None

    def get(self, request, pk):
        task = self.get_object(pk)
        if not task:
            return Response({'error': 'Not found.'}, status=404)
        return Response(MaintenanceTaskSerializer(task).data)

    def patch(self, request, pk):
        task = self.get_object(pk)
        if not task:
            return Response({'error': 'Not found.'}, status=404)
        # Crew can only update status
        if not request.user.is_admin and task.assigned_to != request.user:
            return Response({'error': 'Not allowed.'}, status=403)
        serializer = MaintenanceTaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


class TaskCommentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            task = MaintenanceTask.objects.get(pk=pk)
        except MaintenanceTask.DoesNotExist:
            return Response({'error': 'Not found.'}, status=404)
        serializer = TaskCommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(task=task, author=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


# ── Drill Views 

class DrillListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.is_admin:
            drills = SafetyDrill.objects.all()
        else:
            drills = SafetyDrill.objects.filter(ship=user.ship)

        ship_id  = request.query_params.get('ship')
        status_f = request.query_params.get('status')

        if ship_id:
            drills = drills.filter(ship_id=ship_id)
        if status_f:
            drills = drills.filter(status=status_f)

        serializer = SafetyDrillSerializer(drills, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not request.user.is_admin:
            return Response({'error': 'Admin only.'}, status=403)
        serializer = SafetyDrillSerializer(data=request.data)
        if serializer.is_valid():
            drill = serializer.save(created_by=request.user)
            # Auto create attendance for all crew on ship
            crew = User.objects.filter(ship=drill.ship, role='crew')
            DrillAttendance.objects.bulk_create([
                DrillAttendance(drill=drill, crew_member=member)
                for member in crew
            ])
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class DrillDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return SafetyDrill.objects.get(pk=pk)
        except SafetyDrill.DoesNotExist:
            return None

    def get(self, request, pk):
        drill = self.get_object(pk)
        if not drill:
            return Response({'error': 'Not found.'}, status=404)
        return Response(SafetyDrillSerializer(drill).data)

    def patch(self, request, pk):
        if not request.user.is_admin:
            return Response({'error': 'Admin only.'}, status=403)
        drill = self.get_object(pk)
        if not drill:
            return Response({'error': 'Not found.'}, status=404)
        serializer = SafetyDrillSerializer(drill, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


class DrillAttendanceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            attendance = DrillAttendance.objects.get(
                drill_id=pk,
                crew_member=request.user
            )
        except DrillAttendance.DoesNotExist:
            return Response({'error': 'Not found.'}, status=404)
        attendance.mark_attended()
        return Response({'message': 'Attendance marked.'})


# ── Compliance View 

class ComplianceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        now = timezone.now()
        today = now.date()

        ships = Ship.objects.filter(status='active')
        result = []

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
            overall_score     = round(maintenance_score * 0.6 + drill_score * 0.4, 1)

            if overall_score >= 80:
                risk = 'low'
            elif overall_score >= 60:
                risk = 'medium'
            else:
                risk = 'high'

            result.append({
                'ship': ship.name,
                'overall_score': overall_score,
                'risk_level': risk,
                'maintenance': {
                    'total': total_tasks,
                    'completed': completed_tasks,
                    'overdue': overdue_tasks,
                },
                'drills': {
                    'total': total_drills,
                    'completed': completed_drills,
                    'missed': missed_drills,
                }
            })

        return Response({
            'fleet_score': round(sum(r['overall_score'] for r in result) / len(result), 1) if result else 0,
            'ships': result,
        })