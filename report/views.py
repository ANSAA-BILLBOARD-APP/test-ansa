from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.http import HttpResponse
from .utils import generate_csv_report, count_billboards
from .serializers import ReportSerializer
from drf_spectacular.utils import extend_schema


@extend_schema(
    description=(
        "Download user media asset report in CSV format. Supports filters:\n"
        "- By time: week, month, year\n"
        "- By vacancy: vacant, occupied\n\n"
        "**Examples:**\n"
        "`/report/download-report/?time_filter=week`\n"
        "`/report/download-report/?vacancy=vacant`\n"
        "`/report/download-report/?time_filter=month&vacancy=occupied`\n"
    ),
    summary='Media asset report download',
    tags=["Report"],
)
class ReportDownloadView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReportSerializer

    def get(self, request, format=None):
        user = request.user

        time_filter = request.query_params.get('time_filter')
        vacancy = request.query_params.get('vacancy')

        try:
            csv_content = generate_csv_report(user, time_filter, vacancy)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Prepare filename based on filters
        filename = 'report'
        if time_filter:
            filename += f'_{time_filter}'
        if vacancy is not None:
            filename += f'_vacancy_{vacancy}'
        if not time_filter and vacancy is None:
            filename += '_full'
        filename += '.csv'

        # Return CSV response
        response = HttpResponse(csv_content, content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


@extend_schema(
    description=(
        "Return the count of uploaded media assets. Supports filters:\n"
        "- By time: week, month, year\n"
        "- By vacancy: vacant, occupied\n\n"
        "**Examples:**\n"
        "`/report/count-assets/?time_filter=week`\n"
        "`/report/count-assets/?vacancy=occupied`\n"
        "`/report/count-assets/?time_filter=year&vacancy=vacant`\n"
    ),
    summary='Count uploaded media assets',
    tags=["Report"],
)
class CountReportView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReportSerializer

    def get(self, request, format=None):
        user = request.user

        time_filter = request.query_params.get('time_filter')
        vacancy = request.query_params.get('vacancy')

        if not time_filter and vacancy is None:
            return Response(
                {'error': 'At least one of time_filter or vacancy is required as a parameter.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        billboards = count_billboards(user, time_filter, vacancy)
        count = billboards.count()

        return Response({'count': count}, status=status.HTTP_200_OK)
