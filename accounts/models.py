from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    UserManager
)
from django.db import models
from django.core.mail import send_mail


# Create your models here.
class CustomUserManager(UserManager):
    """ カスタムユーザーマネージャー """
    def _create_user(self, email, password, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.username = email
        user.set_password(password)
        user.save(using=self._db)
        return user


class Organization(models.Model):
    """ 組織モデル """

    # ステータス定義
    STATUS_ACTIVE = 0
    STATUS_INACTIVE = 1
    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'アクティブ'),
        (STATUS_INACTIVE, '非アクティブ'),
    ]

    name = models.CharField(max_length=256, verbose_name='組織名')
    rep_user = models.IntegerField(null=True, verbose_name='担当者ID')
    email = models.EmailField(unique=True, verbose_name='お知らせの送信先メアド')
    address = models.CharField(max_length=512, verbose_name='組織住所')
    tel = models.CharField(max_length=32, verbose_name='代表電話番号')
    status = models.IntegerField(choices=STATUS_CHOICES, verbose_name='ステータス')


class User(AbstractBaseUser, PermissionsMixin):
    """ ユーザーモデル """
    ROLE_GENERAL = 0
    ROLE_ORG_ADMIN = 1
    ROLE_SYS_ADMIN_GEN = 50
    ROLE_CHOICES = [
        (ROLE_GENERAL, '一般ユーザー'),
        (ROLE_ORG_ADMIN, '組織管理者'),
        (ROLE_SYS_ADMIN_GEN, 'システム管理者（一般）'),
    ]

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=256, verbose_name='名')
    last_name = models.CharField(max_length=256, verbose_name='姓')
    icon = models.CharField(
        max_length=512, blank=True, null=True, verbose_name='アイコン画像のパス')
    organization_id = models.ForeignKey(Organization, on_delete=models.CASCADE)
    role = models.IntegerField(choices=ROLE_CHOICES, verbose_name='権限')
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='登録日')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='最終更新日')

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'

    objects = CustomUserManager()

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def email_user(self, subject, message, from_email=None, **kwargs):
        """ ユーザー宛にメールを送信する

        Args:
            subject (string): 件名
            message (string): 本文
            from_email (string, optional): Fromメアド. Defaults to None.
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def __str__(self):
        return self.email

    def get_full_name(self):
        """ ユーザーのフルネームを返す

        Returns:
            string: フルネーム
        """
        return f"{self.last_name} {self.first_name}"
