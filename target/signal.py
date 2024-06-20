# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from .models import MonthlyTarget
# from billboards.models import Billboards  # Assuming this is the model where uploads are tracked
# from datetime import datetime

# @receiver(post_save, sender=Billboards)
# def count_user_target(sender, instance, created, **kwargs):
#     """
#     Update the user's monthly target count whenever a new billboard is uploaded.
#     """
#     if created:
#         current_date = timezone.now()
#         month = current_date.month
#         year = current_date.year

#         # Fetch or create the current month's target for the user
#         monthly_target, _ = MonthlyTarget.objects.get_or_create(
#             user=instance.user, month=month, year=year,
#             defaults={'target': 50}
#         )

#         # Increment the target count
#         monthly_target.target_count += 1
#         monthly_target.save()

# # Ensure the signal is connected in the app's ready method
