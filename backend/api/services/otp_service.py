import random
from datetime import timedelta
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from api.models import OTP_table

class OTPService:
    RESEND_TIMEOUT = 60
    OTP_LIFETIME = 120

    @staticmethod
    def generate_code(length=6) -> str:
        """6-digit code generation"""
        return ''.join(random.choices('0123456789', k=length))

    @staticmethod
    def create_otp(phone):
        """Creates an OTP entry for your phone."""
        now = timezone.now()
        resend_limit = now - timedelta(seconds=OTPService.RESEND_TIMEOUT)

        recent_otp = OTP_table.objects.filter(phone=phone, created_at__gt=resend_limit).first()
        if recent_otp:
            seconds_left = int((recent_otp.expires_at - now).total_seconds())
            raise ValidationError({
                "error": "OTP already sent recently. Please wait before requesting again.",
                "seconds_left": seconds_left
            })

        code = OTPService.generate_code()
        expires_at = now + timedelta(seconds=OTPService.OTP_LIFETIME)

        otp = OTP_table.objects.create(
            phone=phone,
            code=code,
            expires_at=expires_at
        )

        # TODO
        # send_sms(phone, f"Your OTP code is {code}")

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
