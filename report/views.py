from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from django.http import HttpResponse
from .utils import generate_csv_report, count_billboards
from .serializers import ReportSerializer
from drf_spectacular.utils import extend_schema

@extend_schema(
    description="The endpoint is use to download all user report with and without filter in csv format by date(week, month and year) and vacancy eg,    \n\n http://localhost:8000/report/download-report/?time_filter=week \n\n http://localhost:8000/report/download-report/?time_filter=month  \n\n http://localhost:8000/report/download-report/?time_filter=year \n\n http://localhost:8000/report/download-report/?vacancy=vacant \n\n http://localhost:8000/report/download-report/?vacancy=occupied \n\n http://localhost:8000/report/download-report/?time_filter=week&vacancy=vacant \n\n http://localhost:8000/report/download-report/?time_filter=month&vacancy=occupied",
    summary='Media asset report download'
)
class ReportDownloadView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReportSerializer

    def get(self, request, format=None):
        user = request.user
        if not user:
            return Response({'error': 'Authentication required.'}, status=status.HTTP_401_UNAUTHORIZED)
        
        time_filter = request.query_params.get('time_filter')
        vacancy = request.query_params.get('vacancy')

        try:
            csv_content = generate_csv_report(user, time_filter, vacancy)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        response = HttpResponse(csv_content, content_type='text/csv')
        filename = 'report'
        
        # Add filter details to the filename if they are provided
        if time_filter:
            filename += f'_{time_filter}'
        if vacancy is not None:  # Handle boolean filter for vacancy
            filename += f'_vacancy_{vacancy}'
        
        # If no filters are applied, append '_full' to indicate a full report
        if not time_filter and vacancy is None:
            filename += '_full'
        
        filename += '.csv'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response



@extend_schema(
    description="The endpoint return sum total of upploaded user media assets by date(week, month and year) and vacancy eg,    \n\n http://localhost:8000/report/count-assets/?time_filter=week \n\n http://localhost:8000/report/count-assets/?time_filter=month  \n\n http://localhost:8000/report/count-assets/?time_filter=year \n\n http://localhost:8000/report/count-assets/?vacancy=vacant \n\n http://localhost:8000/report/count-assets/?vacancy=occupied \n\n http://localhost:8000/api/download-report/?time_filter=week&vacancy=vacant",
    summary='Count uploaded media assets'
)
class CountReportView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReportSerializer

    def get(self, request, format=None):
        user = request.user
        if not user.is_authenticated:
            return Response({'error': 'Authentication required.'}, status=status.HTTP_401_UNAUTHORIZED)

        time_filter = request.query_params.get('time_filter')
        vacancy = request.query_params.get('vacancy')

        if not time_filter and not vacancy:
            return Response({'error': 'At least one of time_filter or vacancy is required as a parameter.'}, status=status.HTTP_400_BAD_REQUEST)

        billboards = count_billboards(user, time_filter, vacancy)
        count = billboards.count()

        return Response({'count': count}, status=status.HTTP_200_OK)