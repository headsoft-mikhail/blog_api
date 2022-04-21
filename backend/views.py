from django.shortcuts import render
from rest_framework.mixins import DestroyModelMixin
from rest_framework.response import Response
from django_filters import rest_framework as filters
from rest_framework.viewsets import ViewSet, ModelViewSet
from rest_framework.authtoken.models import Token
from rest_framework import status
from django.contrib.auth import authenticate

from backend.permissions import IsAuthenticated, IsNotAuthenticated, IsOwnerOrAdmin, IsActive
from backend.serializers import UserMainInfoSerializer, UserSerializer, PostSerializer, SubscriptionSerializer, \
    SubscriberSerializer, ConfirmEmailSerializer
from backend.models import User, Post, UserSubscription, ConfirmEmailToken, ParentsChildren
from backend.filters import PostsFilter
from backend.tasks import on_new_user_registered, on_account_deleted


# Create your views here.
class LoginViewSet(ViewSet, DestroyModelMixin):
    """Для входа/выхода из аккаунта"""

    def create(self, request, *args, **kwargs):
        """Вход в аккаунт, генерация токена"""
        user = authenticate(request,
                            username=request.data.get('email', None),
                            password=request.data.get('password', None))
        if user is not None:
            if user.is_active:
                token, _ = Token.objects.get_or_create(user=user)
                return Response({'Status': True,
                                 'Token': token.key},
                                status=status.HTTP_201_CREATED)
        return Response({'Status': False},
                        status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, *args, **kwargs):
        """Выход из аккаунта, удаление токена"""
        token = Token.objects.get(user_id=request.user.id)
        if token:
            self.perform_destroy(token)
            return Response({'Status': True},
                            status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'Status': False},
                            status=status.HTTP_400_BAD_REQUEST)

    def get_permissions(self):
        """Получение прав для действий."""
        if self.action in ["create"]:
            return [IsNotAuthenticated()]
        elif self.action in ["destroy"]:
            return [IsAuthenticated()]
        else:
            return []


class AccountViewSet(ModelViewSet):
    """Для создания/просмотра/редактирования/удаления аккаунтов"""
    queryset = User.objects.all()

    def perform_create(self, serializer):
        super().perform_create(serializer)
        serializer.instance.set_password(serializer.instance.password)
        serializer.instance.save()
        token, _ = ConfirmEmailToken.objects.get_or_create(user_id=serializer.instance.id)
        on_new_user_registered.delay(serializer.instance.email, token.key)

    def perform_update(self, serializer):
        super().perform_update(serializer)
        if "password" in serializer.validated_data.keys():
            serializer.instance.set_password(serializer.instance.password)
        serializer.instance.save()

    def destroy(self, request, *args, **kwargs):
        """Удаление аккаунта"""
        user = self.get_object()
        email = user.email
        self.perform_destroy(user)
        on_account_deleted(email)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_permissions(self):
        """Получение прав для действий."""
        if self.action in ["create"]:
            return [IsNotAuthenticated()]
        elif self.action in ["update", "partial_update", "destroy"]:
            return [IsOwnerOrAdmin()]
        elif self.action in ["retrieve"]:
            return [IsAuthenticated()]
        else:
            return []

    def get_serializer_class(self):
        if self.action in ["list"]:
            return UserMainInfoSerializer
        else:
            return UserSerializer


