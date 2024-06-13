# your_app_name/management/commands/monthly_targets.py

from django.core.management.base import BaseCommand
from authentication.models import AnsaaUser
from your_app_name.models import MonthlyTarget
from django.utils import timezone

class Command(BaseCommand):
    help = 'Automatically sets monthly targets for all users'

    def handle(self, *args, **options):
        current_date = timezone.now()
        month = current_date.month
        year = current_date.year
        default_target = 10  # Define your default target here

        for user in AnsaaUser.objects.all():
            MonthlyTarget.get_or_create_current_month_target(user, default_target)
        
        self.stdout.write(self.style.SUCCESS('Monthly targets set for all users'))
