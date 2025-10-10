from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    User, Category, SubCategory, Service, ExecutorReview, Vacancy, ClientReview, Ad, OrderReview, Boost, ServiceBoost,
    VacancyBoost
)

from .serializers import (
    UserSerializer, CategorySerializer, SubCategorySerializer, ServiceSerializer, ExecutorReviewSerializer,
    VacancySerializer, ClientReviewSerializer, AdSerializer, OrderReviewSerializer, BoostSerializer,
    ServiceBoostSerializer, VacancyBoostSerializer
)

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
    queryset = None
    pass


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = None
    pass


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
    pass


class VerifyOTPView(APIView):
    pass


class RegisterView(APIView):
    pass


class LoginView(APIView):
    pass


class LogoutView(APIView):
    pass


class CheckAuthView(APIView):
    pass


class PingView(APIView):
    pass


class CheckUserView(APIView):
    pass


class ProfileView(APIView):
    pass


class ResetPasswordView(APIView):
    pass


class BoostPaymentCreateView(APIView):
    pass


class PaymeCallBackAPIView(APIView):
    pass


class ClickWebhook(APIView):
    pass


class UzumWebhook(APIView):
    pass


class ChatTableView(APIView):
    pass

# -- Functions --

def logout(request):
    return Response({"message": "logout placeholder"})


def check_auth(request):
    return Response({"message": "check_auth placeholder"})


def ping(request):
    return Response({"message": "pong"})


def profile(request):
    return Response({"message": "profile placeholder"})

def click_webhook(request):
    return Response({"message": "click_webhook placeholder"})

def uzum_webhook(request):
    return Response({"message": "uzum_webhook placeholder"})