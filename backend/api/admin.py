from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db import models
from django.utils.html import format_html
from django.utils import timezone
from django.db.models import Case, When, Value, IntegerField
from django.http import HttpResponse
from import_export import resources
from import_export.formats import base_formats
from unfold.contrib.forms.widgets import WysiwygWidget

from .models import User, Category, SubCategory, Service, ServiceImage, ExecutorReview, Vacancy, VacancyImage, \
    ClientReview, BoostPayment, Order, OTP_table, Chat_table, ChatRoom, Message, Ad, Boost, ServiceBoost, VacancyBoost, \
    OrderReview
import logging

from .forms import CustomUserCreationForm

from unfold.admin import ModelAdmin
from unfold.admin import TabularInline, StackedInline

# Set up logging
logger = logging.getLogger(__name__)


# Custom filter for User by phone number
class PhoneFilter(SimpleListFilter):
    title = 'Phone Number'
    parameter_name = 'phone'

    def lookups(self, request, model_admin):
        return [(str(user.phone), str(user.phone)) for user in User.objects.all().distinct()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(phone__icontains=self.value())
        return queryset


# Custom filter for Category by name
class CategoryNameFilter(SimpleListFilter):
    title = 'Category Name'
    parameter_name = 'name'

    def lookups(self, request, model_admin):
        return [(category.title, category.title) for category in Category.objects.all().distinct()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(name=self.value())
        return queryset


# Custom filter for Service by name
class ServiceNameFilter(SimpleListFilter):
    title = 'Service Name'
    parameter_name = 'name'

    def lookups(self, request, model_admin):
        return [(service.title, service.title) for service in Service.objects.all().distinct()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(name=self.value())
        return queryset


# Custom filter for Vacancy by name
class VacancyNameFilter(SimpleListFilter):
    title = 'Vacancy Name'
    parameter_name = 'name'

    def lookups(self, request, model_admin):
        return [(vacancy.title, vacancy.title) for vacancy in Vacancy.objects.all().distinct()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(name=self.value())
        return queryset


# Custom filter for Chat_table by phone
class ChatPhoneFilter(SimpleListFilter):
    title = 'Phone Number'
    parameter_name = 'phone'

    def lookups(self, request, model_admin):
        return [(chat.phone, chat.phone) for chat in Chat_table.objects.all().distinct()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(phone=self.value())
        return queryset


# Custom filter for Payment by status
class PaymentStatusFilter(SimpleListFilter):
    title = 'Payment Status'
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return [('Pending', 'Pending'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled')]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status=self.value())
        return queryset


# Custom filter for Rating
class RatingFilter(SimpleListFilter):
    title = 'Rating'
    parameter_name = 'rating'

    def lookups(self, request, model_admin):
        return [(str(i), f"{i} stars") for i in range(1, 6)]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(rating=float(self.value()))
        return queryset


# Inline for SubCategory in Category
class SubCategoryInline(TabularInline):
    model = SubCategory
    extra = 1
    fields = ('title',)


# Inline for Order in Service
class OrderServiceInline(TabularInline):
    model = Order
    extra = 1
    fields = ('client', 'executor', 'price', 'status', 'date_execution')
    readonly_fields = ('date_order',)
    fk_name = 'service'
    can_delete = True


# Inline for Order in Vacancy
class OrderVacancyInline(TabularInline):
    model = Order
    extra = 1
    fields = ('client', 'executor', 'price', 'status', 'date_execution')
    readonly_fields = ('date_order',)
    fk_name = 'vacancy'
    can_delete = True


# Inline for Message in ChatRoom
class MessageInline(TabularInline):
    model = Message
    extra = 1
    fields = ('sender', 'content', 'file', 'timestamp')
    readonly_fields = ('timestamp',)
    can_delete = True


# Model-specific field definitions for export
MODEL_EXPORT_FIELDS = {
    'User': ['id', 'name', 'phone', 'email', 'role', 'region', 'executor_rating', 'client_rating', 'orders_count', 'created_at'],
    'Category': ['id', 'title', 'display_ru', 'display_uz'],
    'SubCategory': ['id', 'title', 'display_ru', 'display_uz', 'category'],
    'Service': ['id', 'title', 'category', 'price', 'executor', 'moderation'],
    'ServiceImage': ['id', 'service', 'uploaded_at'],
    'Vacancy': ['id', 'title', 'category', 'price', 'client', 'moderation'],
    'VacancyImage': ['id', 'vacancy', 'uploaded_at'],
    'Order': ['id', 'service', 'vacancy', 'client', 'executor', 'date_order', 'status', 'price'],
    'OTP_table': ['phone', 'code', 'created_at', 'expires_at'],
    'Chat_table': ['phone', 'chat_id'],
    'Payment': ['id', 'order', 'client', 'executor', 'date_order', 'status', 'amount', 'price'],
    'ChatRoom': ['name', 'user1', 'user2', 'created_at'],
    'Message': ['room', 'sender', 'content', 'timestamp'],
    'Ad': ['id', 'start_date', 'end_date', 'region', 'link'],
    'ExecutorReview': ['id', 'order', 'executor', 'client', 'rating', 'review', 'created_at'],
    'ClientReview': ['id', 'order', 'executor', 'client', 'rating', 'review', 'created_at'],
    'BoostPayment': ['id', 'boost_payment_id', 'service', 'vacancy', 'boost', 'amount', 'status', 'created_at'],
    'Boost': ['id', 'name', 'boost_type', 'duration_days', 'price', 'discount', 'applies_to'],
    'ServiceBoost': ['id', 'service', 'boost', 'start_date', 'end_date', 'is_active'],
    'VacancyBoost': ['id', 'vacancy', 'boost', 'start_date', 'end_date', 'is_active'],
}


# Generic function to export to Excel
def export_to_excel(modeladmin, request, queryset, fields=None):
    model = modeladmin.model
    model_name = model.__name__
    fields = MODEL_EXPORT_FIELDS.get(model_name, fields or '__all__')
    logger.debug(f"Exporting {model_name} with {queryset.count()} records")

    if not queryset.exists():
        logger.warning(f"No records found for {model_name} export")
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={'Content-Disposition': f'attachment; filename="{model_name}.xlsx"'}
        )
        response.write("No data available to export")
        return response

    resource_class = type(f'{model_name}Resource', (resources.ModelResource,), {
        'Meta': type('Meta', (), {
            'model': model,
            'fields': fields,
            'exclude': getattr(modeladmin, 'export_exclude', []),
        })
    })
    resource = resource_class()
    dataset = resource.export(queryset)

    if not dataset.dict:
        logger.warning(f"Dataset for {model_name} is empty after export")

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': f'attachment; filename="{model_name}.xlsx"'}
    )
    xlsx_format = base_formats.XLSX()
    response.write(xlsx_format.export_data(dataset))
    return response


# Custom admin for User
@admin.register(User)
class UserAdmin(ModelAdmin, BaseUserAdmin):
    add_form = CustomUserCreationForm
    model = User
    ordering = ('-created_at',)

    list_display = (
        'id', 'name', 'phone', 'email', 'role', 'region',
        'executor_rating', 'client_rating', 'avatar_preview',
        'created_at', 'orders_count', 'created_by_display'
    )
    readonly_fields = ('created_by_display',)
    list_filter = (PhoneFilter, 'role', 'region', 'gender')
    search_fields = ('name', 'phone', 'email', 'telegram_username')

    fieldsets = (
        (None, {
            'fields': ('phone', 'password')
        }),
        ('Personal Info', {
            'fields': (
                'name', 'email', 'telegram_username',
                'gender', 'region', 'about_user', 'avatar'
            )
        }),
        ('Professional Info', {
            'fields': (
                'role', 'work_experience',
                'executor_rating', 'client_rating', 'orders_count'
            )
        }),
        ('Permissions', {
            'fields': (
                'is_staff', 'is_superuser',
                'groups', 'user_permissions'
            )
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'phone', 'password1', 'password2', 'name', 'email',
                'role', 'region', 'gender', 'telegram_username', 'avatar',
                'is_staff', 'is_superuser',
                'groups', 'user_permissions'
            ),
        }),
    )

    actions = [export_to_excel]
    export_exclude = ['password', 'avatar'] # Exclude sensitive fields from export

    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.avatar.url)
        return "No Avatar"

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    avatar_preview.short_description = 'Avatar'

    export_to_excel.short_description = "Export selected to Excel"


# Custom admin for Category
@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ('id', 'title', 'display_ru', 'display_uz', 'service_count')
    list_filter = (CategoryNameFilter,)
    search_fields = ('title', 'display_ru', 'display_uz')
    inlines = [SubCategoryInline]
    fieldsets = (
        (None, {
            'fields': ('title', 'display_ru', 'display_uz')
        }),
    )
    actions = [export_to_excel]

    def service_count(self, obj):
        return obj.services.count()

    service_count.short_description = 'Services'

    export_to_excel.short_description = "Export selected to Excel"


# Custom admin for SubCategory
@admin.register(SubCategory)
class SubCategoryAdmin(ModelAdmin):
    list_display = ('id', 'title', 'display_ru', 'display_uz', 'category')
    list_filter = ('category',)
    search_fields = ('title', 'display_ru', 'display_uz')
    fieldsets = (
        (None, {
            'fields': ('title', 'display_ru', 'display_uz', 'category')
        }),
    )
    actions = [export_to_excel]

    export_to_excel.short_description = "Export selected to Excel"


# Custom admin for Service
@admin.register(Service)
class ServiceAdmin(ModelAdmin):
    list_display = (
    'id', 'title', 'category', 'price', 'executor', 'get_first_image', 'boost_priority_display', 'moderation')
    list_filter = (ServiceNameFilter, 'category', 'executor', 'moderation')
    search_fields = ('title', 'description')
    inlines = [OrderServiceInline]
    list_editable = ('moderation',)
    filter_horizontal = ('sub_categories',)
    filter_vertical = ('sub_categories',)
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'category', 'sub_categories', 'price', 'executor', 'moderation')
        }),
    )
    actions = [export_to_excel]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        current_time = timezone.now()
        return queryset.annotate(
            boost_priority=Case(
                When(
                    boost__boost_type='Turbo',
                    boosts__is_active=True,
                    boosts__end_date__gt=current_time,
                    then=Value(2)
                ),
                When(
                    boost__boost_type='Top',
                    boosts__is_active=True,
                    boosts__end_date__gt=current_time,
                    then=Value(1)
                ),
                default=Value(0),
                output_field=IntegerField()
            )
        ).order_by('-boost_priority')

    def boost_priority_display(self, obj):
        priority = obj.boost_priority
        return "Turbo (2)" if priority == 2 else "Top (1)" if priority == 1 else "None (0)"

    boost_priority_display.short_description = 'Boost Priority'

    def get_first_image(self, obj):
        first_image_obj = obj.images.first()  # RelatedManager → первый объект
        if first_image_obj and first_image_obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover;" />',
                first_image_obj.image.url
            )
        return "No Image"

    get_first_image.short_description = 'Image'

    export_to_excel.short_description = "Export selected to Excel"


