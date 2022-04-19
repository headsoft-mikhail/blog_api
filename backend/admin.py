from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from backend.models import User, Post, NotViewedPost, UserSubscription, ConfirmEmailToken



# Register your models here.
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Панель управления пользователями
    """
    model = User

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'second_name', 'last_name', 'nick_name')}),
        ('Contact info', {'fields': ('public_email', 'public_url', 'public_phone_number')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    ordering = ('last_login',)


@admin.register(ConfirmEmailToken)
class ConfirmEmailTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'key', 'created_at',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    pass


@admin.register(NotViewedPost)
class NotViewedPostAdmin(admin.ModelAdmin):
    pass


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    pass
