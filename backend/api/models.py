import uuid

from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import BaseUserManager

def get_default_end_date():
    return timezone.now() + timedelta(days=7)

class UserManager(BaseUserManager):
    def create_user(self, phone, email=None, password=None, **extra_fields):
        if not phone:
            raise ValueError('The Phone field must be set')
        user = self.model(phone=phone, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(phone, email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    REGIONS = [
        ('Республика Каракалпакстан', 'Республика Каракалпакстан'),
        ('Андижанская область', 'Андижанская область'),
        ('Бухарская область', 'Бухарская область'),
        ('Джизакская область', 'Джизакская область'),
        ('Кашкадарьинская область', 'Кашкадарьинская область'),
        ('Навоийская область', 'Навоийская область'),
        ('Наманганская область', 'Наманганская область'),
        ('Самаркандская область', 'Самаркандская область'),
        ('Сырдарьинская область', 'Сырдарьинская область'),
        ('Сурхандарьинская область', 'Сурхандарьинская область'),
        ('Ташкентская область', 'Ташкентская область'),
        ('Ферганская область', 'Ферганская область'),
        ('Хорезмская область', 'Хорезмская область'),
        ('Город Ташкент', 'Город Ташкент'),
    ]

    name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(unique=False, null=True, blank=True)
    phone = PhoneNumberField(unique=True)
    about_user = models.TextField(null=True, blank=True)
    work_experience = models.FloatField(null=True, blank=True)
    role = models.CharField(
        max_length=50,
        choices=[('клиент', 'Клиент'), ('специалист', 'Специалист')],
        default='клиент'
    )
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    region = models.CharField(
        max_length=100,
        choices=REGIONS,
        null=True,
        blank=True
    )

    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    telegram_username = models.CharField(max_length=255, null=True, blank=True)
    telegram_id = models.BigIntegerField(unique=True, null=True, blank=True)
    gender = models.CharField(
        max_length=10,
        choices=[('male', 'Male'), ('female', 'Female')],
        null=True,
        blank=True
    )
    executor_rating = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)]
    )
    client_rating = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)]
    )
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    birthday = models.DateField(null=True, blank=True)
    lang = models.CharField(
        max_length=5,
        choices=[('ru', 'Ru'), ('uz', 'Uz')],
        default="ru"
    )
    orders_count = models.IntegerField(
        verbose_name="Количество заказов",
        default=0,
        validators=[MinValueValidator(0)]
    )
    created_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_users',
        verbose_name='Кем создан'
    )

    objects = UserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'users'
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return str(self.phone)

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

    def is_trusted(self) -> bool:
        return self.orders_count > 3

    def update_ratings(self):
        # Calculate average executor rating
        executor_reviews = self.executor_reviews_as_executor.all()
        if executor_reviews.exists():
            self.executor_rating = executor_reviews.aggregate(avg_rating=models.Avg('rating'))['avg_rating'] or 0.0
        else:
            self.executor_rating = 0.0

        # Calculate average client rating
        client_reviews = self.client_reviews_as_client.all()
        if client_reviews.exists():
            self.client_rating = client_reviews.aggregate(avg_rating=models.Avg('rating'))['avg_rating'] or 0.0
        else:
            self.client_rating = 0.0

        self.save()

    def created_by_display(self):
        if self.created_by:
            return self.created_by.name or str(self.created_by.phone)
        return "Сам"

    created_by_display.short_description = "Кем создан"

class OTP_table(models.Model):
    session_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    phone = PhoneNumberField()
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        db_table = 'otp_table'
        verbose_name = "OTP таблица"
        verbose_name_plural = "OTP таблицы"

    def __str__(self):
        return f"Code {self.code} for {self.phone}"

class Category(models.Model):
    title = models.CharField(max_length=255)
    display_ru = models.CharField(max_length=255, null=True, blank=True)
    display_uz = models.CharField(max_length=255, null=True, blank=True)
    service_count = models.IntegerField(default=0)

    class Meta:
        db_table = "categories"
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.title

class SubCategory(models.Model):
    title = models.CharField(max_length=255)
    display_ru = models.CharField(max_length=255, blank=True, null=True)
    display_uz = models.CharField(max_length=255, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='sub_categories')

    class Meta:
        db_table = 'sub_categories'
        verbose_name = "Подкатегория"
        verbose_name_plural = "Подкатегории"

    def __str__(self):
        return self.title

