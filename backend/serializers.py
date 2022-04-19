from rest_framework import serializers
from backend.models import User, Post, UserSubscription, ConfirmEmailToken


class DynamicModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed, and takes in a "nested"
    argument to return nested serializers
    """

    def __init__(self, *args, **kwargs):
        include = kwargs.pop("include", None)
        exclude = kwargs.pop("exclude", None)
        depth = kwargs.pop("depth", None)

        if depth is not None:
            self.Meta.depth = depth

        super(DynamicModelSerializer, self).__init__(*args, **kwargs)

        if include is not None:
            for field in include:
                if field not in self.fields:
                    self.Meta.fields.append(field)

        if exclude is not None:
            for field_name in exclude:
                self.Meta.fields.pop(field_name)


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
        read_only_fields = ('id', )


class UserSerializer(serializers.ModelSerializer):
    """Пользователи"""
    subscribers = UserMainInfoSerializer(read_only=True, many=True)
    subscriptions = UserMainInfoSerializer(read_only=True, many=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'first_name', 'second_name', 'last_name',
                  'nick_name', 'subscriptions', 'subscribers')
        read_only_fields = ('id',)
        extra_kwargs = {
            'password': {'write_only': True}
        }


class PostSerializer(DynamicModelSerializer):
    """Публикации"""
    owner = UserMainInfoSerializer(read_only=True)

    class Meta:
        model = Post
        fields = ('id', 'created_at', 'owner', 'content', 'nesting_level')
        read_only_fields = ('id',)

    def get_fields(self):
        fields = super(PostSerializer, self).get_fields()
        fields['comments'] = PostSerializer(many=True)
        return fields


class SubscriptionSerializer(serializers.ModelSerializer):
    """Подписки"""
    owner = UserMainInfoSerializer(read_only=True)
    author = UserMainInfoSerializer(read_only=True)

    class Meta:
        model = UserSubscription
        fields = ['owner', 'author', 'created_at']




