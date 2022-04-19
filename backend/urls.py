from django.urls import path, include
from rest_framework.routers import DefaultRouter
from backend import views

router = DefaultRouter()
router.register(r'accounts', views.AccountViewSet, basename="accounts")
router.register(r'confirm', views.ConfirmAccountViewSet, basename="confirm")
router.register(r'login', views.LoginViewSet, basename="login")

urlpatterns = [
    path('', include(router.urls)),
]
