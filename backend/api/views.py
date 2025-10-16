from payme.models import PaymeTransactions
from payme.types import response
from rest_framework import viewsets
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from payme.views import PaymeWebHookAPIView

from .models import (
    User, Category, SubCategory, Service, ExecutorReview, Vacancy, ClientReview, Ad, OrderReview, Boost, ServiceBoost,
    VacancyBoost, Order
)

from .serializers import (
    UserSerializer, CategorySerializer, SubCategorySerializer, ServiceSerializer, ExecutorReviewSerializer,
    VacancySerializer, ClientReviewSerializer, AdSerializer, OrderReviewSerializer, BoostSerializer,
    ServiceBoostSerializer, VacancyBoostSerializer, RequestOTPSerializer, VerifyOTPSerializer, RegisterSerializer,
    LoginSerializer, ResetPasswordSerializer, OrderSerializer, PaymentSerializer
)

from .permissions import IsOrderOwner

from .services.otp_service import OTPService
from .services.payme_service  import PaymeService, payme
from .services.user_service import UserService

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


class ExecutorReviewViewSet(viewsets.ModelViewSet):
    queryset = ExecutorReview.objects.all()
    serializer_class = ExecutorReviewSerializer


class VacancyViewSet(viewsets.ModelViewSet):
    queryset = Vacancy.objects.all()
    serializer_class = VacancySerializer


class ClientReviewViewSet(viewsets.ModelViewSet):
    queryset = ClientReview.objects.all()
    serializer_class = ClientReviewSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsOrderOwner]

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

class RequestOTPView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = RequestOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data.get("phone")

        if not phone:
            return Response({
                "success": False,
                "message": "Пожалуйста, укажите номер телефона."
            })

        try:
            otp = OTPService.create_otp(phone)
            return Response({
                "success": True,
                "message": "Код подтверждения отправлен успешно",
                "data": {
                    "expires_at": otp.expires_at,
                    "code": otp.code,
                }
            }, status=status.HTTP_200_OK)

        except ValidationError as e:
            detail = e.detail
            if isinstance(detail, dict):
                message = str(detail.get("error", "Не удалось отправить код."))
                seconds_left = detail.get("seconds_left", 0)
                return Response({
                    "success": False,
                    "message": f"Подождите {seconds_left} сек, прежде чем запросить новый код.",
                    "data": {"seconds_left": seconds_left}
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "success": False,
                    "message": str(detail)
                }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "success": False,
                "message": "Произошла ошибка при отправке кода. Попробуйте позже."
            }, status=status.HTTP_200_OK)

class VerifyOTPView(APIView):
    permission_classes =  [AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data['phone']
        code = serializer.validated_data['code']

        success, message = OTPService.verify_otp(phone, code)

        if success:
            return Response({
                "success": True,
                "message": message
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "success": False,
                "message": message
            }, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(APIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        user = UserService.register_user(
            phone=data["phone"],
            password=data["password"],
            name=data.get("name"),
            telegram_id=data.get("telegram_id", None),
            telegram_username=data.get("telegram_username", None),
            role=data.get("role", "client")
        )

        return Response({
            "message": "Регистрация успешно завершена!",
            "user": {
                "id": user.id,
                "phone": str(user.phone),
                "name": user.name,
                "telegram_id": user.telegram_id,
                "telegram_username": user.telegram_username,
                "role": user.role,
            }
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data["phone"]
        password = serializer.validated_data["password"]

        tokens = UserService.login_user(phone, password)
        return Response(tokens, status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        UserService.logout(refresh_token)
        return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)


class CheckAuthView(APIView):
    permission_classes = [IsAuthenticated]

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
    permission_classes = [AllowAny]
    def get(self, request):
        return Response({"status": "ok", "message": "pong"})


class CheckUserView(APIView):
    permission_classes = [AllowAny]
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
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile_data = UserService.get_user_profile(request.user)
            return Response(profile_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]
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
