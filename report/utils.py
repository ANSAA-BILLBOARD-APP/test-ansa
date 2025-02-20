import csv
from io import StringIO
from django.utils import timezone
from datetime import timedelta
from media_asset.models import Billboards


def filter_billboards(user, time_filter=None, vacancy=None):
    now = timezone.now()
    
    if time_filter == 'week':
        start_date = now - timedelta(days=now.weekday())
    elif time_filter == 'month':
        start_date = now.replace(day=1)
    elif time_filter == 'year':
        start_date = now.replace(month=1, day=1)
    else:
        start_date = None

    # Start with all billboards for the given user
    queryset = Billboards.objects.filter(user=user)

    # Apply time filter if provided
    if start_date:
        queryset = queryset.filter(date__gte=start_date)

    # Apply vacancy filter if provided
    if vacancy is not None:
        queryset = queryset.filter(vacancy=vacancy)

    return queryset

def generate_csv_report(user, time_filter=None, vacancy=None):
    # Retrieve the filtered billboards
    billboards = filter_billboards(user, time_filter, vacancy)
    
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Unique ID', 'Asset Type', 'Signage Type', 'Zone', 'Sub Zone', 'Status', 'Vacancy', 'Dimension', 'Actual_size', 'Price', 'Payment status', 'Payment date', 'User', 'Qr_code', 'Date'])
    
    for billboard in billboards:
        writer.writerow([
            billboard.unique_id,
            billboard.get_sign_type_display(),
            billboard.get_signage_type_display(),
            billboard.get_zone_display(),
            billboard.sub_zone,
            billboard.get_status_display(),
            billboard.get_vacancy_display(),
            billboard.dimension,
            billboard.actual_size,
            billboard.price,
            billboard.get_payment_status_display(),
            billboard.payment_date,
            billboard.user,
            f"https://dotsassets.com/{billboard.qr_code}",
            billboard.date,
        ])
    
    return output.getvalue()


def count_billboards(user, time_filter=None, vacancy=None):
    now = timezone.now()
    
    if time_filter == 'week':
        start_date = now - timedelta(days=now.weekday())
    elif time_filter == 'month':
        start_date = now.replace(day=1)
    elif time_filter == 'year':
        start_date = now.replace(month=1, day=1)
    else:
        start_date = None

    queryset = Billboards.objects.filter(user=user)

    if start_date:
        queryset = queryset.filter(date__gte=start_date)

    if vacancy:
        queryset = queryset.filter(vacancy=vacancy)

    return queryset
