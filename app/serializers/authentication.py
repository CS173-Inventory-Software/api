from rest_framework import serializers

class RequestCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()