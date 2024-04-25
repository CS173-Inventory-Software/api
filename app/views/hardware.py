from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from app.serializers.hardware import HardwareInstanceSerializer, HardwareSerializer
from ..baserow_client import get_baserow_operator
from ..baserow_client.assignment_log import AssignmentLog
from ..baserow_client.hardware import Hardware, HardwareInstance
from baserowapi import Filter
import json
from django.http import Http404
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from ..baserow_client.user import UserTypeEnum
class HardwareList(APIView):
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
        
        rows = Hardware.table.get_rows(**kwargs)

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
        if request.user.role.role not in [UserTypeEnum.ADMIN.value, UserTypeEnum.SUPER_ADMIN.value, UserTypeEnum.ROOT_ADMIN.value]:
            return Response({'message': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        errors = {}
        hardware_serializer = HardwareSerializer(data=request.data)
        if not hardware_serializer.is_valid():
            errors.update(hardware_serializer.errors)

        hardware_instance_serializer = HardwareInstanceSerializer(data=request.data.get('one2m').get('instances').get('data'), many=True)

        if not hardware_instance_serializer.is_valid():
            errors['instances'] = hardware_instance_serializer.errors

        if errors:
            return Response({"message": "Invalid data", "errors": errors}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        new_row = {
            'name': request.data.get('name'),
            'brand': request.data.get('brand'),
            'type': request.data.get('type'),
            'model_number': request.data.get('model_number'),
            'description': request.data.get('description'),
        }
        added_row = Hardware.table.add_row(new_row)
        new_id = added_row.id

        # Instances
        instances = request.data.get('one2m').get('instances').get('data')
        for instance in instances:
            new_instance_row = {
                'serial_number': instance.get('serial_number'),
                'procurement_date': instance.get('procurement_date'),
                'hardware': [new_id],
                'status': [instance.get('status')] if instance.get('status') else [],
            }
            if instance.get("assignee"):
                new_instance_row['assignee'] = [instance.get('assignee')]
                # Add assignment log
            hardware_instance_row = HardwareInstance.table.add_row(new_instance_row)
            if instance.get("assignee"):
                AssignmentLog.assign({
                    'user': [instance.get('assignee')],
                    'hardware': [hardware_instance_row.id],
                })
        return Response({'data': new_id}, status=status.HTTP_201_CREATED)

class HardwareDetail(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, format=None):
        try:
            row = Hardware.table.get_row(pk)
            data = row.content
            data['id'] = row.id

            # Instances

            rows = HardwareInstance.table.get_rows(filters=[Filter('hardware', pk, 'link_row_has')])
            instances = []
            for row in rows:
                instance = row.content
                instance['id'] = row.id
                instance['status'] = row.values['status'].id
                instance['hardware'] = row.values['hardware'].id
                instance['assignee'] = row.values['assignee'].id
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
        if request.user.role.role == UserTypeEnum.VIEWER.value:
            return Response({'message': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        errors = {}

        hardware_serializer = HardwareSerializer(data=request.data)
        if not hardware_serializer.is_valid():
            errors.update(hardware_serializer.errors)

        hardware_instance_serializer = HardwareInstanceSerializer(data=request.data.get('one2m').get('instances').get('data'), many=True)

        if not hardware_instance_serializer.is_valid():
            errors['instances'] = hardware_instance_serializer.errors

        if errors:
            return Response({"message": "Invalid data", "errors": errors}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        row = Hardware.table.get_row(pk)
        instances_to_delete = request.data.get('one2m').get('instances').get('delete')

        if request.user.role.role in [UserTypeEnum.ADMIN.value, UserTypeEnum.SUPER_ADMIN.value, UserTypeEnum.ROOT_ADMIN.value]:
            row['name'] = request.data.get('name')
            row['brand'] = request.data.get('brand')
            row['type'] = request.data.get('type')
            row['model_number'] = request.data.get('model_number')
            row['description'] = request.data.get('description')

            for instance in instances_to_delete:
                HardwareInstance.table.get_row(instance).delete()

        row['for_deletion'] = request.data.get('for_deletion')
        row.update()

        instances = request.data.get('one2m').get('instances').get('data')
        for instance in instances:
            if 'id' in instance:
                if instance['id'] in instances_to_delete:
                    continue

                instance_row = HardwareInstance.table.get_row(instance['id'])
                if request.user.role.role in [UserTypeEnum.ADMIN.value, UserTypeEnum.SUPER_ADMIN.value, UserTypeEnum.ROOT_ADMIN.value]:
                    instance_row['serial_number'] = instance['serial_number']
                    instance_row['procurement_date'] = instance['procurement_date']
                    if instance.get('status'):
                        instance_row['status'] = [instance['status']]

                # Check if the new assignee is set and the current assignee is not set
                # Assign
                if instance.get('assignee') and len(instance_row['assignee']) == 0:
                    AssignmentLog.assign(instance['assignee'], hardware=instance['id'])

                # Check if the new assignee and current assignee are set
                # And if they are not equal
                # Assign and unassign
                if instance.get('assignee') and len(instance_row['assignee']) > 0 and instance.get('assignee') != instance_row.values['assignee'].id:
                    AssignmentLog.assign(instance['assignee'], hardware=instance['id'])
                    AssignmentLog.assign(instance_row['assignee'][0], hardware=instance['id'], assignment_type=2)

                # Check if the new assignee is not set and the current assignee
                # Unassign
                if not instance.get('assignee') and len(instance_row['assignee']) > 0:
                    AssignmentLog.assign(instance_row['assignee'][0], hardware=instance['id'], assignment_type=2)

                if instance.get('assignee'):
                    instance_row['assignee'] = [instance['assignee']]
                else:
                    instance_row['assignee'] = []

                instance_row.update()
            else:

                if request.user.role.role not in [UserTypeEnum.ADMIN.value, UserTypeEnum.SUPER_ADMIN.value, UserTypeEnum.ROOT_ADMIN.value]:
                    continue

                new_instance_row = {
                    'serial_number': instance.get('serial_number'),
                    'procurement_date': instance.get('procurement_date'),
                    'hardware': [pk],
                }

                if instance.get('status'):
                    new_instance_row['status'] = [instance.get('status')]

                if instance.get('assignee'):
                    new_instance_row['assignee'] = [instance.get('assignee')]

                hardware_instance_row = HardwareInstance.table.add_row(new_instance_row)

                if instance.get('assignee'):
                    AssignmentLog.assign(instance['assignee'], hardware=hardware_instance_row.id)

        return Response({'message': 'successful'})

    def delete(self, request, pk, format=None):
        if request.user.role.role not in [UserTypeEnum.ADMIN.value, UserTypeEnum.SUPER_ADMIN.value, UserTypeEnum.ROOT_ADMIN.value]:
            return Response({'message': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        
        row = Hardware.table.get_row(pk)
        row.delete()

        return Response({'message': 'Successful'}, status=status.HTTP_204_NO_CONTENT)