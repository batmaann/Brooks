from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q


ZERO = Decimal("0")
MONEY_MAX_DIGITS = 14
MONEY_DECIMAL_PLACES = 2
VALUE_MAX_DIGITS = 18
VALUE_DECIMAL_PLACES = 6


class ServiceCategory(models.TextChoices):
    HOUSING = "housing", "Содержание жилья"
    COLD_WATER = "cold_water", "Холодная вода"
    HOT_WATER = "hot_water", "Горячая вода"
    SEWERAGE = "sewerage", "Водоотведение"
    ELECTRICITY = "electricity", "Электроэнергия"
    HEATING = "heating", "Отопление"
    GAS = "gas", "Газ"
    WASTE = "waste", "Обращение с ТКО"
    CAPITAL_REPAIR = "capital_repair", "Капитальный ремонт"
    SECURITY = "security", "Безопасность"
    INSURANCE = "insurance", "Страхование"
    OTHER = "other", "Прочее"


class ConsumptionScope(models.TextChoices):
    INDIVIDUAL = "individual", "Индивидуальное потребление"
    COMMON = "common", "Общедомовые нужды"
    HOUSING = "housing", "Жилищная услуга"
    OTHER = "other", "Прочее"


class CalculationMethod(models.TextChoices):
    METER = "meter", "По счетчику"
    STANDARD = "standard", "По нормативу"
    AREA = "area", "По площади"
    FIXED = "fixed", "Фиксированная сумма"
    OTHER = "other", "Другой способ"
    UNKNOWN = "unknown", "Неизвестно"


class MeterKind(models.TextChoices):
    INDIVIDUAL = "individual", "Индивидуальный"
    COMMON = "common", "Общедомовой"


class UtilityDocument(models.Model):
    """Одна квитанция за один расчетный период."""

    billing_period = models.DateField(
        "расчетный период",
        help_text="Первый день расчетного месяца, например 2026-05-01.",
        db_index=True,
    )
    issued_at = models.DateField("дата квитанции", null=True, blank=True)
    due_at = models.DateField("оплатить до", null=True, blank=True)
    provider = models.CharField(
        "поставщик или расчетный центр", max_length=255, blank=True
    )
    document_number = models.CharField("номер документа", max_length=100, blank=True)
    source_file = models.FileField(
        "исходный файл", upload_to="utility_documents/%Y/%m/", blank=True
    )
    source_hash = models.CharField(
        "SHA-256 файла", max_length=64, blank=True, unique=True, null=True
    )

    accrued_total = models.DecimalField(
        "начислено",
        max_digits=MONEY_MAX_DIGITS,
        decimal_places=MONEY_DECIMAL_PLACES,
        default=ZERO,
    )
    adjustment_total = models.DecimalField(
        "перерасчет",
        max_digits=MONEY_MAX_DIGITS,
        decimal_places=MONEY_DECIMAL_PLACES,
        default=ZERO,
        help_text="Уменьшение хранится отрицательным числом.",
    )
    opening_balance = models.DecimalField(
        "долг или переплата на начало",
        max_digits=MONEY_MAX_DIGITS,
        decimal_places=MONEY_DECIMAL_PLACES,
        default=ZERO,
        help_text="Долг положительный, переплата отрицательная.",
    )
    credited_payment = models.DecimalField(
        "оплата, учтенная в квитанции",
        max_digits=MONEY_MAX_DIGITS,
        decimal_places=MONEY_DECIMAL_PLACES,
        default=ZERO,
        validators=[MinValueValidator(ZERO)],
    )
    amount_due = models.DecimalField(
        "итого к оплате",
        max_digits=MONEY_MAX_DIGITS,
        decimal_places=MONEY_DECIMAL_PLACES,
        validators=[MinValueValidator(ZERO)],
    )
    optional_amount_due = models.DecimalField(
        "итого с добровольными услугами",
        max_digits=MONEY_MAX_DIGITS,
        decimal_places=MONEY_DECIMAL_PLACES,
        null=True,
        blank=True,
        validators=[MinValueValidator(ZERO)],
    )
    notes = models.TextField("примечания", blank=True)
    created_at = models.DateTimeField("добавлено", auto_now_add=True)
    updated_at = models.DateTimeField("изменено", auto_now=True)

    class Meta:
        verbose_name = "квитанция ЖКХ"
        verbose_name_plural = "квитанции ЖКХ"
        ordering = ("-billing_period", "-id")
        indexes = [
            models.Index(fields=("billing_period", "provider")),
        ]

    def __str__(self):
        provider = self.provider or "ЖКХ"
        return f"{provider}: {self.billing_period:%m.%Y} — {self.amount_due} руб."


