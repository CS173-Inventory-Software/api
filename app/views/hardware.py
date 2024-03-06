from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from ..baserow_client import hardware_table

class HardwareList(APIView):
    def get(self, request, format=None):
        hardware = []
        for row in hardware_table.get_rows():
            hardware.append(row.content)
        return Response({'data': hardware}, status=status.HTTP_200_OK)
