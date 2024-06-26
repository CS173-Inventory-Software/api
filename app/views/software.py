from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from app.serializers.software import SoftwareInstanceSerializer, SoftwareSerializer, SoftwareSubscriptionSerializer
from ..baserow_client import get_baserow_operator
from ..baserow_client.software import Software, SoftwareInstance, SoftwareSubscription
from ..baserow_client.assignment_log import AssignmentLog
from ..baserow_client.user import UserTypeEnum
from baserowapi import Filter
import json
from django.http import Http404
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated

class SoftwareList(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
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
        
        rows = Software.table.get_rows(**kwargs)

        row_counter = 0
        for row in rows:
            row_counter += 1
            if row_counter - 1 < page * size or row_counter - 1 >= (page + 1) * size:
                continue
            data = row.content
            data['id'] = row.id
            software.append(data)
        return Response({'data': software, 'totalRecords': row_counter}, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        if request.user.role.role not in [UserTypeEnum.ADMIN.value, UserTypeEnum.SUPER_ADMIN.value, UserTypeEnum.ROOT_ADMIN.value]:
            return Response({'message': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        errors = {}

        software_serializer = SoftwareSerializer(data=request.data)
        if not software_serializer.is_valid():
            errors.update(software_serializer.errors)

        software_instance_serializer = SoftwareInstanceSerializer(data=request.data.get('one2m').get('instances').get('data'), many=True)

        if not software_instance_serializer.is_valid():
            errors['instances'] = software_instance_serializer.errors

        software_subscription_serializer = SoftwareSubscriptionSerializer(data=request.data.get('one2m').get('subscriptions').get('data'), many=True)

        if not software_subscription_serializer.is_valid():
            errors['subscriptions'] = software_subscription_serializer.errors

        if errors:
            return Response({"message": "Invalid data", "errors": errors}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        new_row = {
            'name': request.data.get('name'),
            'brand': request.data.get('brand'),
            'type': request.data.get('type'),
            'version_number': request.data.get('version_number'),
            'description': request.data.get('description'),
            'expiration_date': request.data.get('expiration_date'),
        }
        added_row = Software.table.add_row(new_row)
        new_id = added_row.id

        # Instances
        instances = request.data.get('one2m').get('instances').get('data')
        for instance in instances:
            new_instance_row = {
                'serial_key': instance.get('serial_key'),
                'software': [new_id],
                'status': [instance.get('status')] if instance.get('status') else [],
            }
            if instance.get("assignee"):
                new_instance_row['assignee'] = [instance.get('assignee')]
                # Add assignment log
            software_instance_row = SoftwareInstance.table.add_row(new_instance_row)
            if instance.get("assignee"):
                AssignmentLog.assign({
                    'user': [instance.get('assignee')],
                    'software': [software_instance_row.id],
                })

        # Subscriptions
        subscriptions = request.data.get('one2m').get('subscriptions').get('data')
        for subscription in subscriptions:
            new_subscription_row = {
                'start': subscription.get('start'),
                'end': subscription.get('end'),
                'software': [new_id],
                'number_of_licenses': int(subscription.get('number_of_licenses')),
            }
            SoftwareSubscription.table.add_row(new_subscription_row)
        return Response({'data': new_id}, status=status.HTTP_201_CREATED)

class SoftwareDetail(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, format=None):
        try:
            row = Software.table.get_row(pk)
            data = row.content
            data['id'] = row.id

            # Instances

            rows = SoftwareInstance.table.get_rows(filters=[Filter('software', pk, 'link_row_has')])
            instances = []
            for row in rows:
                instance = row.content
                instance['id'] = row.id
                instance['status'] = row.values['status'].id
                instance['software'] = row.values['software'].id
                instance['assignee'] = row.values['assignee'].id
                instances.append(instance)

            # Subscriptions

            rows = SoftwareSubscription.table.get_rows(filters=[Filter('software', pk, 'link_row_has')])
            subscriptions = []
            for row in rows:
                subscription = row.content
                subscription['id'] = row.id
                subscription['software'] = row.values['software'].id
                subscription['number_of_licenses'] = int(subscription['number_of_licenses'])
                subscriptions.append(subscription)


            data['one2m'] = {
                'instances': {
                    'data': instances
                },
                'subscriptions': {
                    'data': subscriptions
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

        software_serializer = SoftwareSerializer(data=request.data)
        if not software_serializer.is_valid():
            errors.update(software_serializer.errors)

        software_instance_serializer = SoftwareInstanceSerializer(data=request.data.get('one2m').get('instances').get('data'), many=True)

        if not software_instance_serializer.is_valid():
            errors['instances'] = software_instance_serializer.errors

        software_subscription_serializer = SoftwareSubscriptionSerializer(data=request.data.get('one2m').get('subscriptions').get('data'), many=True)

        if not software_subscription_serializer.is_valid():
            errors['subscriptions'] = software_subscription_serializer.errors

        if errors:
            return Response({"message": "Invalid data", "errors": errors}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        row = Software.table.get_row(pk)
        instances_to_delete = request.data.get('one2m').get('instances').get('delete')

        if request.user.role.role in [UserTypeEnum.ADMIN.value, UserTypeEnum.SUPER_ADMIN.value, UserTypeEnum.ROOT_ADMIN.value]:
            row['name'] = request.data.get('name')
            row['brand'] = request.data.get('brand')
            row['version_number'] = request.data.get('version_number')
            row['description'] = request.data.get('description')
            row['expiration_date'] = request.data.get('expiration_date')
            row.update()

            for instance in instances_to_delete:
                SoftwareInstance.table.get_row(instance).delete()

        # Instances

        instances = request.data.get('one2m').get('instances').get('data')
        for instance in instances:
            if 'id' in instance:
                if instance['id'] in instances_to_delete:
                    continue

                instance_row = SoftwareInstance.table.get_row(instance['id'])

                if request.user.role.role in [UserTypeEnum.ADMIN.value, UserTypeEnum.SUPER_ADMIN.value, UserTypeEnum.ROOT_ADMIN.value]:
                    instance_row['serial_key'] = instance['serial_key']
                    instance_row['status'] = [instance['status']] if instance.get('status') else []

                current_assignee = instance_row['assignee']
                assignment_type = None

                # Check if the new assignee is set and the current assignee is not set
                # Assign
                if instance.get('assignee') and len(instance_row['assignee']) == 0:
                    AssignmentLog.assign(instance['assignee'], software=instance['id'])

                # Check if the new assignee and current assignee are set
                # And if they are not equal
                # Assign and unassign
                if instance.get('assignee') and len(instance_row['assignee']) > 0 and instance.get('assignee') != instance_row.values['assignee'].id:
                    AssignmentLog.assign(instance['assignee'], software=instance['id'])
                    AssignmentLog.assign(instance_row['assignee'][0], software=instance['id'], assignment_type=2)

                # Check if the new assignee is not set and the current assignee
                # Unassign
                if not instance.get('assignee') and len(instance_row['assignee']) > 0:
                    AssignmentLog.assign(instance_row['assignee'][0], software=instance['id'], assignment_type=2)

                if instance.get('assignee'):
                    instance_row['assignee'] = [instance['assignee']]
                else:
                    instance_row['assignee'] = []

                instance_row.update()
            else:

                if request.user.role.role not in [UserTypeEnum.ADMIN.value, UserTypeEnum.SUPER_ADMIN.value, UserTypeEnum.ROOT_ADMIN.value]:
                    continue

                new_instance_row = {
                    'serial_key': instance.get('serial_key'),
                    'software': [pk],
                }

                if instance.get('status'):
                    new_instance_row['status'] = [instance.get('status')]

                if instance.get('assignee'):
                    new_instance_row['assignee'] = [instance.get('assignee')]

                software_instance_row = SoftwareInstance.table.add_row(new_instance_row)

                if instance.get('assignee'):
                    AssignmentLog.assign(instance['assignee'], software=software_instance_row.id)

        # Subscriptions

        subscriptions_to_delete = request.data.get('one2m').get('subscriptions').get('delete')
        if request.user.role.role in [UserTypeEnum.ADMIN.value, UserTypeEnum.SUPER_ADMIN.value, UserTypeEnum.ROOT_ADMIN.value]:
            for subscription in subscriptions_to_delete:
                SoftwareSubscription.table.get_row(subscription).delete()

        subscriptions = request.data.get('one2m').get('subscriptions').get('data')
        for subscription in subscriptions:
            if 'id' in subscription:
                if subscription['id'] in subscriptions_to_delete or request.user.role.role not in [UserTypeEnum.ADMIN.value, UserTypeEnum.SUPER_ADMIN.value, UserTypeEnum.ROOT_ADMIN.value]:
                    continue

                subscription_row = SoftwareSubscription.table.get_row(subscription['id'])

                subscription_row['start'] = subscription['start']
                subscription_row['end'] = subscription['end']
                subscription_row['number_of_licenses'] = int(subscription['number_of_licenses'])
                subscription_row.update()

            else:
                if request.user.role.role not in [UserTypeEnum.ADMIN.value, UserTypeEnum.SUPER_ADMIN.value, UserTypeEnum.ROOT_ADMIN.value]:
                    continue

                SoftwareSubscription.create(pk, subscription.get('start'), subscription.get('end'), int(subscription.get('number_of_licenses')))

        return Response({'message': 'successful'})

    def delete(self, request, pk, format=None):
        if request.user.role.role not in [UserTypeEnum.ADMIN.value, UserTypeEnum.SUPER_ADMIN.value, UserTypeEnum.ROOT_ADMIN.value]:
            return Response({'message': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        
        row = Software.table.get_row(pk)
        row.delete()

        return Response({'message': 'Successful'}, status=status.HTTP_204_NO_CONTENT)