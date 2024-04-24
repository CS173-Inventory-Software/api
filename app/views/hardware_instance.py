import csv
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from ..baserow_client import get_baserow_operator
from ..baserow_client.hardware import HardwareInstance
from baserowapi import Filter
import json
from django.http import Http404, HttpResponse
from rest_framework.authentication import SessionAuthentication
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

class HardwareInstanceList(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        hardware = []
        search: dict = json.loads(request.query_params['search'])
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
        for key in search["filters"]:
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
        
        kwargs['page_size'] = 10000
        rows = HardwareInstance.table.get_rows(**kwargs)

        print(kwargs)

        row_counter = 0
        for row in rows:
            row_counter += 1
            if row_counter - 1 < page * size or row_counter - 1 >= (page + 1) * size:
                continue
            data = row.content
            data['hardware'] = row.values['hardware'].id
            data['status'] = row.values['status'].id
            data['id'] = row.id
            hardware.append(data)
        return Response({'data': hardware, 'totalRecords': row_counter}, status=status.HTTP_200_OK)


    
class HardwareCSV(APIView):

    def get(self, request, format=None):
        response = HardwareInstanceList.as_view()(request._request)

        hardware = response.data['data']

        response = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="hardware.csv"'},
        )

        writer = csv.writer(response)
        writer.writerow([
            "ID",
            "Name", 
            "Brand", 
            "Type", 
            "Model Number", 
            "Serial Number",
            "Procurement Date",
            "Status",
            "Assignee",
        ])

        for row in hardware:
            writer.writerow([
                row['id'],
                row['hardware_name'],
                row['hardware_brand'],
                row['hardware_type'],
                row['hardware_model_number'],
                row['serial_number'],
                row['procurement_date'],
                row['status_formula'],
                row['assignee_formula'],
            ])

        return response