class ConfirmAccountViewSet(ModelViewSet):
    """Класс для подтверждения почтового адреса"""
    serializer_class = ConfirmEmailSerializer

    def create(self, request):
        """Подтверждение почтового адреса"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        if serializer.instance.get('status', False) is False:
            return Response({'Activation status': 'Wrong email or token'},
                            status=status.HTTP_403_FORBIDDEN,
                            headers=headers)
        else:
            return Response({'Activation status': 'Success'},
                            status=status.HTTP_201_CREATED,
                            headers=headers)


class SubscriptionsViewSet(ModelViewSet):
    """Для создания/просмотра/удаления подписок"""
    serializer_class = SubscriptionSerializer

    def get_queryset(self):
        if self.action in ["list"]:
            return UserSubscription.objects.filter(owner=self.request.user).order_by("created_at")
        else:
            return UserSubscription.objects.none()

    def perform_create(self, serializer):
        """Создание подписки"""
        serializer.save(owner=self.request.user,
                        author=User.objects.get(id=self.request.data.get('author', None)))

    def destroy(self, request, *args, **kwargs):
        """Отписка"""
        instance = UserSubscription.objects.filter(owner=self.request.user, author=kwargs['pk']).first()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_permissions(self):
        if self.action in ["list", "create"]:
            return [IsActive()]
        elif self.action in ["destroy"]:
            return [IsOwnerOrAdmin()]
        else:
            return []


class SubscribersViewSet(ModelViewSet):
    """Для просмотра подписчиков"""
    serializer_class = SubscriberSerializer
    queryset = UserSubscription.objects.none()

    def get_queryset(self):
        return UserSubscription.objects.filter(author=self.request.user).order_by("created_at")

    def get_permissions(self):
        """Получение прав для действий."""
        if self.action in ["list"]:
            return [IsActive()]
        else:
            return []


class PostsViewSet(ModelViewSet):
    """Для создания/удаления/редактирования постов."""
    queryset = Post.objects.select_related('owner').order_by('-created_at')
    serializer_class = PostSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = PostsFilter

    def perform_create(self, serializer):
        """Создание новой публикации/комментария с записью его потомком во всех его родителей"""
        if 'parent_id' in self.request.data.keys():
            parent = Post.objects.get(id=self.request.data['parent_id'])
            child = serializer.save(owner=self.request.user, nesting_level=parent.nesting_level + 1)
            ParentsChildren(parent=parent, child=child).save()
            ParentsChildren.objects.bulk_create(
                [
                    ParentsChildren(parent=item.parent, child=child)
                    for item
                    in ParentsChildren.objects.prefetch_related('parent').filter(child=parent)
                ])
        else:
            serializer.save(owner=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        """Просмотр публикации/поста,
        при указании nests_down в ответе будут также комментарии вложенностью
        ниже самой публикации на указанное значение"""
        nests_down = self.request.data.get('nests_down', None)
        post = Post.objects.filter(id=kwargs['pk'])
        if nests_down == "all":
            children = Post.objects.prefetch_related('parent').order_by('-created_at').filter(
                parent__parent__id=kwargs['pk'], nesting_level__gte=post.first().nesting_level)
        elif type(nests_down) is int:
            children = Post.objects.prefetch_related('parent').order_by('-created_at').filter(
                parent__parent__id=kwargs['pk'], nesting_level__lte=post.first().nesting_level + nests_down)
        else:
            self.queryset = post
            return super().retrieve(request, *args, **kwargs)
        self.queryset = (post | children).distinct()
        return super().list(request, *args, **kwargs)

    def get_permissions(self):
        """Получение прав для действий."""
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated()]
        elif self.action in ["create"]:
            return [IsActive()]
        elif self.action in ["destroy"]:
            return [IsOwnerOrAdmin()]
        else:
            return []


class FeedViewSet(ModelViewSet):
    """Для создания/удаления/редактирования постов."""
    queryset = Post.objects.none()
    serializer_class = PostSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = PostsFilter

    def list(self, request, *args, **kwargs):
        """Просмотр ленты"""
        authors = [item.author.id for item in UserSubscription.objects.filter(owner=self.request.user.id)]
        self.queryset = Post.objects.select_related('owner').order_by('-created_at').filter(owner_id__in=authors)
        response = super().list(request, *args, **kwargs)
        return response

    def get_permissions(self):
        """Получение прав для действий."""
        if self.action in ["list"]:
            return [IsAuthenticated()]
        else:
            return []
