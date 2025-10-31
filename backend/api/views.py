import logging

from django.core.exceptions import ValidationError
from payme.models import PaymeTransactions
from payme.types import response
from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError as DRFValidationError

from payme.views import PaymeWebHookAPIView

from .models import (
    User, Category, SubCategory, Service, ExecutorReview, Vacancy, ClientReview, Ad, OrderReview, Boost, ServiceBoost,
    VacancyBoost, Order, OTP_table
)

from .serializers import (
    UserSerializer, CategorySerializer, SubCategorySerializer, ServiceSerializer, ExecutorReviewSerializer,
    VacancySerializer, ClientReviewSerializer, AdSerializer, OrderReviewSerializer, BoostSerializer,
    ServiceBoostSerializer, VacancyBoostSerializer, RequestOTPSerializer, VerifyOTPSerializer, RegisterSerializer,
    LoginSerializer, ResetPasswordSerializer, OrderSerializer, PaymentSerializer
)

from .permissions import IsOwner

from .services.otp_service import OTPService
from .services.payme_service  import PaymeService, payme
from .services.user_service import UserService
from .services.vacancy_notification import notify_vacancy, notify_service

logger = logging.getLogger("app")

# --- ViewSets ---

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class SubCategoryViewSet(viewsets.ModelViewSet):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer


class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

    def perform_create(self, serializer):
        service = serializer.save()
        logger.info(f"Создан сервис {service.id} от пользователя {service.client}")
        notify_service(service)


class ExecutorReviewViewSet(viewsets.ModelViewSet):
    queryset = ExecutorReview.objects.all()
    serializer_class = ExecutorReviewSerializer


class VacancyViewSet(viewsets.ModelViewSet):
    queryset = Vacancy.objects.all()
    serializer_class = VacancySerializer

    def perform_create(self, serializer):
        vacancy = serializer.save()
        logger.info(f"Создана вакансия {vacancy.id} от пользователя {vacancy.client}")
        notify_vacancy(vacancy)


class ClientReviewViewSet(viewsets.ModelViewSet):
    queryset = ClientReview.objects.all()
    serializer_class = ClientReviewSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    # permission_classes = [IsAuthenticated, IsOrderOwner]

    def get_queryset(self):
        return Order.objects.filter(client=self.request.user)

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = PaymeTransactions.objects.all()
    serializer_class = PaymentSerializer


class AdViewSet(viewsets.ModelViewSet):
    queryset = Ad.objects.all()
    serializer_class = AdSerializer
    http_method_names = ['get']

class OrderReviewsView(viewsets.ModelViewSet):
    queryset = OrderReview.objects.all()
    serializer_class = OrderReviewSerializer


class BoostViewSet(viewsets.ModelViewSet):
    queryset = Boost.objects.all()
    serializer_class = BoostSerializer


class ServiceBoostViewSet(viewsets.ModelViewSet):
    queryset = ServiceBoost.objects.all()
    serializer_class = ServiceBoostSerializer

class VacancyBoostViewSet(viewsets.ModelViewSet):
    queryset = VacancyBoost.objects.all()
    serializer_class = VacancyBoostSerializer

# --- APIViews ---

