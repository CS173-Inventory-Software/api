from rest_framework import serializers

class SoftwareSerializer(serializers.Serializer):
    name = serializers.CharField()
    brand = serializers.CharField()
    version_number = serializers.CharField()
    description = serializers.CharField()
    expiration_date = serializers.DateField()

class SoftwareInstanceSerializer(serializers.Serializer):
    serial_key = serializers.CharField()
    status = serializers.IntegerField(required=False, allow_null=True)
    assignee = serializers.IntegerField(required=False, allow_null=True)
    software = serializers.IntegerField(required=False, allow_null=True)

class SoftwareSubscriptionSerializer(serializers.Serializer):
    start = serializers.DateField()
    end = serializers.DateField()
    number_of_licenses = serializers.IntegerField()
    software = serializers.IntegerField(required=False, allow_null=True)