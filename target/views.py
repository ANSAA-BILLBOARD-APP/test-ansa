from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import datetime

class UserBillboardStats(APIView):

    def get(self, request):
        user = request.user  # Assuming user is authenticated
        current_date = datetime.now()
        year = current_date.year
        month = current_date.month

        # Get or create the monthly target for the current month
        monthly_target = MonthlyTarget.get_or_create_current_month_target(user)

        # Get the monthly upload count
        monthly_count = Billboards.count_billboards_uploaded(user, year, month)

        # Get weekly counts
        weekly_counts = Billboards.count_weekly_billboards_uploaded(user, year, month)

        return Response({
            'monthly_target': monthly_target.target,
            'monthly_count': monthly_count,
            'weekly_counts': weekly_counts
        })
