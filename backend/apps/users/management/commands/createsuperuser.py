from django.contrib.auth.management.commands.createsuperuser import Command as BaseCommand
from apps.users.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        super().handle(*args, **options)
        username = options.get('username')
        if not username:
            username = input('Enter the username you just created: ')
        try:
            user = User.objects.get(username=username)
            user.role = 'admin'
            user.is_staff = True
            user.save()
            self.stdout.write(f'✅ Role set to ADMIN for {username}')
        except User.DoesNotExist:
            pass