# your_app_name/models.py

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from authentication.models import AnsaaUser

class MonthlyTarget(models.Model):
    user = models.ForeignKey(AnsaaUser, on_delete=models.CASCADE)
    month = models.IntegerField()  # 1 for January, 2 for February, etc.
    year = models.IntegerField()
    target = models.IntegerField()  # The target number of billboards to upload

    class Meta:
        unique_together = ('user', 'month', 'year')
        verbose_name = _('Monthly Target')
        verbose_name_plural = _('Monthly Targets')

    def __str__(self):
        return f'{self.user.username} - {self.month}/{self.year} Target'

    @staticmethod
    def get_or_create_current_month_target(user, default_target=10):
        current_date = timezone.now()
        month = current_date.month
        year = current_date.year

        monthly_target, created = MonthlyTarget.objects.get_or_create(
            user=user, month=month, year=year,
            defaults={'target': default_target}
        )
        return monthly_target





