from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from ..baserow_client import status_table, get_baserow_operator
from ..baserow_client.user import UserType
from baserowapi import Filter
import json

class UserTypeList(APIView):
    def get(self, request, format=None):
        entities = []

        rows = UserType.table.get_rows(filters=[Filter('label', 'Root Admin', 'not_equal')])

        row_counter = 0
        for row in rows:
            data = row.content
            data['id'] = row.id
            entities.append(data)
        return Response({'data': entities}, status=status.HTTP_200_OK)