class UtilityService(models.Model):
    """Справочник услуг, объединяющий разные названия из квитанций."""

    name = models.CharField("название", max_length=150, unique=True)
    category = models.CharField(
        "категория",
        max_length=30,
        choices=ServiceCategory.choices,
        default=ServiceCategory.OTHER,
        db_index=True,
    )
    default_unit = models.CharField(
        "единица измерения",
        max_length=30,
        blank=True,
        help_text="Например: м³, кВт·ч, Гкал, м².",
    )
    is_optional = models.BooleanField(
        "добровольная услуга",
        default=False,
        help_text="Например, добровольное страхование.",
    )

    class Meta:
        verbose_name = "вид услуги"
        verbose_name_plural = "виды услуг"
        ordering = ("category", "name")

    def __str__(self):
        return self.name


class Charge(models.Model):
    """Строка начисления из квитанции."""

    document = models.ForeignKey(
        UtilityDocument,
        on_delete=models.CASCADE,
        related_name="charges",
        verbose_name="квитанция",
    )
    service = models.ForeignKey(
        UtilityService,
        on_delete=models.PROTECT,
        related_name="charges",
        verbose_name="услуга",
    )
    source_name = models.CharField(
        "название в квитанции",
        max_length=255,
        blank=True,
        help_text="Исходный текст нужен для проверки автоматического импорта.",
    )
    scope = models.CharField(
        "область потребления",
        max_length=20,
        choices=ConsumptionScope.choices,
        default=ConsumptionScope.INDIVIDUAL,
    )
    calculation_method = models.CharField(
        "способ расчета",
        max_length=20,
        choices=CalculationMethod.choices,
        default=CalculationMethod.UNKNOWN,
    )
    tariff_zone = models.CharField(
        "тарифная зона",
        max_length=50,
        blank=True,
        help_text="Например: день, ночь, пик.",
    )
    quantity = models.DecimalField(
        "объем",
        max_digits=VALUE_MAX_DIGITS,
        decimal_places=VALUE_DECIMAL_PLACES,
        null=True,
        blank=True,
    )
    unit = models.CharField("единица измерения", max_length=30, blank=True)
    tariff = models.DecimalField(
        "тариф",
        max_digits=VALUE_MAX_DIGITS,
        decimal_places=VALUE_DECIMAL_PLACES,
        null=True,
        blank=True,
    )
    accrued = models.DecimalField(
        "начислено",
        max_digits=MONEY_MAX_DIGITS,
        decimal_places=MONEY_DECIMAL_PLACES,
        default=ZERO,
    )
    adjustment = models.DecimalField(
        "перерасчет",
        max_digits=MONEY_MAX_DIGITS,
        decimal_places=MONEY_DECIMAL_PLACES,
        default=ZERO,
        help_text="Уменьшение хранится отрицательным числом.",
    )
    opening_balance = models.DecimalField(
        "долг или переплата",
        max_digits=MONEY_MAX_DIGITS,
        decimal_places=MONEY_DECIMAL_PLACES,
        default=ZERO,
    )
    credited_payment = models.DecimalField(
        "учтенная оплата",
        max_digits=MONEY_MAX_DIGITS,
        decimal_places=MONEY_DECIMAL_PLACES,
        default=ZERO,
        validators=[MinValueValidator(ZERO)],
    )
    amount_due = models.DecimalField(
        "к оплате",
        max_digits=MONEY_MAX_DIGITS,
        decimal_places=MONEY_DECIMAL_PLACES,
        default=ZERO,
        validators=[MinValueValidator(ZERO)],
    )
    adjustment_reason = models.CharField(
        "основание перерасчета", max_length=500, blank=True
    )

    class Meta:
        verbose_name = "начисление"
        verbose_name_plural = "начисления"
        ordering = ("document", "id")
        indexes = [
            models.Index(fields=("service", "document")),
            models.Index(fields=("scope", "calculation_method")),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(quantity__isnull=True) | Q(quantity__gte=ZERO),
                name="charge_quantity_nonnegative",
            ),
            models.CheckConstraint(
                condition=Q(tariff__isnull=True) | Q(tariff__gte=ZERO),
                name="charge_tariff_nonnegative",
            ),
        ]

    def __str__(self):
        return (
            f"{self.service} — {self.document.billing_period:%m.%Y}: "
            f"{self.amount_due} руб."
        )