class Service(models.Model):
    MODERATION_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='services')
    sub_categories = models.ManyToManyField(SubCategory, related_name='services')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    executor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='services')
    moderation = models.CharField(max_length=20, choices=MODERATION_CHOICES, default='Pending', null=True, blank=True)
    boost = models.ForeignKey('Boost', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = 'services'
        verbose_name = "Сервис"
        verbose_name_plural = "Сервисы"

    def __str__(self):
        return self.title

class ServiceImage(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='services/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'service_images'
        verbose_name = "Фото сервиса"
        verbose_name_plural = "Фото сервисов"

    def __str__(self):
        return f"Image for {self.service.name} uploaded at {self.uploaded_at}"

class Vacancy(models.Model):
    MODERATION_STATUS = [
        ('pending', 'На модерации'),
        ('approved', 'Одобрено'),
        ('rejected', 'Отклонено'),
    ]
    title = models.CharField(max_length=255, verbose_name="Название")
    description = models.TextField(null=True, blank=True, verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='vacancies', verbose_name="Категория")
    boost = models.ForeignKey('Boost', on_delete=models.CASCADE, null=True, blank=True, verbose_name="Буст")
    sub_category = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name='vacancies', verbose_name="Подкатегория")
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vacancies', verbose_name="Клиент")
    images = models.ImageField(upload_to='vacancies/', verbose_name="Фотография")
    moderation = models.CharField(
        max_length=10,
        choices=MODERATION_STATUS,
        default='pending',
        verbose_name="Модерация"
    )
    class Meta:
        db_table = 'vacancies'
        verbose_name = "Вакансия"
        verbose_name_plural = "Вакансии"

    def __str__(self):
        return self.title

class VacancyImage(models.Model):
    vacancy = models.ForeignKey(
        Vacancy,
        on_delete=models.CASCADE,
        related_name="vacancy_images"
    )
    image = models.ImageField(upload_to="vacancies/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "vacancy_images"
        verbose_name = "Фото вакансии"
        verbose_name_plural = "Фото вакансий"

    def __str__(self):
        return f"Image for {self.vacancy.name}"

class ExecutorReview(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='executor_reviews')
    vacancy = models.ForeignKey(  'Vacancy', on_delete=models.CASCADE, related_name='executor_reviews_as_vacancy', null=True, blank=True)
    executor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='executor_reviews_as_executor')
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='executor_reviews_as_client')
    rating = models.FloatField(validators=[MinValueValidator(1.0), MaxValueValidator(5.0)])
    review = models.TextField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'executor_reviews'
        verbose_name = "Отзыв о исполнителе"
        verbose_name_plural = "Отзывы о исполнителях"
        unique_together = ('order', 'client')

class ClientReview(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='client_reviews')
    executor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='client_reviews_as_executor'
    )
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='client_reviews_as_client'
    )
    rating = models.FloatField(
        validators=[MinValueValidator(1.0), MaxValueValidator(5.0)],
        help_text="Rating between 1.0 and 5.0"
    )
    review = models.TextField(max_length=250, help_text="Review text up to 250 characters")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'client_reviews'
        verbose_name = "Отзыв клиента"
        verbose_name_plural = "Отзывы клиентов"
        unique_together = ('order', 'executor')  # Prevent multiple reviews by the same executor for an order

    def __str__(self):
        return f"Review by {self.executor} for client {self.client} on order {self.order.id}"

class ChatRoom(models.Model):
    user1 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chatrooms_as_user1'
    )
    user2 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chatrooms_as_user2'
    )
    name = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="chat_rooms",
        blank=True
    )

    class Meta:
        verbose_name = "Комната чата"
        verbose_name_plural = "Комнаты чатов"

    def __str__(self):
        return self.name or f"{self.user1} ↔ {self.user2}"

class Chat_table(models.Model):
    phone = PhoneNumberField(unique=True)
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chats_started")
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chats_received")
    chat_id = models.BigIntegerField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_message = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Таблица чата"
        verbose_name_plural = "Таблицы чатов"

    def __str__(self):
        return f"Chat {self.id}: {self.user1} - {self.user2}"

class Order(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='orders', null=True, blank=True)
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE, related_name='orders', null=True, blank=True)
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='client_orders')
    status = models.CharField(max_length=50, choices=[
        ('Awaiting', 'Awaiting'),
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled')
    ], default='Awaiting')
    executor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders_as_executor", null=True,
                  blank=True)
    date_order = models.DateTimeField(auto_now_add=True)
    date_execution = models.DateTimeField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        db_table = 'orders'
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return str(self.id)

class OrderReview(models.Model):
    order = models.OneToOneField('Order', on_delete=models.CASCADE, related_name='order_review')
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='order_reviews_as_reviewer'
    )
    rating = models.FloatField(
        validators=[MinValueValidator(1.0), MaxValueValidator(5.0)],
        help_text="Rating between 1.0 and 5.0"
    )
    review = models.TextField(max_length=250, help_text="Review text up to 250 characters")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'order_reviews'
        verbose_name = "Отзыв о заказе"
        verbose_name_plural = "Отзывы о заказах"

    def __str__(self):
        return f"Отзыв на заказ #{self.order.id} от {self.reviewer.name}"