# Custom admin for ServiceImage
@admin.register(ServiceImage)
class ServiceImageAdmin(ModelAdmin):
    list_display = ('id', 'service', 'image_preview', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('service__name',)
    fieldsets = (
        (None, {
            'fields': ('service', 'image')
        }),
    )
    readonly_fields = ('uploaded_at',)
    actions = [export_to_excel]
    export_exclude = ['image']  # Exclude image field from export

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image.url)
        return "No Image"

    image_preview.short_description = 'Image Preview'

    export_to_excel.short_description = "Export selected to Excel"


# Custom admin for Vacancy
@admin.register(Vacancy)
class VacancyAdmin(ModelAdmin):
    list_display = (
    'id', 'title', 'category', 'price', 'client', 'get_first_image', 'boost_priority_display', 'moderation')
    list_filter = (VacancyNameFilter, 'category', 'client', 'moderation')
    search_fields = ('title', 'description')
    inlines = [OrderVacancyInline]
    list_editable = ('moderation',)

    formfield_overrides = {
        models.TextField: {
            "widget": WysiwygWidget,
        }
    }

    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'category', 'sub_category', 'price', 'client', 'moderation')
        }),
    )
    actions = [export_to_excel]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        current_time = timezone.now()
        return queryset.annotate(
            boost_priority=Case(
                When(
                    boost__boost_type='Turbo',
                    boosts__is_active=True,
                    boosts__end_date__gt=current_time,
                    then=Value(2)
                ),
                When(
                    boost__boost_type='Top',
                    boosts__is_active=True,
                    boosts__end_date__gt=current_time,
                    then=Value(1)
                ),
                default=Value(0),
                output_field=IntegerField()
            )
        ).order_by('-boost_priority')

    def boost_priority_display(self, obj):
        priority = obj.boost_priority
        return "Turbo (2)" if priority == 2 else "Top (1)" if priority == 1 else "None (0)"

    boost_priority_display.short_description = 'Boost Priority'

    def get_first_image(self, obj):
        first_image = obj.images.url if obj.images else None
        if first_image and first_image.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />',
                               first_image.image.url)
        return "No Image"

    get_first_image.short_description = 'Image'

    export_to_excel.short_description = "Export selected to Excel"


