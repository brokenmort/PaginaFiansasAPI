from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Create or update a superuser with given credentials"

    def add_arguments(self, parser):
        parser.add_argument("--email", required=True)
        parser.add_argument("--password", required=True)
        parser.add_argument("--first_name", default="")
        parser.add_argument("--last_name", default="")

    def handle(self, *args, **options):
        User = get_user_model()
        email = options["email"]
        password = options["password"]
        first_name = options.get("first_name")
        last_name = options.get("last_name")

        u = User.objects.filter(email=email).first()
        if u is None:
            u = User.objects.create_superuser(email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f"Created superuser: {email}"))
        else:
            u.is_staff = True
            u.is_superuser = True
            u.set_password(password)
            self.stdout.write(self.style.WARNING(f"Updated existing user to superuser: {email}"))
        if first_name:
            u.first_name = first_name
        if last_name:
            u.last_name = last_name
        u.save()
        self.stdout.write(self.style.SUCCESS("OK"))

