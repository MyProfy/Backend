import random
import uuid

from datetime import timedelta
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from api.models import OTP_table
from django.utils.formats import date_format

from config import settings

class OTPService:
    RESEND_TIMEOUT = 60
    OTP_LIFETIME = 120

    @staticmethod
    def generate_code(length=4) -> str:
        """6-digit code generation"""
        return ''.join(random.choices('0123456789', k=length))

    @staticmethod
    def create_otp(phone):
        now = timezone.now()
        resend_limit = now - timedelta(seconds=OTPService.RESEND_TIMEOUT)
        session_id = str(uuid.uuid4())

        recent_otp = OTP_table.objects.filter(phone=phone, created_at__gt=resend_limit).first()
        if recent_otp:
            seconds_left = OTPService.RESEND_TIMEOUT - int((now - recent_otp.created_at).total_seconds())
            raise ValidationError({
                "error": "OTP already sent recently. Please wait before requesting again.",
                "seconds_left": max(seconds_left, 0)
            })

        code = OTPService.generate_code()
        expires_at = now + timedelta(seconds=OTPService.OTP_LIFETIME)

        otp = OTP_table.objects.create(
            phone=phone,
            code=code,
            expires_at=expires_at,
            session_id=session_id
        )

        local_time = timezone.localtime(expires_at)
        formatted_time = date_format(local_time, format="d.m.Y H:i", use_l10n=True)

        return {
            "success": True,
            "message": "Ссылка для подтверждения отправлена",
            "data": {
                "expires_at": formatted_time,
                "link": f"https://t.me/{settings.BOT_NAME}?start={session_id}"
            }
        }

    @staticmethod
    def get_otp_by_session_id(session_id: str):
        otp = OTP_table.objects.filter(session_id=session_id).first()
        if not otp or timezone.now() > otp.expires_at:
            return None
        return otp

    @staticmethod
    def verify_otp(phone, code):
        """Checks the validity of the OTP and deletes it if verified"""
        otp = OTP_table.objects.filter(phone=phone, code=code).last()

        if not otp:
            return False, "Invalid code"

        if timezone.now() > otp.expires_at:
            otp.delete()
            return False, "Code expired"

        otp.delete()

        return True, "Code verified"