# Custom admin for VacancyImage
@admin.register(VacancyImage)
class VacancyImageAdmin(ModelAdmin):
    list_display = ('id', 'vacancy', 'image_preview', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('vacancy__name',)
    fieldsets = (
        (None, {
            'fields': ('vacancy', 'image')
        }),
    )
    readonly_fields = ('uploaded_at',)
    actions = [export_to_excel]
    export_exclude = ['image']  # Exclude image field from export

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image.url)
        return "No Image"

    image_preview.short_description = 'Image Preview'

    export_to_excel.short_description = "Export selected to Excel"


# Custom admin for Order
@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = ('id', 'service', 'vacancy', 'client', 'executor', 'date_order', 'status', 'price')
    list_filter = ('status', 'date_order', 'client', 'executor')
    search_fields = ('service__name', 'vacancy__name', 'client__name', 'executor__name')
    fieldsets = (
        (None, {
            'fields': ('service', 'vacancy', 'client', 'executor', 'price', 'status', 'date_execution')
        }),
    )
    readonly_fields = ('date_order',)
    actions = [export_to_excel]

    export_to_excel.short_description = "Export selected to Excel"


@admin.register(OrderReview)
class OrderReviewAdmin(ModelAdmin):
    list_display = ('id', 'order', 'reviewer', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('order__id', 'reviewer__phone', 'review')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

    fieldsets = (
        (None, {
            'fields': ('order', 'reviewer', 'rating', 'review')
        }),
        ('Дата создания', {
            'fields': ('created_at',),
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('order', 'reviewer')


# Custom admin for OTP_table
@admin.register(OTP_table)
class OTPAdmin(ModelAdmin):
    list_display = ('phone', 'code', 'created_at', 'expires_at')
    list_filter = ('created_at',)
    search_fields = ('phone', 'code')
    fieldsets = (
        (None, {
            'fields': ('phone', 'code', 'created_at', 'expires_at')
        }),
    )
    readonly_fields = ('created_at',)
    actions = [export_to_excel]
    verbose_name = 'OTP Table'
    verbose_name_plural = 'OTP Tables'

    export_to_excel.short_description = "Export selected to Excel"


# Custom admin for Chat_table
@admin.register(Chat_table)
class ChatTableAdmin(ModelAdmin):
    list_display = ('phone', 'chat_id')
    list_filter = (ChatPhoneFilter,)
    search_fields = ('phone', 'chat_id')
    fieldsets = (
        (None, {
            'fields': ('phone', 'chat_id')
        }),
    )
    actions = [export_to_excel]

    export_to_excel.short_description = "Export selected to Excel"


# Custom admin for Payment
# @admin.register(Payment)
# class PaymentAdmin(admin.ModelAdmin):
#     list_display = ('id', 'order', 'client', 'executor', 'date_order', 'status', 'amount', 'price')
#     list_filter = (PaymentStatusFilter, 'date_order', 'client', 'executor')
#     search_fields = ('order__id', 'client__name', 'executor__name')
#     fieldsets = (
#         (None, {
#             'fields': ('order', 'client', 'executor', 'amount', 'price', 'status', 'date_execution')
#         }),
#     )
#     readonly_fields = ('date_order',)
#     actions = [export_to_excel]
#
#     export_to_excel.short_description = "Export selected to Excel"

# Custom admin for ChatRoom
@admin.register(ChatRoom)
class ChatRoomAdmin(ModelAdmin):
    list_display = ('name', 'user1', 'user2', 'created_at')
    list_filter = ('created_at', 'user1', 'user2')
    search_fields = ('name', 'user1__name', 'user2__name')
    inlines = [MessageInline]
    fieldsets = (
        (None, {
            'fields': ('name', 'user1', 'user2')
        }),
    )
    readonly_fields = ('created_at',)
    actions = [export_to_excel]

    export_to_excel.short_description = "Export selected to Excel"


# Custom admin for Message
@admin.register(Message)
class MessageAdmin(ModelAdmin):
    list_display = ('room', 'sender', 'content_preview', 'timestamp')
    list_filter = ('timestamp', 'sender')
    search_fields = ('content', 'sender__name', 'room__name')
    fieldsets = (
        (None, {
            'fields': ('room', 'sender', 'content', 'file')
        }),
    )
    readonly_fields = ('timestamp',)
    actions = [export_to_excel]

    def content_preview(self, obj):
        return obj.content[:50] + ('...' if len(obj.content) > 50 else '')

    content_preview.short_description = 'Content'

    export_to_excel.short_description = "Export selected to Excel"


# Custom admin for Ad
@admin.register(Ad)
class AdAdmin(ModelAdmin):
    list_display = ('id', 'image_preview', 'start_date', 'end_date', 'region', 'link')
    list_filter = ('start_date', 'end_date')
    search_fields = ('region', 'link')
    fieldsets = (
        (None, {
            'fields': ('image', 'start_date', 'end_date', 'region', 'link')
        }),
    )
    actions = [export_to_excel]
    export_exclude = ['image']  # Exclude image field from export

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" style="object-fit: cover;" />', obj.image.url)
        return "No Image"

    image_preview.short_description = 'Ad Banner Preview'

    export_to_excel.short_description = "Export selected to Excel"


# Custom admin for ExecutorReview
@admin.register(ExecutorReview)
class ExecutorReviewAdmin(ModelAdmin):
    list_display = ('id', 'order', 'executor', 'client', 'rating', 'review_preview', 'created_at')
    list_filter = (RatingFilter, 'created_at', 'order', 'executor', 'client')
    search_fields = ('order__id', 'executor__name', 'client__name', 'review')
    fieldsets = (
        (None, {
            'fields': ('order', 'executor', 'client', 'rating', 'review')
        }),
    )
    readonly_fields = ('created_at',)
    actions = [export_to_excel]

    def review_preview(self, obj):
        return obj.review[:50] + ('...' if len(obj.review) > 50 else '')

    review_preview.short_description = 'Review'

    export_to_excel.short_description = "Export selected to Excel"


# Custom admin for ClientReview
@admin.register(ClientReview)
class ClientReviewAdmin(ModelAdmin):
    list_display = ('id', 'order', 'executor', 'client', 'rating', 'review_preview', 'created_at')
    list_filter = (RatingFilter, 'created_at', 'order', 'executor', 'client')
    search_fields = ('order__id', 'executor__name', 'client__name', 'review')
    fieldsets = (
        (None, {
            'fields': ('order', 'executor', 'client', 'rating', 'review')
        }),
    )
    readonly_fields = ('created_at',)
    actions = [export_to_excel]

    def review_preview(self, obj):
        return obj.review[:50] + ('...' if len(obj.review) > 50 else '')

    review_preview.short_description = 'Review'

    export_to_excel.short_description = "Export selected to Excel"


class BoostPaymentStatusFilter(SimpleListFilter):
    title = 'Payment Status'
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return [
            ('pending', 'Pending'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status=self.value())
        return queryset


@admin.register(BoostPayment)
class BoostPaymentAdmin(ModelAdmin):
    list_display = ('id', 'boost_payment_id', 'get_service_or_vacancy', 'boost', 'amount', 'status', 'created_at')
    list_filter = (BoostPaymentStatusFilter, 'created_at', 'boost_payment_id')
    search_fields = ('boost__name', 'service__name', 'vacancy__name')
    fieldsets = (
        (None, {
            'fields': ('amount', 'service', 'vacancy', 'boost', 'status')
        }),
    )
    readonly_fields = ('created_at',)
    actions = [export_to_excel]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('boost', 'service', 'vacancy')

    def get_service_or_vacancy(self, obj):
        if obj.service:
            return obj.service.name
        elif obj.vacancy:
            return obj.vacancy.name
        return "None"

    get_service_or_vacancy.short_description = 'Service/Vacancy'

    export_to_excel.short_description = "Export selected to Excel"


# Custom admin for Boost
@admin.register(Boost)
class BoostAdmin(ModelAdmin):
    list_display = ('id', 'name', 'boost_type', 'duration_days', 'price', 'discount', 'applies_to')
    list_filter = ('boost_type', 'applies_to')
    search_fields = ('name',)
    fieldsets = (
        (None, {
            'fields': ('name', 'boost_type', 'duration_days', 'price', 'discount', 'applies_to')
        }),
    )
    actions = [export_to_excel]

    export_to_excel.short_description = "Export selected to Excel"


# Custom admin for ServiceBoost
@admin.register(ServiceBoost)
class ServiceBoostAdmin(ModelAdmin):
    list_display = ('id', 'service', 'boost', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active', 'start_date', 'end_date')
    search_fields = ('service__name', 'boost__name')
    fieldsets = (
        (None, {
            'fields': ('service', 'boost', 'start_date', 'is_active')
        }),
    )
    readonly_fields = ('start_date',)
    actions = [export_to_excel]

    export_to_excel.short_description = "Export selected to Excel"


# Custom admin for VacancyBoost
@admin.register(VacancyBoost)
class VacancyBoostAdmin(ModelAdmin):
    list_display = ('id', 'vacancy', 'boost', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active', 'start_date', 'end_date')
    search_fields = ('vacancy__name', 'boost__name')
    fieldsets = (
        (None, {
            'fields': ('vacancy', 'boost', 'start_date', 'is_active')
        }),
    )
    readonly_fields = ('start_date',)
    actions = [export_to_excel]

    export_to_excel.short_description = "Export selected to Excel"