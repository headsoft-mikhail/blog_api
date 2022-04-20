from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django_rest_passwordreset.views import ResetPasswordConfirmViewSet, ResetPasswordRequestTokenViewSet
from backend import views

router = DefaultRouter()
router.register(r'accounts', views.AccountViewSet, basename="accounts")
router.register(r'confirm', views.ConfirmAccountViewSet, basename="confirm")
router.register(r'login', views.LoginViewSet, basename="login")
router.register(r'password_reset', ResetPasswordRequestTokenViewSet, basename="password_reset")
router.register(r'password_confirm', ResetPasswordConfirmViewSet, basename="password_confirm")
router.register(r'subscriptions', views.SubscriptionsViewSet, basename="subscriptions")
router.register(r'subscribers', views.SubscribersViewSet, basename="subscribers")
router.register(f'posts', views.PostsViewSet, basename="posts")
router.register(f'feed', views.FeedViewSet, basename="feed")

urlpatterns = [
    path('', include(router.urls))
]
