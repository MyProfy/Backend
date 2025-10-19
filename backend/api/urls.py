from rest_framework.routers import DefaultRouter
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserViewSet, CategoryViewSet, SubCategoryViewSet, ServiceViewSet,
    ExecutorReviewViewSet, VacancyViewSet, ClientReviewViewSet, OrderViewSet,
    PaymentViewSet, AdViewSet, OrderReviewsView, BoostViewSet,
    ServiceBoostViewSet, VacancyBoostViewSet,
    RequestOTPView, VerifyOTPView, RegisterView, LoginView, LogoutView, CheckAuthView, BoostPaymentCreateView,
    GetOTPBySessionView,
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'subcategories', SubCategoryViewSet, basename='subcategories')
router.register(r'services', ServiceViewSet, basename='services')
router.register(r'executor-reviews', ExecutorReviewViewSet, basename='executor-reviews')
router.register(r'vacancies', VacancyViewSet, basename='vacancies')
router.register(r'client-reviews', ClientReviewViewSet, basename='client-reviews')
router.register(r'orders', OrderViewSet, basename='orders')
router.register(r'payments', PaymentViewSet, basename='payments')
router.register(r'ads', AdViewSet, basename='ads')
router.register(r'order-reviews', OrderReviewsView, basename='order-reviews')
router.register(r'boosts', BoostViewSet, basename='boosts')
router.register(r'service-boosts', ServiceBoostViewSet, basename='service-boosts')
router.register(r'vacancy-boosts', VacancyBoostViewSet, basename='vacancy-boosts')

urlpatterns = [
    path('', include(router.urls)),

    # Payme
    path('order/create/', BoostPaymentCreateView.as_view()),

    # OTP
    path('auth/otp/request/', RequestOTPView.as_view(), name='request-otp'),
    path('auth/otp/verify/', VerifyOTPView.as_view(), name='verify-otp'),
    path("auth/otp/session/", GetOTPBySessionView.as_view(), name="otp-by-session"),

    # Auth
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/check/', CheckAuthView.as_view(), name='check-auth'),
]
