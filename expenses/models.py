from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class ExpenseCategory(models.Model):
    """Редактируемая категория расходов."""
    slug = models.SlugField(_('Код'), max_length=50, unique=True)
    name = models.CharField(_('Название'), max_length=100)
    description = models.TextField(_('Описание'), blank=True)
    is_active = models.BooleanField(_('Активна'), default=True)

    class Meta:
        verbose_name = _('Категория расходов')
        verbose_name_plural = _('Категории расходов')
        ordering = ['name']

    def __str__(self):
        return self.name


class Expense(models.Model):
    """Универсальная строка расхода, не привязанная к автомобилям."""
    date = models.DateField(_('Дата траты'))
    category = models.ForeignKey(ExpenseCategory, on_delete=models.PROTECT,
                                 verbose_name=_('Категория'), related_name='expenses')
    amount = models.DecimalField(_('Сумма (₽)'), max_digits=12, decimal_places=2,
                                 validators=[MinValueValidator(0)])
    description = models.CharField(_('Описание'), max_length=255, blank=True)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             verbose_name=_('Пользователь'), related_name='expenses')

    source_app = models.CharField(_('Приложение-источник'), max_length=50, blank=True)
    source_model = models.CharField(_('Модель-источник'), max_length=50, blank=True)
    source_id = models.PositiveBigIntegerField(_('ID источника'), null=True, blank=True)
    metadata = models.JSONField(_('Дополнительные данные'), default=dict, blank=True)

    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Дата обновления'), auto_now=True)

    class Meta:
        verbose_name = _('Трата')
        verbose_name_plural = _('Траты')
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['user', 'category']),
            models.Index(fields=['source_app', 'source_model', 'source_id']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['source_app', 'source_model', 'source_id'],
                name='unique_expense_source',
                condition=models.Q(source_app__gt='', source_model__gt=''),
            ),
        ]

    def __str__(self):
        return f"{self.date}: {self.category} - {self.amount}₽"
