from decimal import Decimal

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


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


class Quarter(models.IntegerChoices):
    FIRST = 1, _('1 квартал')
    SECOND = 2, _('2 квартал')
    THIRD = 3, _('3 квартал')
    FOURTH = 4, _('4 квартал')


class FinanceType(models.TextChoices):
    EXPENSE = 'expense', _('Трата')
    INCOME = 'income', _('Доход')
    SAVING = 'saving', _('Сбережение')


class Project(models.Model):
    name = models.CharField(_('Название проекта'), max_length=255)
    slug = models.SlugField(_('Код проекта'), max_length=255, blank=True, allow_unicode=True)
    description = models.TextField(_('Описание'), blank=True)
    started_at = models.DateField(_('Дата начала проекта'), null=True, blank=True)
    finished_at = models.DateField(_('Дата окончания проекта'), null=True, blank=True)
    is_active = models.BooleanField(_('Активен'), default=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='finance_projects', verbose_name=_('Пользователь'),
    )
    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Дата обновления'), auto_now=True)

    class Meta:
        verbose_name = _('Проект')
        verbose_name_plural = _('Проекты')
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(fields=['user', 'name'], name='unique_project_name_per_user'),
            models.UniqueConstraint(fields=['user', 'slug'], name='unique_project_slug_per_user'),
            models.CheckConstraint(
                condition=(models.Q(finished_at__isnull=True) | models.Q(started_at__isnull=True)
                           | models.Q(finished_at__gte=models.F('started_at'))),
                name='project_finished_after_started',
            ),
        ]
        indexes = [models.Index(fields=['user', 'is_active'])]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class BankLabel(models.Model):
    name = models.CharField(_('Название'), max_length=255)
    slug = models.SlugField(_('Код метки'), max_length=255, blank=True, allow_unicode=True)
    color = models.CharField(
        _('Цвет'), max_length=7, default='#3B82F6',
        validators=[RegexValidator(r'^#[0-9A-Fa-f]{6}$', _('Укажите HEX-цвет в формате #3B82F6.'))],
    )
    icon = models.CharField(_('Иконка'), max_length=100, blank=True,
                            help_text=_('Например: bank, cash, card'))
    description = models.TextField(_('Описание'), blank=True)
    is_active = models.BooleanField(_('Активна'), default=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='bank_labels', verbose_name=_('Пользователь'),
    )
    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Дата обновления'), auto_now=True)

    class Meta:
        verbose_name = _('Банковская метка')
        verbose_name_plural = _('Банковские метки')
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(fields=['user', 'name'], name='unique_bank_label_name_per_user'),
            models.UniqueConstraint(fields=['user', 'slug'], name='unique_bank_label_slug_per_user'),
        ]
        indexes = [models.Index(fields=['user', 'is_active'])]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class FinanceOperation(models.Model):
    date = models.DateField(_('Дата'))
    month = models.IntegerField(_('Месяц'), choices=Month.choices, editable=False)
    quarter = models.IntegerField(_('Финансовый квартал'), choices=Quarter.choices, editable=False)
    movement_type = models.CharField(_('Тип движения денег'), max_length=20, choices=FinanceType.choices)
    project = models.ForeignKey(Project, on_delete=models.PROTECT,
                                related_name='finance_operations', verbose_name=_('Проект'))
    amount = models.DecimalField(
        _('Сумма RUB'), max_digits=14, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
    )
    bank_label = models.ForeignKey(
        BankLabel, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='finance_operations', verbose_name=_('Банковская метка'),
    )
    comment = models.TextField(_('Комментарий'), blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='finance_operations', verbose_name=_('Пользователь'),
    )
    # Specialized apps attach their domain object without making core depend on them.
    source_content_type = models.ForeignKey(
        ContentType, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='+', verbose_name=_('Тип исходной записи'),
    )
    source_object_id = models.PositiveBigIntegerField(_('ID исходной записи'), null=True, blank=True)
    source = GenericForeignKey('source_content_type', 'source_object_id')
    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Дата обновления'), auto_now=True)

    class Meta:
        verbose_name = _('Финансовая операция')
        verbose_name_plural = _('Финансовые операции')
        ordering = ['-date', '-created_at']
        constraints = [
            models.CheckConstraint(condition=models.Q(amount__gt=0), name='finance_amount_positive'),
            models.CheckConstraint(
                condition=(models.Q(source_content_type__isnull=True, source_object_id__isnull=True)
                           | models.Q(source_content_type__isnull=False, source_object_id__isnull=False)),
                name='finance_source_fields_together',
            ),
            models.UniqueConstraint(
                fields=['user', 'source_content_type', 'source_object_id'],
                condition=models.Q(source_object_id__isnull=False),
                name='unique_finance_operation_source_per_user',
            ),
        ]
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['user', 'month', 'quarter']),
            models.Index(fields=['project', 'date']),
            models.Index(fields=['source_content_type', 'source_object_id']),
        ]

    def clean(self):
        errors = {}
        if self.project_id and self.user_id and self.project.user_id != self.user_id:
            errors['project'] = _('Проект должен принадлежать пользователю операции.')
        if self.bank_label_id and self.user_id and self.bank_label.user_id != self.user_id:
            errors['bank_label'] = _('Банковская метка должна принадлежать пользователю операции.')
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.month = self.date.month
        self.quarter = ((self.date.month - 1) // 3) + 1
        super().save(*args, **kwargs)

    @property
    def signed_amount(self):
        return -self.amount if self.movement_type == FinanceType.EXPENSE else self.amount

    def __str__(self):
        return (f'{self.date} | {self.get_movement_type_display()} | '
                f'{self.project} | {self.amount} ₽')