class Meter(models.Model):
    """Счетчик без хранения адреса или данных плательщика."""

    service = models.ForeignKey(
        UtilityService,
        on_delete=models.PROTECT,
        related_name="meters",
        verbose_name="услуга",
    )
    serial_number = models.CharField("номер счетчика", max_length=100, blank=True)
    kind = models.CharField(
        "тип счетчика",
        max_length=20,
        choices=MeterKind.choices,
        default=MeterKind.INDIVIDUAL,
    )
    unit = models.CharField("единица измерения", max_length=30)
    verification_due_at = models.DateField(
        "поверка до", null=True, blank=True
    )
    active = models.BooleanField("используется", default=True)
    notes = models.TextField("примечания", blank=True)

    class Meta:
        verbose_name = "счетчик"
        verbose_name_plural = "счетчики"
        ordering = ("service", "serial_number", "id")
        constraints = [
            models.UniqueConstraint(
                fields=("service", "serial_number", "kind"),
                condition=~Q(serial_number=""),
                name="unique_numbered_meter_per_service",
            ),
        ]

    def __str__(self):
        number = f" № {self.serial_number}" if self.serial_number else ""
        return f"{self.service}{number}"


class MeterReading(models.Model):
    """Показание одного счетчика в конкретной тарифной зоне."""

    meter = models.ForeignKey(
        Meter,
        on_delete=models.CASCADE,
        related_name="readings",
        verbose_name="счетчик",
    )
    document = models.ForeignKey(
        UtilityDocument,
        on_delete=models.SET_NULL,
        related_name="meter_readings",
        verbose_name="квитанция",
        null=True,
        blank=True,
    )
    reading_date = models.DateField("дата показания", db_index=True)
    tariff_zone = models.CharField(
        "тарифная зона",
        max_length=50,
        blank=True,
        help_text="Например: день или ночь.",
    )
    previous_value = models.DecimalField(
        "предыдущее показание",
        max_digits=VALUE_MAX_DIGITS,
        decimal_places=VALUE_DECIMAL_PLACES,
        null=True,
        blank=True,
    )
    current_value = models.DecimalField(
        "текущее показание",
        max_digits=VALUE_MAX_DIGITS,
        decimal_places=VALUE_DECIMAL_PLACES,
        validators=[MinValueValidator(ZERO)],
    )
    consumption = models.DecimalField(
        "расход",
        max_digits=VALUE_MAX_DIGITS,
        decimal_places=VALUE_DECIMAL_PLACES,
        null=True,
        blank=True,
        validators=[MinValueValidator(ZERO)],
        help_text="Можно сохранить значение из квитанции или вычислить по показаниям.",
    )

    class Meta:
        verbose_name = "показание счетчика"
        verbose_name_plural = "показания счетчиков"
        ordering = ("-reading_date", "meter", "tariff_zone")
        indexes = [
            models.Index(fields=("meter", "reading_date")),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=("meter", "reading_date", "tariff_zone"),
                name="unique_meter_reading_per_date_and_zone",
            ),
            models.CheckConstraint(
                condition=(
                    Q(previous_value__isnull=True)
                    | Q(current_value__gte=models.F("previous_value"))
                ),
                name="meter_current_not_below_previous",
            ),
        ]

    def save(self, *args, **kwargs):
        if self.consumption is None and self.previous_value is not None:
            self.consumption = self.current_value - self.previous_value
        super().save(*args, **kwargs)

    def __str__(self):
        zone = f" ({self.tariff_zone})" if self.tariff_zone else ""
        return f"{self.meter}{zone}: {self.current_value} на {self.reading_date}"


class Payment(models.Model):
    """Фактически потраченные деньги, а не только начисление в квитанции."""

    document = models.ForeignKey(
        UtilityDocument,
        on_delete=models.SET_NULL,
        related_name="payments",
        verbose_name="квитанция",
        null=True,
        blank=True,
    )
    paid_at = models.DateField("дата оплаты", db_index=True)
    amount = models.DecimalField(
        "сумма",
        max_digits=MONEY_MAX_DIGITS,
        decimal_places=MONEY_DECIMAL_PLACES,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    note = models.CharField("примечание", max_length=255, blank=True)
    created_at = models.DateTimeField("добавлено", auto_now_add=True)

    class Meta:
        verbose_name = "оплата ЖКХ"
        verbose_name_plural = "оплаты ЖКХ"
        ordering = ("-paid_at", "-id")
        indexes = [
            models.Index(fields=("paid_at", "amount")),
        ]

    def __str__(self):
        return f"{self.paid_at}: {self.amount} руб."