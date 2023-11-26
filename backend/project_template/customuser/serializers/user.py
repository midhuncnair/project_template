"""
The serializers of customuser module
"""


# from __future__ import


__all__ = [
    'UserSerializer',
    'UserProfileSerializer',
]
__version__ = "1.0.0.0"
__author__ = "Midhun C Nair <midhunch@gmail.com>"
__maintainers__ = [
    "Midhun C Nair <midhunch@gmail.com>",
]


from rest_framework import serializers

from django.contrib.auth import get_user_model
from customuser.models import UserProfile


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Defines the serializer class for User
    """

    root_user_id = serializers.SerializerMethodField()
    def get_root_user_id(self, obj):
        return obj.id

    def create(self, validated_data):
        """
        Defines the create.
        """
        model_obj = User.objects.create(**validated_data)
        return model_obj

    def update(self, instance, validated_data):
        """
        Defines the update.
        """
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.save()
        return instance

    class Meta:
        model = User
        # fields = '__all__'
        exclude = (
            'password',
            'is_staff',
            'groups',
            'user_permissions',
        )


class UserProfileSerializer(serializers.ModelSerializer):
    """Defines the serializer class for UserProfile
    """
    id = serializers.SerializerMethodField()
    def get_id(self, obj):
        return obj.user_profile_id

    name = serializers.SerializerMethodField()
    def get_name(self, obj):
        return obj.name

    email = serializers.SerializerMethodField()
    def get_email(self, obj):
        return obj.user.email

    image = serializers.SerializerMethodField()
    def get_image(self, obj):
        return obj.thumbnail

    user = UserSerializer(read_only=True)
    # def create(self, validated_data):
    #     """Defines the create
    #     """
    #     model_obj = UserProfile.objects.get_or_create(**validated_data)
    #     return model_obj

    def update(self, instance, validated_data):
        """Defines the update
        """
        # instance.save()
        return instance

    class Meta:
        model = UserProfile
        # fields = '__all__'
        exclude = (
            'password_version',
        )
