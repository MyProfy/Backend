from rest_framework import serializers

from payme.models import PaymeTransactions
from phonenumber_field.serializerfields import PhoneNumberField
from .models import (
    User, Category, SubCategory, Service, ExecutorReview, Vacancy, ClientReview, Ad, OrderReview, Boost, ServiceBoost,
    VacancyBoost, Order
)

class UserSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%d.%m.%Y %H:%M", read_only=True)
    class Meta:
        model = User
        fields = [
            'id', 'name', 'phone', 'about_user', 'role', 'region',
            'executor_rating', 'work_experience', 'email',  'client_rating', 'telegram_username',
            'telegram_id', 'gender', 'avatar', 'birthday', 'lang', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'executor_rating', 'client_rating']

class CategorySerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%d.%m.%Y %H:%M", read_only=True)

    class Meta:
        model = Category
        fields = [
            'id',
            'title',
            'display_ru',
            'display_uz',
            'service_count',
            'created_at',
        ]
        read_only_fields = ['id', 'service_count', 'created_at']

class SubCategorySerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%d.%m.%Y %H:%M", read_only=True)
    category_name = serializers.CharField(source='category.title', read_only=True)

    class Meta:
        model = SubCategory
        fields = [
            'id',
            'category',
            'category_name',
            'title',
            'display_ru',
            'display_uz',
            'created_at',
        ]
        read_only_fields = ['id', 'category_name', 'service_count', 'created_at']

class ServiceSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%d.%m.%Y %H:%M", read_only=True)
    category_name = serializers.CharField(source='category.title', read_only=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False, read_only=True)
    sub_categories_names = serializers.SlugRelatedField(
        source='sub_categories',
        many=True,
        read_only=True,
        slug_field='title'
    )
    executor_name = serializers.CharField(source='executor.phone', read_only=True)
    boost_name = serializers.CharField(source='boost.name', read_only=True, default=None)

    class Meta:
        model = Service
        fields = [
            'id',
            'executor',
            'executor_name',
            'category',
            'category_name',
            'sub_categories',
            'sub_categories_names',
            'title',
            'description',
            'price',
            'moderation',
            'boost',
            'boost_name',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'executor_name',
            'category_name',
            'sub_categories_names',
            'boost_name',
            'created_at',
        ]

class ExecutorReviewSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%d.%m.%Y %H:%M", read_only=True)
    class Meta:
        model = ExecutorReview
        fields = '__all__'
        read_only_fields = ('created_at',)

class VacancySerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False)
    moderation_display = serializers.CharField(source='get_moderation_display', read_only=True)

    class Meta:
        model = Vacancy
        fields = [
            'id', 'title', 'description', 'price', 'category', 'sub_category',
            'client', 'images', 'moderation', 'moderation_display', 'boost'
        ]
        read_only_fields = ['id', 'moderation_display']

class ClientReviewSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%d.%m.%Y %H:%M", read_only=True)

    class Meta:
        model = ClientReview
        fields = [
            'id',
            'order',
            'executor',
            'client',
            'rating',
            'review',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

class AdSerializer(serializers.ModelSerializer):
    start_date = serializers.DateTimeField(format="%d.%m.%Y %H:%M", read_only=True)
    end_date = serializers.DateTimeField(format="%d.%m.%Y %H:%M", read_only=True)

    class Meta:
        model = Ad
        fields = [
            'id',
            'image',
            'start_date',
            'end_date',
            'region',
            'link',
        ]
        read_only_fields = ['id', 'start_date', 'end_date']

class OrderReviewSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%d.%m.%Y %H:%M", read_only=True)
    class Meta:
        model = OrderReview
        fields = '__all__'
        read_only_fields = ['created_at']

class BoostSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False)
    final_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
        coerce_to_string=False
    )

    class Meta:
        model = Boost
        fields = [
            'id',
            'name',
            'boost_type',
            'duration_days',
            'price',
            'discount',
            'final_price',
            'applies_to',
        ]

class ServiceBoostSerializer(serializers.ModelSerializer):
    boost = BoostSerializer()
    start_date = serializers.DateTimeField(format="%d.%m.%Y %H:%M", read_only=True)
    end_date = serializers.DateTimeField(format="%d.%m.%Y %H:%M", read_only=True)

    class Meta:
        model = ServiceBoost
        fields = ['id', 'service', 'boost', 'start_date', 'end_date', 'is_active']

class VacancyBoostSerializer(serializers.ModelSerializer):
    boost = BoostSerializer()
    start_date = serializers.DateTimeField(format="%d.%m.%Y %H:%M", read_only=True)
    end_date = serializers.DateTimeField(format="%d.%m.%Y %H:%M", read_only=True)

    class Meta:
        model = VacancyBoost
        fields = ['id', 'vacancy', 'boost', 'start_date', 'end_date', 'is_active']

class RequestOTPSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)

class VerifyOTPSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    code = serializers.CharField(max_length=6)

class RegisterSerializer(serializers.Serializer):
    phone = PhoneNumberField()
    password = serializers.CharField(write_only=True)
    name = serializers.CharField(required=False, allow_blank=True)
    role = serializers.ChoiceField(choices=[('client', 'Client'), ('executor', 'Executor')], default='client')

    def validate_phone(self, value):
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("Пользователь с таким номером уже зарегистрирован.")
        return value

class LoginSerializer(serializers.Serializer):
    phone = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)

class ResetPasswordSerializer(serializers.Serializer):
    phone = serializers.CharField()
    otp_code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(min_length=6)

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymeTransactions
        fields = "__all__"
        read_only_fields = ["performed_at", "cancelled_at"]