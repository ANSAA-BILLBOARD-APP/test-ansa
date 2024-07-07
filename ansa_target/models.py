from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from authentication.models import AnsaaUser
from datetime import datetime
from media_asset.models import Billboards
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete


class Month(models.IntegerChoices):
    JANUARY = 1, 'January'
    FEBRUARY = 2, 'February'
    MARCH = 3, 'March'
    APRIL = 4, 'April'
    MAY = 5, 'May'
    JUNE = 6, 'June'
    JULY = 7, 'July'
    AUGUST = 8, 'August'
    SEPTEMBER = 9, 'September'
    OCTOBER = 10, 'October'
    NOVEMBER = 11, 'November'
    DECEMBER = 12, 'December'


class Target(models.Model):
    user = models.ForeignKey(AnsaaUser, on_delete=models.CASCADE)
    month = models.IntegerField(choices=Month.choices)
    year = models.PositiveIntegerField(default=datetime.now().year)
    target = models.IntegerField(default=50)  # The target number of billboards to upload
    target_count = models.IntegerField(default=0)
    date = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = _('Monthly Target')
        verbose_name_plural = _('Monthly Targets')

    def __str__(self):
        return f'{self.user.fullname} - {self.month}/{self.year} Target'


def count_user_target(sender, instance, created, **kwargs):
    """
    Updates the target_count of the user's current month's target upon billboard creation.
    """
    if created:  # Only increment if a new billboard is created
        year = datetime.now().year
        month = datetime.now().month

        target_obj, created = Target.objects.get_or_create(
            user=instance.user, 
            year=year, 
            month=month,
            defaults={'target': 50}
        )
        
        if not created:  # Increment the count if the target already existed
            target_obj.target_count += 1
            target_obj.save()

# Connect signal to create or update target count
models.signals.post_save.connect(count_user_target, sender=Billboards)


@receiver(post_delete, sender=Billboards)
def decrement_target_count(sender, instance, **kwargs):
    """
    Decrements the target_count of the user's current month's target 
    when a billboard is deleted.
    """
    current_date = timezone.now()
    month = current_date.month
    year = current_date.year

    try:
        target_obj = Target.objects.get(user=instance.user, month=month, year=year)
        if target_obj.target_count > 0:
            target_obj.target_count -= 1
            target_obj.save()
    except Target.DoesNotExist:
        pass  # If no target object exists, nothing to decrement

# Connect signals
models.signals.post_save.connect(count_user_target, sender=Billboards)