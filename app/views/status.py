from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from ..baserow_client import get_baserow_operator
from ..baserow_client.status import Status

class StatusList(APIView):
    def get(self, request, format=None):
        entities = []

        rows = Status.table.get_rows()

        row_counter = 0
        for row in rows:
            data = row.content
            data['id'] = row.id
            entities.append(data)
        return Response({'data': entities}, status=status.HTTP_200_OK)