class Ad(models.Model):
    image = models.ImageField(upload_to='ads/', verbose_name="Ad Banner")
    start_date = models.DateTimeField(default=timezone.now, verbose_name="Start of Showing Ad")
    end_date = models.DateTimeField(default=get_default_end_date,
                                    verbose_name="End of Showing Ad")
    region = models.CharField(max_length=500, null=True, blank=True, verbose_name="Regions (comma-separated)", help_text="Enter regions separated by commas, e.g., 'Region1, Region2'")
    link = models.URLField(max_length=2000, null=True, blank=True, verbose_name="Click Link", help_text="URL where the banner should redirect when clicked")

    class Meta:
        db_table = 'ads'
        verbose_name = "Реклама"
        verbose_name_plural = "Рекламы"

    def __str__(self):
        return f"Ad from {self.start_date} to {self.end_date}"

# New Boost-related models
class Boost(models.Model):
    name = models.CharField(max_length=100, unique=True)  # e.g., "Top 1 Day", "Turbo 1 Week"
    boost_type = models.CharField(max_length=20, choices=[('Top', 'Top'), ('Turbo', 'Turbo')])
    duration_days = models.PositiveIntegerField()  # Duration in days (e.g., 1, 7, 14, 30)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.PositiveIntegerField(default=0)  # Percentage discount
    applies_to = models.CharField(max_length=20, choices=[('Service', 'Service'), ('Vacancy', 'Vacancy')])

    class Meta:
        db_table = 'boosts'
        verbose_name = "Буст"
        verbose_name_plural = "Бусты"

    def __str__(self):
        return f"{self.name} ({self.boost_type}) for {self.applies_to} - {self.duration_days} days"

    @property
    def final_price(self):
        if self.discount and self.discount > 0:
            discounted = self.price - (self.price * Decimal(self.discount) / Decimal(100))
            return discounted.quantize(Decimal('0.01'))
        return self.price

class ServiceBoost(models.Model):
    service = models.ForeignKey('Service', on_delete=models.CASCADE, related_name='boosts')
    boost = models.ForeignKey('Boost', on_delete=models.CASCADE, related_name='service_boosts')
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(editable=False)
    is_active = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Буст сервиса"
        verbose_name_plural = "Бусты сервисов"
        ordering = ['-is_active', '-start_date']

    def __str__(self):
        return f"Boost {self.service} ({self.boost.name}) до {self.end_date:%d.%m.%Y}"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.end_date = self.start_date + timedelta(days=self.boost.duration_days)
        super().save(*args, **kwargs)

    def check_status(self):
        if self.is_active and timezone.now() > self.end_date:
            self.is_active = False
            self.save()

class VacancyBoost(models.Model):
    vacancy = models.ForeignKey('Vacancy', on_delete=models.CASCADE, related_name='boosts')
    boost = models.ForeignKey('Boost', on_delete=models.CASCADE, related_name='vacancy_boosts')
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(editable=False)
    is_active = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Буст вакансии"
        verbose_name_plural = "Бусты вакансий"
        ordering = ['-is_active', '-start_date']

    def __str__(self):
        return f"Boost {self.vacancy} ({self.boost.name}) до {self.end_date:%d.%m.%Y}"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.end_date = self.start_date + timedelta(days=self.boost.duration_days)
        super().save(*args, **kwargs)

    def check_status(self):
        if self.is_active and timezone.now() > self.end_date:
            self.is_active = False
            self.save()

class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField(null=True,blank=True)
    file = models.FileField(upload_to='chat_files/', null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        db_table = 'messages'
        ordering = ['timestamp']
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"

    def __str__(self):
        return f"Message from {self.sender.name or self.sender.phone} in {self.room.name or 'ChatRoom ' + str(self.room.id)}"

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=['is_read'])

class BoostPayment(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    service = models.ForeignKey('Service', on_delete=models.SET_NULL, null=True, blank=True)
    vacancy = models.ForeignKey('Vacancy', on_delete=models.SET_NULL, null=True, blank=True)
    boost = models.ForeignKey('Boost', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='pending')  # pending, completed, cancelled
    boost_payment_id = models.IntegerField(editable=False, unique=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.boost_payment_id != self.id:
            self.boost_payment_id = self.id
            super().save(update_fields=['boost_payment_id'])

    class Meta:
        verbose_name = "Буст оплаты"
        verbose_name_plural = "Бусты оплат"

    def __str__(self):
        return f"Order #{self.id}"

@receiver(post_save, sender=ExecutorReview)
@receiver(post_save, sender=ClientReview)
def update_user_ratings(sender, instance, created, **kwargs):
    if created:
        if sender == ExecutorReview:
            instance.executor.update_ratings()
        elif sender == ClientReview:
            instance.client.update_ratings()