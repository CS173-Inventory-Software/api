from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from ..baserow_client import get_baserow_operator
from ..baserow_client.user import User, UserType
from baserowapi import Filter
import json
from django.http import Http404

class UserList(APIView):
    def get(self, request, format=None):
        users = []
        search: dict = json.loads(request.query_params['search'])
        kwargs = {}

        # Pagination

        page = search.get('page', 0)
        size = search.get('rows', 100)

        # Sorting
        sort_order = search.get('sortOrder', 1)
        sort_direction = '+' if sort_order == 1 else '-'
        sort_field = search.get('sortField')

        if sort_field:
            kwargs['order_by'] = [f'{sort_direction}{sort_field}']

        # Filtering
        filters = []
        for key in search.get("filters", {}):
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
        
        rows = User.table.get_rows(**kwargs)

        row_counter = 0
        for row in rows:
            row_counter += 1
            if row_counter - 1 < page * size or row_counter - 1 >= (page + 1) * size:
                continue
            data = row.content
            data['id'] = row.id
            users.append(data)
        return Response({'data': users, 'totalRecords': row_counter}, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        added_row = User.create(
            request.data.get('email'), 
            request.data.get('type')
        )

        return Response({'data': added_row.id}, status=status.HTTP_201_CREATED)

class UserDetail(APIView):
    def get(self, request, pk, format=None):
        try:
            row = User.table.get_row(pk)
        except Exception as e:
            raise Http404

        data = row.content
        data['id'] = row.id
        data['type'] = row.values['type'].id
        return Response({'data': data})

    def put(self, request, pk, format=None):
        row = User.table.get_row(pk)
        row['email'] = request.data.get('email')
        row['type'] = [request.data.get('type')]
        row.update()
        return Response({'message': 'Successful'})