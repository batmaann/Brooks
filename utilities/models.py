from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _


class Quarter(models.IntegerChoices):
    FIRST = 1, _('1 квартал')
    SECOND = 2, _('2 квартал')
    THIRD = 3, _('3 квартал')
    FOURTH = 4, _('4 квартал')


class Month(models.IntegerChoices):
    JANUARY = 1, _('Январь')
    FEBRUARY = 2, _('Февраль')
    MARCH = 3, _('Март')
    APRIL = 4, _('Апрель')
    MAY = 5, _('Май')
    JUNE = 6, _('Июнь')
    JULY = 7, _('Июль')
    AUGUST = 8, _('Август')
    SEPTEMBER = 9, _('Сентябрь')
    OCTOBER = 10, _('Октябрь')
    NOVEMBER = 11, _('Ноябрь')
    DECEMBER = 12, _('Декабрь')


class Bank(models.TextChoices):
    M1 = 'MK1', _('Сбербанк (MK1)')
    M2 = 'MK2', _('Тинькофф (MK2)')
    M3 = 'M3', _('ВТБ (M3)')
    OTHER = 'OTHER', _('Другой')


class Company(models.Model):
    name = models.CharField(_('Название компании'), max_length=255)
    category_name = models.CharField(_('Краткое название/Категория'), max_length=100, null=True, blank=True)
    account_number = models.CharField(_('Номер лицевого счета'), max_length=100, null=True, blank=True)

    class Meta:
        verbose_name = _('Компания')
        verbose_name_plural = _('Компании')

    def __str__(self):
        return self.category_name or self.name


