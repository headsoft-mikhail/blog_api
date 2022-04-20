from rest_framework import serializers
from backend.models import User, Post, UserSubscription, ConfirmEmailToken, ParentsChildren


class ConfirmEmailSerializer(serializers.Serializer):
    """Класс для подтверждения email"""
    token = serializers.CharField(max_length=5)
    email = serializers.EmailField()

    def create(self, validated_data):
        """Подтверждение email"""
        token = ConfirmEmailToken.objects.filter(user__email=validated_data['email'],
                                                 key=validated_data['token']).first()
        if token:
            token.user.is_active = True
            token.user.save()
            token.delete()
            validated_data['status'] = True
        else:
            validated_data['status'] = False
        return validated_data

    def update(self, instance, validated_data):
        super().update()


class UserMainInfoSerializer(serializers.ModelSerializer):
    """Пользователи (сокращенный)"""

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'nick_name')
        read_only_fields = ('id',)


class SubscriptionSerializer(serializers.ModelSerializer):
    """Подписки"""
    author = UserMainInfoSerializer(read_only=True, required=False)

    class Meta:
        model = UserSubscription
        fields = ['author', 'created_at']


class SubscriberSerializer(serializers.ModelSerializer):
    """Подписчики"""
    owner = UserMainInfoSerializer(read_only=True)

    class Meta:
        model = UserSubscription
        fields = ['owner', 'created_at']


class UserSerializer(serializers.ModelSerializer):
    """Пользователи"""
    subscribers = SubscriptionSerializer(read_only=True, many=True)
    subscriptions = SubscriberSerializer(read_only=True, many=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'first_name', 'second_name', 'last_name',
                  'nick_name', 'subscriptions', 'subscribers')
        read_only_fields = ('id',)
        extra_kwargs = {
            'password': {'write_only': True}
        }


class PostSerializer(serializers.ModelSerializer):
    """Публикации"""
    owner = UserMainInfoSerializer(read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'created_at', 'owner', 'content', 'parent', 'child', 'nesting_level']
        read_only_fields = ('id', 'parent', 'child')
