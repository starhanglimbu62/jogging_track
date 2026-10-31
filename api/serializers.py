from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Entry, UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('id', 'role')
        read_only_fields = ('id', 'role')


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'profile')
        read_only_fields = ('id', 'profile')


class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        read_only_fields = ('id',)
        extra_kwargs = {'password': {'write_only': True, 'min_length': 8}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        UserProfile.objects.create(user=user, role='USER')
        return user


class EntrySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True, required=False)
    average_speed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Entry
        fields = ('id', 'distance', 'duration', 'date', 'user', 'user_id', 'average_speed')
        read_only_fields = ('id', 'user', 'average_speed')

    def get_average_speed(self, obj):
        return round(float(obj.distance) / obj.duration, 2) if obj.duration else 0

    def validate(self, attrs):
        if attrs.get('distance', 0) < 0 or attrs.get('duration', 0) <= 0:
            raise serializers.ValidationError('Distance must be non-negative and duration must be positive.')
        request = self.context.get('request')
        if request and request.user.profile.role != 'ADMIN':
            attrs.pop('user_id', None)
        return attrs
