from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from ..baserow_client import hardware_table, hardware_instance_table, get_baserow_operator
from baserowapi import Filter
import json
from django.http import Http404

class HardwareList(APIView):
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
        
        rows = hardware_table.get_rows(**kwargs)

        row_counter = 0
        for row in rows:
            row_counter += 1
            if row_counter - 1 < page * size or row_counter - 1 >= (page + 1) * size:
                continue
            data = row.content
            data['id'] = row.id
            if row['status'] == []:
                data['status'] = 'Available'
            hardware.append(data)
        return Response({'data': hardware, 'totalRecords': row_counter}, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        new_row = {
            'name': request.data.get('name'),
            'brand': request.data.get('brand'),
            'type': request.data.get('type'),
            'model_number': request.data.get('model_number'),
            'description': request.data.get('description'),
        }
        added_row = hardware_table.add_row(new_row)
        new_id = added_row.id

        # Instances
        instances = request.data.get('one2m').get('instances').get('data')
        for instance in instances:
            new_instance_row = {
                'serial_number': instance.get('serial_number'),
                'procurement_date': instance.get('procurement_date'),
                'hardware': [new_id],
            }
            hardware_instance_table.add_row(new_instance_row)
        return Response({'data': new_id}, status=status.HTTP_201_CREATED)

class HardwareDetail(APIView):
    def get(self, request, pk, format=None):
        try:
            row = hardware_table.get_row(pk)
            data = row.content
            data['id'] = row.id

            # Instances

            rows = hardware_instance_table.get_rows(filters=[Filter('hardware', pk, 'link_row_has')])
            instances = []
            for row in rows:
                instance = row.content
                instance['id'] = row.id
                instance['status'] = row.values['status'].id if len(row.values['status'].value) else None

                del instance['hardware']
                instances.append(instance)

            data['one2m'] = {
                'instances': {
                    'data': instances
                }
            }

            return Response({'data': data})
        except Exception as e:
            print(e)
            raise Http404

    def put(self, request, pk, format=None):
        row = hardware_table.get_row(pk)
        row['name'] = request.data.get('name')
        row['brand'] = request.data.get('brand')
        row['type'] = request.data.get('type')
        row['model_number'] = request.data.get('model_number')
        row['description'] = request.data.get('description')

        instances = request.data.get('one2m').get('instances').get('data')
        for instance in instances:
            if 'id' in instance:
                instance_row = hardware_instance_table.get_row(instance['id'])
                instance_row['serial_number'] = instance['serial_number']
                instance_row['procurement_date'] = instance['procurement_date']
                instance_row['status'] = [instance['status']]
                instance_row.update()
            else:
                new_instance_row = {
                    'serial_number': instance.get('serial_number'),
                    'procurement_date': instance.get('procurement_date'),
                    'status': [instance.get('status')],
                    'hardware': [pk],
                }
                hardware_instance_table.add_row(new_instance_row)

        return Response({'message': 'successful'})