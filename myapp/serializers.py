from rest_framework import serializers
from .models import User

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'password')

    def create(self, validated_data):
        user = User(email=validated_data['email'], is_active=False)
        user.set_password(validated_data['password'])
        user.save()
        return user


class VerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField()


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()