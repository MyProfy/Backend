from django.utils import timezone
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed, NotFound
from rest_framework.exceptions import ValidationError
from api.models import OTP_table, User


class UserService:

    @staticmethod
    def register_user(phone: str, password: str, **kwargs):
        otp = OTP_table.objects.filter(phone=phone).order_by('-created_at').first()
        if User.objects.filter(phone=phone).exists():
            raise ValidationError("Пользователь с таким номером уже зарегистрирован.")

        kwargs.pop("telegram_id", None)
        kwargs.pop("telegram_username", None)

        user = User.objects.create_user(
            phone=phone,
            password=password,
            telegram_id=otp.telegram_id,
            telegram_username=otp.telegram_username,
            **kwargs
        )

        otp.delete()
        return user

    @staticmethod
    def login_user(phone: str, password: str):
        """Authenticate user and return JWT tokens."""
        user = authenticate(phone=phone, password=password)

        if user is None:
            raise AuthenticationFailed("Неверный номер телефона или пароль.")

        refresh = RefreshToken.for_user(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "phone": str(user.phone),
                "name": user.name,
                "role": user.role,
            },
        }

    @staticmethod
    def logout(refresh_token_str: str):
        if not refresh_token_str:
            raise ValidationError("Refresh token is required.")

        try:
            token = RefreshToken(refresh_token_str)
            token.blacklist()
        except Exception:
            raise ValidationError("Invalid or expired token.")

    @staticmethod
    def check_user_exists(phone: str) -> bool:
        """Check if user exists by phone."""
        if not phone:
            raise ValidationError("Поле 'phone' обязательно.")
        return User.objects.filter(phone=phone).exists()

    @staticmethod
    def get_user_profile(user):
        """Return profile user"""
        if not user or not user.is_authenticated:
            raise ValidationError("Пользователь не авторизован.")

        try:
            return {
                "id": user.id,
                "name": user.name,
                "phone": str(user.phone),
                "email": user.email,
                "role": user.role,
                "about_user": user.about_user,
                "region": user.region,
                "created_at": user.created_at,
                "executor_rating": user.executor_rating,
                "client_rating": user.client_rating,
                "avatar": user.avatar.url if user.avatar else None,
                "telegram_username": user.telegram_username,
                "lang": user.lang,
            }
        except Exception:
            raise NotFound("Профиль пользователя не найден.")

    @staticmethod
    def reset_password(phone: str, otp_code: str, new_password: str):
        """Reset password with OTP code"""
        otp = OTP_table.objects.filter(phone=phone, code=otp_code).last()
        if not otp:
            raise ValidationError("Неверный код подтверждения.")
        if timezone.now() > otp.expires_at:
            raise ValidationError("Срок действия кода истёк.")

        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            raise ValidationError("Пользователь с таким номером не найден.")

        user.set_password(new_password)
        user.save()

        # Delete OTP
        otp.delete()

        return {"message": "Пароль успешно обновлён."}