from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from ..baserow_client.user import UserType
from baserowapi import Filter
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated

class UserTypeList(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        entities = []

        rows = UserType.table.get_rows(filters=[Filter('label', 'Root Admin', 'not_equal')])

        row_counter = 0
        for row in rows:
            data = row.content
            data['id'] = row.id
            entities.append(data)
        return Response({'data': entities}, status=status.HTTP_200_OK)
