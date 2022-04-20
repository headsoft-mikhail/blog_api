from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from django_rest_passwordreset.tokens import get_token_generator


# Create your models here.
class UserManager(BaseUserManager):
    """
    Миксин для управления пользователями
    """

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """

        if not email:
            raise ValueError('Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_active', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Пользователи"""

    username = None
    email = models.EmailField(verbose_name='Email',
                              unique=True)
    first_name = models.CharField(max_length=50,
                                  verbose_name='Имя',
                                  blank=False)
    second_name = models.CharField(max_length=50,
                                   verbose_name='Отчество',
                                   blank=True)
    last_name = models.CharField(max_length=50,
                                 verbose_name='Фамилия',
                                 blank=False)
    nick_name = models.CharField(max_length=50,
                                 verbose_name='Никнейм',
                                 blank=True)
    public_phone_number = PhoneNumberField(verbose_name='Номер телефона',
                                           blank=True)
    public_url = models.URLField(verbose_name='Сайт/соцсеть',
                                 blank=True)
    public_email = models.EmailField(verbose_name='Email',
                                     blank=True)

    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = "Список пользователей"
        ordering = ('-email',)

    def __str__(self):
        return (self.first_name + ' ' + self.last_name).strip()


class Post(models.Model):
    """Публикация """
    created_at = models.DateTimeField(verbose_name='Время публикации',
                                      auto_now_add=True)
    owner = models.ForeignKey(User,
                              verbose_name='Автор',
                              related_name="posts",
                              on_delete=models.CASCADE,
                              blank=False)
    content = models.TextField(verbose_name='Текст',
                               blank=False)
    nesting_level = models.PositiveIntegerField(verbose_name='Уровень вложенности',
                                                default=0)

    class Meta:
        verbose_name = 'Публикация'
        verbose_name_plural = "Список публикаций"
        ordering = ('-created_at',)

    def __str__(self):
        return f'{super().__str__()}\n' \
               f'{self.content}'


class ParentsChildren(models.Model):
    parent = models.ForeignKey(Post,
                               verbose_name='Предок',
                               related_name='child',
                               on_delete=models.CASCADE)
    child = models.ForeignKey(Post,
                              verbose_name='Потомок',
                              related_name='parent',
                              on_delete=models.CASCADE)

    class Meta:
        unique_together = ("parent", "child")
        verbose_name_plural = "Публикации и комментарии"


class NotViewedPost(models.Model):
    """Непросмотренные посты"""
    user = models.ForeignKey(User,
                             verbose_name='Просмотрели',
                             related_name='not_viewed_by_users',
                             on_delete=models.CASCADE)
    post = models.ForeignKey(Post,
                             verbose_name='Просмотрены',
                             related_name='not_viewed_posts',
                             on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Непросмотренные публикации"

    unique_together = ("user", "post")


class UserSubscription(models.Model):
    owner = models.ForeignKey(User,
                              verbose_name='Подписки',
                              related_name='subscriptions',
                              on_delete=models.CASCADE)
    author = models.ForeignKey(User,
                               verbose_name='Подписчики',
                               related_name='subscribers',
                               on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("owner", "author")
        verbose_name_plural = "Подписки и подписчики"


class ConfirmEmailToken(models.Model):
    class Meta:
        verbose_name = 'Токен подтверждения Email'
        verbose_name_plural = 'Токены подтверждения Email'

    @staticmethod
    def generate_key():
        """Генерирует псевдослучайную последовательность используя os.urandom и binascii.hexlify"""
        return get_token_generator().generate_token()

    user = models.ForeignKey(User,
                             related_name='confirm_email_tokens',
                             on_delete=models.CASCADE,
                             verbose_name="Владелец токена")
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name="Время создания")
    key = models.CharField(verbose_name="Токен",
                           max_length=5,
                           db_index=True,
                           unique=True)

    class Meta:
        verbose_name = 'Токен'
        verbose_name_plural = "Токены подтверждения"

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.key
