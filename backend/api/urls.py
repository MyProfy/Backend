from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, CategoryViewSet, SubCategoryViewSet, ServiceViewSet,
    ExecutorReviewViewSet, VacancyViewSet, ClientReviewViewSet, OrderViewSet,
    PaymentViewSet, AdViewSet, OrderReviewsView, BoostViewSet, ServiceBoostViewSet, VacancyBoostViewSet
)
from django.urls import path, include
from .views import (
    RequestOTPView, VerifyOTPView, RegisterView, LoginView, logout,
    check_auth, ping, CheckUserView, profile, ChatTableView,
    ResetPasswordView, BoostPaymentCreateView, PaymeCallBackAPIView,
    click_webhook, uzum_webhook
)

router = DefaultRouter()
# router.register(r'users', UserViewSet, basename='users')
# router.register(r'categories', CategoryViewSet, basename='categories')
# router.register(r'subcategories', SubCategoryViewSet, basename='subcategories')
# router.register(r'services', ServiceViewSet, basename='services')
# router.register(r'executor-reviews', ExecutorReviewViewSet, basename='executor-reviews')
# router.register(r'vacancies', VacancyViewSet, basename='vacancies')
# router.register(r'client-reviews', ClientReviewViewSet, basename='client-reviews')
# router.register(r'orders', OrderViewSet, basename='orders')
# router.register(r'payments', PaymentViewSet, basename='payments')
# router.register(r'ads', AdViewSet, basename='ads')
# router.register(r'order-reviews', OrderReviewsView, basename='order-reviews')
# router.register(r'boosts', BoostViewSet, basename='boosts')
# router.register(r'service-boosts', ServiceBoostViewSet, basename='service-boosts')
# router.register(r'vacancy-boosts', VacancyBoostViewSet, basename='vacancy-boosts')

urlpatterns = [
    path('', include(router.urls)),

    path('otp/request/', RequestOTPView.as_view(), name='request-otp'),
    path('otp/verify/', VerifyOTPView.as_view(), name='verify-otp'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', logout, name='logout'),
    path('check-auth/', check_auth, name='check-auth'),
    path('ping/', ping, name='ping'),
    path('check-user/', CheckUserView.as_view(), name='check-user'),
    path('profile/', profile, name='profile'),
    path('chat-table/', ChatTableView.as_view(), name='chat-table'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('boost-payment-create/', BoostPaymentCreateView.as_view(), name='boost-payment-create'),
    path('payme/callback/', PaymeCallBackAPIView.as_view(), name='payme-callback'),
    path('click/webhook/', click_webhook, name='click-webhook'),
    path('uzum/webhook/', uzum_webhook, name='uzum-webhook'),
]
