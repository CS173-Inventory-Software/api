from rest_framework import serializers

class HardwareSerializer(serializers.Serializer):
    name = serializers.CharField()
    brand = serializers.CharField()
    type = serializers.CharField()
    model_number = serializers.CharField()
    description = serializers.CharField()

class HardwareInstanceSerializer(serializers.Serializer):
    serial_number = serializers.CharField()
    procurement_date = serializers.DateField()
    status = serializers.IntegerField(required=False)
    assignee = serializers.IntegerField(required=False)
    hardware = serializers.IntegerField(required=False)