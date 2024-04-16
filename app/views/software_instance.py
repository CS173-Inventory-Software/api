from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from ..baserow_client import get_baserow_operator
from ..baserow_client.software import Software, SoftwareInstance
from baserowapi import Filter
import json
from django.http import Http404

class SoftwareInstanceList(APIView):
    def get(self, request, format=None):
        software = []
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