class UtilityPayment(models.Model):
    """Модель для учета коммунальных платежей"""
    # Основные данные
    date = models.DateField(_('Дата платежа'))
    month = models.IntegerField(_('Месяц'), choices=Month.choices)
    quarter = models.IntegerField(_('Квартал'), choices=Quarter.choices)

    # Компания и описание
    company = models.ForeignKey(
        Company,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Компания'),
        related_name='payments'
    )
    company_name = models.CharField(_('Название компании'), max_length=255)
    description = models.TextField(_('Описание услуги'))

    # Финансовые данные
    price = models.DecimalField(
        _('Сумма (₽)'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    is_paid = models.BooleanField(_('Оплачено'), default=False)
    billing_statement = models.CharField(_('Номер счета'), max_length=100, blank=True)

    # Банковские данные
    bank = models.CharField(
        _('Банк'),
        max_length=20,
        choices=Bank.choices,
        blank=True,
        null=True
    )

    # Статус и комментарии
    needs_payment = models.BooleanField(_('Требует оплаты'), default=False)
    isReported = models.BooleanField(_('Уведомление показаний счётчика'), default=False)
    comment = models.TextField(_('Комментарий'), blank=True, null=True)

    # Метаданные
    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Дата обновления'), auto_now=True)

    class Meta:
        verbose_name = _('Коммунальный платеж')
        verbose_name_plural = _('Коммунальные платежи')
        ordering = ['-date', 'company_name']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['month', 'quarter']),
            models.Index(fields=['company_name']),
            models.Index(fields=['is_paid', 'needs_payment']),
            models.Index(fields=['bank']),
        ]

    def __str__(self):
        return f"{self.date}: {self.company_name} - {self.price}₽"

    def save(self, *args, **kwargs):
        # Автоматическое определение месяца и квартала из даты, если не заданы
        if self.date and (not self.month or not self.quarter):
            self.month = self.date.month
            self.quarter = ((self.date.month - 1) // 3) + 1

        # Если выбрана компания из базы, используем ее название
        if self.company and not self.company_name:
            self.company_name = self.company.name

        super().save(*args, **kwargs)

    @property
    def formatted_price(self):
        """Отформатированная сумма"""
        return f"{self.price:,.2f} ₽".replace(',', ' ')

    @property
    def status(self):
        """Статус платежа"""
        if self.is_paid:
            return _('Оплачен')
        elif self.needs_payment:
            return _('Требует оплаты')
        else:
            return _('В ожидании')


class MonthlySummary(models.Model):
    """Модель для месячной статистики платежей"""
    year = models.IntegerField(_('Год'), validators=[MinValueValidator(2000), MinValueValidator(2100)])
    month = models.IntegerField(_('Месяц'), choices=Month.choices)

    total_payments = models.DecimalField(_('Всего платежей'), max_digits=12, decimal_places=2, default=0)
    paid_amount = models.DecimalField(_('Оплачено'), max_digits=12, decimal_places=2, default=0)
    pending_amount = models.DecimalField(_('Ожидает оплаты'), max_digits=12, decimal_places=2, default=0)

    # Статистика по категориям (теперь на основе описания или названия компании)
    electricity_total = models.DecimalField(_('Электроэнергия'), max_digits=10, decimal_places=2, default=0)
    gas_total = models.DecimalField(_('Газ'), max_digits=10, decimal_places=2, default=0)
    water_total = models.DecimalField(_('Вода'), max_digits=10, decimal_places=2, default=0)
    rent_total = models.DecimalField(_('Аренда/Наем'), max_digits=10, decimal_places=2, default=0)
    maintenance_total = models.DecimalField(_('Содержание и ремонт'), max_digits=10, decimal_places=2, default=0)
    trash_total = models.DecimalField(_('Твердые отходы'), max_digits=10, decimal_places=2, default=0)
    internet_total = models.DecimalField(_('Интернет'), max_digits=10, decimal_places=2, default=0)
    other_total = models.DecimalField(_('Прочее'), max_digits=10, decimal_places=2, default=0)

    # Количество платежей
    payment_count = models.IntegerField(_('Количество платежей'), default=0)
    paid_count = models.IntegerField(_('Оплаченных'), default=0)
    pending_count = models.IntegerField(_('Ожидающих'), default=0)

    class Meta:
        verbose_name = _('Месячный отчет')
        verbose_name_plural = _('Месячные отчеты')
        ordering = ['-year', '-month']
        unique_together = ['year', 'month']
        indexes = [
            models.Index(fields=['year', 'month']),
        ]

    def __str__(self):
        return f"{self.year}-{self.month:02d}: {self.total_payments}₽"

    @property
    def completion_rate(self):
        """Процент оплаты"""
        if self.total_payments > 0:
            return (self.paid_amount / self.total_payments) * 100
        return 0


class RecurringPayment(models.Model):
    """Модель для регулярных (ежемесячных) платежей"""
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        verbose_name=_('Компания'),
        related_name='recurring_payments'
    )
    description = models.TextField(_('Описание'))
    amount = models.DecimalField(
        _('Сумма (₽)'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    due_day = models.IntegerField(
        _('День оплаты'),
        validators=[MinValueValidator(1), MinValueValidator(31)],
        help_text=_('День месяца, когда должен быть произведен платеж')
    )
    bank = models.CharField(
        _('Банк'),
        max_length=20,
        choices=Bank.choices,
        blank=True,
        null=True
    )
    is_active = models.BooleanField(_('Активный'), default=True)
    auto_create = models.BooleanField(
        _('Автосоздание'),
        default=True,
        help_text=_('Автоматически создавать платежи каждый месяц')
    )

    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Дата обновления'), auto_now=True)

    class Meta:
        verbose_name = _('Регулярный платеж')
        verbose_name_plural = _('Регулярные платежи')
        ordering = ['due_day', 'company']

    def __str__(self):
        return f"{self.company}: {self.description} - {self.amount}₽ (до {self.due_day} числа)"


class PaymentTemplate(models.Model):
    """Шаблон для быстрого создания платежей"""
    name = models.CharField(_('Название шаблона'), max_length=100)
    company_name = models.CharField(_('Компания'), max_length=255)
    description = models.TextField(_('Описание'))
    default_amount = models.DecimalField(
        _('Сумма по умолчанию (₽)'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    default_bank = models.CharField(
        _('Банк по умолчанию'),
        max_length=20,
        choices=Bank.choices,
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = _('Шаблон платежа')
        verbose_name_plural = _('Шаблоны платежей')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.company_name})"