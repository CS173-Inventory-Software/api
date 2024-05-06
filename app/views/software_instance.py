import csv
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from ..baserow_client import get_baserow_operator
from ..baserow_client.software import Software, SoftwareInstance
from baserowapi import Filter
import json
from django.http import Http404, HttpResponse
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated

class SoftwareInstanceList(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        software = []
        search: dict = json.loads(request.query_params.get('search', '{}'))
        kwargs = {}

        # Pagination

        page = search.get('page', 0)
        size = search.get('rows', 5)

        # Sorting
        sort_order = search.get('sortOrder', 1)
        sort_direction = '+' if sort_order == 1 else '-'
        sort_field = search.get('sortField')

        if sort_field:
            kwargs['order_by'] = [f'{sort_direction}{sort_field}']

        # Filtering
        filters = []
        for key in search.get('filters', {}):
            for constraint in search["filters"][key]['constraints']:
                if constraint['value'] is None:
                    continue
                filters.append(
                    Filter(
                        key,
                        constraint['value'],
                        get_baserow_operator(constraint['matchMode']))
                    )
        if len(filters) > 0:
            kwargs['filters'] = filters
        
        rows = SoftwareInstance.table.get_rows(**kwargs)

        row_counter = 0
        for row in rows:
            row_counter += 1
            if row_counter - 1 < page * size or row_counter - 1 >= (page + 1) * size:
                continue
            data = row.content
            data['software'] = row.values['software'].id
            data['status'] = row.values['status'].id
            data['id'] = row.id
            software.append(data)
        return Response({'data': software, 'totalRecords': row_counter}, status=status.HTTP_200_OK)

class SoftwareCSV(APIView):

    def get(self, request, format=None):
        response = SoftwareInstanceList.as_view()(request._request)

        software = response.data['data']

        response = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="software.csv"'},
        )

        writer = csv.writer(response)
        writer.writerow([
            "ID",
            "Name", 
            "Brand", 
            "Version Number", 
            "Expiration Date",
            "Serial Key",
            "Status",
            "Assignee",
        ])

        for row in software:
            writer.writerow([
                row['id'],
                row['software_name'],
                row['software_brand'],
                row['software_version_number'],
                row['software_expiration_date'],
                row['serial_key'],
                row['status_formula'],
                row['assignee_formula'],
            ])

        return response

class SoftwareJSON(APIView):

    def get(self, request, format=None):
        response = SoftwareInstanceList.as_view()(request._request)

        software = response.data['data']
        total = response.data['totalRecords']

        response = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="software.csv"'},
        )
        

        headers = [
            "ID",
            "Name", 
            "Brand", 
            "Version Number", 
            "Serial Key",
            "Status",
            "Assignee",
        ]
        fields = [
            "id",
            "software_name",
            "software_brand",
            "software_version_number",
            "serial_key",
            "status_formula",
            "assignee_formula",
        ]

        for row in software:
            row = {header: row[field] for header, field in zip(headers, fields)}

        return Response({'data': software, 'totalRecords': total}, status=status.HTTP_200_OK)
