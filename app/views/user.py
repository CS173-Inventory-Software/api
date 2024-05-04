from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from ..baserow_client import get_baserow_operator
from ..baserow_client.user import User, UserType, UserTypeEnum
from baserowapi import Filter
import json
from django.http import Http404
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from app.views.hardware_instance import HardwareInstanceList
from app.views.software_instance import SoftwareInstanceList

class UserList(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
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
        if request.user.role.role not in [UserTypeEnum.SUPER_ADMIN.value, UserTypeEnum.ROOT_ADMIN.value]:
            return Response({'message': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        added_row = User.create(
            request.data.get('email'), 
            request.data.get('type')
        )

        return Response({'data': added_row.id}, status=status.HTTP_201_CREATED)

class UserDetail(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk, format=None):
        try:
            row = User.table.get_row(pk)
        except Exception as e:
            raise Http404

        data = row.content
        data['id'] = row.id
        data['type'] = row.values['type'].id
        del data['auth_code']
        del data['auth_expiry']
        return Response({'data': data})

    def put(self, request, pk, format=None):
        if request.user.role.role not in [UserTypeEnum.SUPER_ADMIN.value, UserTypeEnum.ROOT_ADMIN.value]:
            return Response({'message': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        if request.data.get('type') not in [UserTypeEnum.VIEWER.value, UserTypeEnum.CLERK.value, UserTypeEnum.ADMIN.value, UserTypeEnum.SUPER_ADMIN.value]:
            return Response({'message': 'Invalid user type'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        row = User.table.get_row(pk)
        row['email'] = request.data.get('email')
        row['type'] = [request.data.get('type')]
        row.update()
        return Response({'message': 'Successful'})
    
    def delete(self, request, pk, format=None):
        if request.user.role.role not in [UserTypeEnum.SUPER_ADMIN.value, UserTypeEnum.ROOT_ADMIN.value]:
            return Response({'message': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        
        row = User.table.get_row(pk)
        if row.values['type'].id == UserTypeEnum.ROOT_ADMIN.value or (row.values['type'].id == UserTypeEnum.SUPER_ADMIN.value and request.user.role.role != UserTypeEnum.ROOT_ADMIN.value):
            return Response({'message': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        
        row.delete()

        return Response({'message': 'Successful'}, status=status.HTTP_204_NO_CONTENT)

class UserAssignedHardware(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        search = json.loads(request._request.GET.copy().get('search', '{}'))
        search['filters'] = search['filters'] if 'filters' in search else {}

        search['filters']['assignee_formula'] = {
            'constraints': [
                {
                    'value': request.user.email,
                    'matchMode': 'equals'
                }
            ]
        }

        get_params = request._request.GET.copy()
        get_params['search'] = json.dumps(search)
        request._request.GET = get_params

        response = HardwareInstanceList.as_view()(request._request)

        return response
\
class UserAssignedSoftware(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        search = json.loads(request._request.GET.copy().get('search', '{}'))
        search['filters'] = search['filters'] if 'filters' in search else {}

        search['filters']['assignee_formula'] = {
            'constraints': [
                {
                    'value': request.user.email,
                    'matchMode': 'equals'
                }
            ]
        }

        get_params = request._request.GET.copy()
        get_params['search'] = json.dumps(search)
        request._request.GET = get_params

        response = SoftwareInstanceList.as_view()(request._request)

        return response