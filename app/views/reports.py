from rest_framework.views import APIView
import json
from app.views.hardware_instance import HardwareInstanceList
from app.views.software_instance import SoftwareInstanceList
import datetime

class SoftwareNearExpiry(APIView):
    def get(self, request):
        search = json.loads(request._request.GET.copy().get('search', '{}'))
        search['filters'] = search['filters'] if 'filters' in search else {}

        seven_days_from_now = datetime.datetime.now() + datetime.timedelta(days=7)

        search['filters']['software_expiration_date'] = {
            'constraints': [
                {
                    'value': seven_days_from_now.strftime('%Y-%m-%d'),
                    'matchMode': 'date_before_or_equal'
                }
            ]
        }

        get_params = request._request.GET.copy()
        get_params['search'] = json.dumps(search)
        request._request.GET = get_params

        response = SoftwareInstanceList.as_view()(request._request)

        return response

class HardwareNeedingMaintenance(APIView):
    def get(self, request):
        search = json.loads(request._request.GET.copy().get('search', '{}'))
        search['filters'] = search['filters'] if 'filters' in search else {}


        search['filters']['status_formula'] = {
            'constraints': [
                {
                    'value': 'For Repair',
                    'matchMode': 'equals'
                }
            ]
        }

        get_params = request._request.GET.copy()
        get_params['search'] = json.dumps(search)
        request._request.GET = get_params

        response = HardwareInstanceList.as_view()(request._request)

        return response

class HardwareNotAssigned(APIView):
    def get(self, request):
        search = json.loads(request._request.GET.copy().get('search', '{}'))
        search['filters'] = search['filters'] if 'filters' in search else {}

        search['filters']['status_formula'] = {
            'constraints': [
                {
                    'value': 'Unassigned',
                    'matchMode': 'equals'
                }
            ]
        }

        get_params = request._request.GET.copy()
        get_params['search'] = json.dumps(search)
        request._request.GET = get_params

        response = HardwareInstanceList.as_view()(request._request)

        return response

class SoftwareNotAssigned(APIView):
    def get(self, request):
        search = json.loads(request._request.GET.copy().get('search', '{}'))
        search['filters'] = search['filters'] if 'filters' in search else {}

        search['filters']['status_formula'] = {
            'constraints': [
                {
                    'value': 'Unassigned',
                    'matchMode': 'equals'
                }
            ]
        }

        get_params = request._request.GET.copy()
        get_params['search'] = json.dumps(search)
        request._request.GET = get_params

        response = SoftwareInstanceList.as_view()(request._request)

        return response