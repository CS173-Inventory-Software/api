from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from ..baserow_client import hardware_table

class HardwareList(APIView):
    def get(self, request, format=None):
        hardware = []
        for row in hardware_table.get_rows():
            data = row.content
            data['id'] = row.id
            if row['status'] == []:
                data['status'] = 'Available'
            hardware.append(data)
        return Response({'data': hardware}, status=status.HTTP_200_OK)