class RequestOTPView(GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RequestOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data.get("phone")

        if not phone:
            logger.warning("RequestOTPView: Phone number is missing in request")
            return Response({
                "success": False,
                "message": "Введите номер телефона"
            })

        logger.info("RequestOTPView: OTP request for phone: %s", phone)

        try:
            otp_data = OTPService.create_otp(phone)

            logger.info("RequestOTPView: OTP created successfully for phone: %s", phone)
            return Response(otp_data, status=status.HTTP_200_OK)

        except ValidationError as e:
            detail = e.detail
            if isinstance(detail, dict):
                seconds_left = detail.get("seconds_left", 0)
                logger.warning(
                    "RequestOTPView: Too frequent OTP requests for phone: %s. Wait %d seconds",
                    phone, seconds_left
                )
                return Response({
                    "success": False,
                    "message": f"Подождите {seconds_left} секунд перед повторным запросом.",
                    "data": {"seconds_left": seconds_left}
                }, status=status.HTTP_200_OK)
            else:
                logger.warning("RequestOTPView: Validation error for phone %s: %s", phone, str(detail))
                return Response({
                    "success": False,
                    "message": str(detail)
                }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error("RequestOTPView: Error generating OTP for phone %s: %s", phone, str(e), exc_info=True)
            return Response({
                "success": False,
                "message": "Ошибка при генерации ссылки. Попробуйте позже.",
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetOTPBySessionView(GenericAPIView):
    permission_classes = [AllowAny]

    def get(self, request):
        session_id = request.query_params.get("session_id")
        if not session_id:
            return Response({
                "success": False,
                "message": "session_id обязателен"
            }, status=status.HTTP_400_BAD_REQUEST)

        otp = OTPService.get_otp_by_session_id(session_id)
        if not otp:
            return Response({
                "success": False,
                "message": "OTP не найден или истёк"
            }, status=status.HTTP_404_NOT_FOUND)

        return Response({
            "success": True,
            "data": {
                "code": otp.code,
                "expires_at": OTPService.format_expiration(otp.expires_at),
                "phone": str(otp.phone)
            }
        }, status=status.HTTP_200_OK)


class VerifyOTPView(GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data['phone']
        code = serializer.validated_data['code']

        logger.info("VerifyOTPView: OTP verification attempt for phone: %s", phone)

        success, message = OTPService.verify_otp(phone, code)

        if success:
            logger.info("VerifyOTPView: OTP verified successfully for phone: %s", phone)
            return Response({
                "success": True,
                "message": message
            }, status=status.HTTP_200_OK)
        else:
            logger.warning("VerifyOTPView: OTP verification failed for phone: %s. Reason: %s", phone, message)
            return Response({
                "success": False,
                "message": message
            }, status=status.HTTP_400_BAD_REQUEST)

class AttachTelegramView(GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request):
        session_id = request.data.get("session_id")
        telegram_id = request.data.get("telegram_id")
        telegram_username = request.data.get("telegram_username")

        if not session_id or not telegram_id:
            return Response({
                "success": False,
                "message": "session_id и telegram_id обязательны"
            }, status=status.HTTP_400_BAD_REQUEST)

        success, message = OTPService.attach_telegram_data(session_id, telegram_id, telegram_username)

        return Response({
            "success": success,
            "message": message
        }, status=status.HTTP_200_OK if success else status.HTTP_404_NOT_FOUND)


class RegisterView(APIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        phone = data["phone"]

        logger.info("RegisterView: Registration attempt for phone: %s", phone)

        try:
            user = UserService.register_user(
                phone=data["phone"],
                password=data["password"],
                name=data.get("name"),
                telegram_id=data.get("telegram_id"),
                telegram_username=data.get("telegram_username"),
                gender=data.get("gender"),
                region=data.get("region"),
                role=data.get("role", "client"),
            )

            logger.info(
                "RegisterView: User registered successfully. User ID: %s, Phone: %s",
                user.id,
                phone,
            )

            return Response({
                "success": True,
                "message": "Регистрация успешно завершена!",
                "user": {
                    "id": user.id,
                    "phone": str(user.phone),
                    "name": user.name,
                    "telegram_id": user.telegram_id,
                    "telegram_username": user.telegram_username,
                    "gender": user.gender,
                    "region": user.region,
                    "role": user.role,
                }
            }, status=status.HTTP_201_CREATED)

        except (ValidationError, DRFValidationError) as e:
            logger.warning("RegisterView: Validation error for phone %s: %s", phone, str(e))

            if hasattr(e, "detail"):
                if isinstance(e.detail, (list, tuple)):
                    message = e.detail[0]
                elif isinstance(e.detail, dict):
                    message = next(iter(e.detail.values()))[0]
                else:
                    message = e.detail
            else:
                message = str(e)

            return Response({
                "success": False,
                "message": str(message),
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(
                "RegisterView: Registration failed for phone %s: %s",
                phone,
                str(e),
                exc_info=True
            )
            return Response({
                "success": False,
                "message": "Ошибка при регистрации. Попробуйте позже."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LoginView(APIView):
    serializer_class = LoginSerializer
    # permission_classes = [AllowAny]
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data["phone"]
        password = serializer.validated_data["password"]

        tokens = UserService.login_user(phone, password)
        return Response(tokens, status=status.HTTP_200_OK)


class LogoutView(GenericAPIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        UserService.logout(refresh_token)
        return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)


class CheckAuthView(GenericAPIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "authenticated": True,
            "user": {
                "id": user.id,
                "phone": str(user.phone),
                "name": user.name,
                "role": user.role,
            }
        })


class PingView(APIView):
    # permission_classes = [AllowAny]
    def get(self, request):
        return Response({"status": "ok", "message": "pong"})


class CheckUserView(APIView):
    # permission_classes = [AllowAny]
    def post(self, request):
        phone = request.data.get("phone")

        try:
            exists = UserService.check_user_exists(phone)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {
                "exists": exists,
                "message": "Пользователь найден." if exists else "Пользователь не найден."
            },
            status=status.HTTP_200_OK
        )


class ProfileView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile_data = UserService.get_user_profile(request.user)
            return Response(profile_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    # permission_classes = [AllowAny]
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        result = UserService.reset_password(
            phone=data["phone"],
            otp_code=data["otp_code"],
            new_password=data["new_password"]
        )

        return Response(result, status=status.HTTP_200_OK)


class BoostPaymentCreateView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()

        result = {
            "order": serializer.data
        }

        payme_link = payme.initializer.generate_pay_link(
            id=serializer.data["id"],
            amount=serializer.data["price"],
            return_url="https://myprofy.uz/"
        )
        result["payme_link"] = payme_link

        return Response(result)


class PaymeCallBackAPIView(PaymeWebHookAPIView):
    permission_classes = [AllowAny]
    def check_perform_transaction(self, params):
        account = self.fetch_account(params)
        self.validate_amount(account, params.get('amount'))
        result = response.CheckPerformTransaction(allow=True)
        return result.as_resp()

    def handle_successfully_payment(self, params, result, *args, **kwargs):
        PaymeService.successfully_payment(params=params)

    def handle_cancelled_payment(self, params, result, *args, **kwargs):
        PaymeService.canceled_payment(params=params)

class ChatTableView(APIView):
    pass
