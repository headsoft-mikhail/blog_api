from blog_api.celery import app
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
import sys


@app.task
def on_new_user_registered(email, token):
    """Отправляем письмо с токеном подтверждением почты"""
    text_content = f'Welcome to our service.\n' \
                   f'Your email confirmation token: {token}'
    msg = EmailMultiAlternatives(
        subject=f"Email confirmation for your account",
        body=text_content,
        from_email=settings.EMAIL_HOST_USER,
        to=[email]
    )
    msg.send()


@app.task
def on_account_deleted(email):
    """Отправляем письмо с подтверждением почты"""
    text_content = f'We are sorry You are leaving.\n' \
                   f'Thank You for being with us!'
    msg = EmailMultiAlternatives(
        subject=f"Your account has been deleted",
        body=text_content,
        from_email=settings.EMAIL_HOST_USER,
        to=[email]
    )
    msg.send()


@app.task
def on_reset_password_token_created(email, token):
    """Отправляем письмо с токеном для сброса пароля"""
    text_content = f'This is an important message.\n' \
                   f'Your password reset token: {token}'
    msg = EmailMultiAlternatives(
        subject=f"Password reset token for your account",
        body=text_content,
        from_email=settings.EMAIL_HOST_USER,
        to=[email]
    )
    msg.send()


@app.task
def on_post_password_reset(email):
    """Отправляем сообщение о сбросе пароля"""
    text_content = f'Thanks for using our service.\n' \
                   f'Your password has been successfully reset.'
    msg = EmailMultiAlternatives(
        subject=f"Password reset",
        body=text_content,
        from_email=settings.EMAIL_HOST_USER,
        to=[email]
    )
    if 'test' not in sys.argv:
        msg.send()
