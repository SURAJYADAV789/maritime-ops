from rest_framework import serializers
from django.contrib.auth import authenticate
from apps.users.models import User
from apps.ships.models import Ship
from apps.maintenance.models import MaintenanceTask, TaskComment
from apps.drills.models import SafetyDrill, DrillAttendance

# ── Auth


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "password2", "role", "ship"]

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already in use.")
        return value

    def create(self, validated_data):
        validated_data.pop("password2")
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            role=validated_data.get("role", "crew"),
            ship=validated_data.get("ship", None),
        )
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(
            username=attrs.get("username"), password=attrs.get("password")
        )
        if not user:
            raise serializers.ValidationError("Invalid username or password.")
        if not user.is_active:
            raise serializers.ValidationError("Account is disabled.")
        attrs["user"] = user
        return attrs


# ── Ships


class ShipSerializer(serializers.ModelSerializer):
    crew_count = serializers.SerializerMethodField()

    class Meta:
        model = Ship
        fields = "__all__"

    def get_crew_count(self, obj):
        return obj.crew_members.count()


# ── Maintenance


class TaskCommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.get_full_name", read_only=True)

    class Meta:
        model = TaskComment
        fields = ["id", "content", "author_name", "created_at"]


class MaintenanceTaskSerializer(serializers.ModelSerializer):
    comments = TaskCommentSerializer(many=True, read_only=True)
    ship_name = serializers.CharField(source="ship.name", read_only=True)
    assigned_to_name = serializers.CharField(
        source="assigned_to.get_full_name", read_only=True
    )
    is_overdue = serializers.BooleanField(read_only=True)

    class Meta:
        model = MaintenanceTask
        fields = "__all__"
        read_only_fields = ["created_by", "created_at", "updated_at", "completed_at"]


# ── Drills


class DrillAttendanceSerializer(serializers.ModelSerializer):
    crew_member_name = serializers.CharField(
        source="crew_member.get_full_name", read_only=True
    )

    class Meta:
        model = DrillAttendance
        fields = "__all__"


class SafetyDrillSerializer(serializers.ModelSerializer):
    attendances = DrillAttendanceSerializer(many=True, read_only=True)
    ship_name = serializers.CharField(source="ship.name", read_only=True)
    participation_rate = serializers.SerializerMethodField()

    class Meta:
        model = SafetyDrill
        fields = "__all__"
        read_only_fields = ["created_by", "created_at", "updated_at", "completed_at"]

    def get_participation_rate(self, obj):
        total = obj.attendances.count()
        if total == 0:
            return 0
        attended = obj.attendances.filter(attended=True).count()
        return round((attended / total) * 100, 1)
