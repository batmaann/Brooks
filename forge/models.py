from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _


class FuelType(models.TextChoices):
    AI92 = 'АИ-92', _('АИ-92')
    AI95 = 'АИ-95', _('АИ-95')
    AI98 = 'АИ-98', _('АИ-98')
    DIESEL = 'ДТ', _('Дизель')
    GAS = 'ГАЗ', _('Газ')


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


class GasStation(models.Model):
    """Модель для автозаправочных станций"""
    name = models.CharField(_('Название АЗС'), max_length=255)
    number = models.CharField(_('Номер АЗС'), max_length=50, blank=True)
    address = models.TextField(_('Адрес'), blank=True)
    company = models.CharField(_('Компания'), max_length=100, blank=True)

    class Meta:
        verbose_name = _('АЗС')
        verbose_name_plural = _('АЗС')
        ordering = ['company', 'name']

    def __str__(self):
        if self.number:
            return f"{self.company} {self.name} №{self.number}"
        return f"{self.company} {self.name}"


class Vehicle(models.Model):
    """Модель для транспортных средств"""
    name = models.CharField(_('Название'), max_length=100)
    brand = models.CharField(_('Марка'), max_length=50, null=True, blank=True)
    model = models.CharField(_('Модель'), max_length=50, null=True, blank=True)
    year = models.IntegerField(_('Год выпуска'), null=True, blank=True, validators=[
        MinValueValidator(1900),
        MaxValueValidator(2100)
    ])
    license_plate = models.CharField(_('Госномер'), max_length=20, blank=True, help_text='у123хм456')
    initial_odometer = models.IntegerField(_('Начальный пробег'), default=0)
    is_active = models.BooleanField(_('Активный'), default=True)

    class Meta:
        verbose_name = _('Транспортное средство')
        verbose_name_plural = _('Транспортные средства')
        ordering = ['name']

    def __str__(self):
        return self.name

    def current_odometer(self):
        """Текущий пробег"""
        last_refuel = Refueling.objects.filter(vehicle=self).order_by('-date').first()
        if last_refuel:
            return last_refuel.odometer
        return self.initial_odometer


class Refueling(models.Model):
    """Модель для заправок топлива"""
    date = models.DateField(_('Дата заправки'))
    month = models.IntegerField(_('Месяц'), choices=Month.choices)
    quarter = models.IntegerField(_('Квартал'), choices=Quarter.choices)

    # Пробег
    mileage = models.IntegerField(_('Пробег с прошлой заправки (км)'), validators=[MinValueValidator(0)])
    odometer = models.IntegerField(_('Показания одометра (км)'), validators=[MinValueValidator(0)])

    # Топливо
    fuel_quantity = models.DecimalField(_('Количество топлива (л)'), max_digits=6, decimal_places=2,
                                        validators=[MinValueValidator(0)])
    price_per_liter = models.DecimalField(_('Цена за литр (₽)'), max_digits=6, decimal_places=2,
                                          validators=[MinValueValidator(0)])
    total_cost = models.DecimalField(_('Общая стоимость (₽)'), max_digits=8, decimal_places=2,
                                     validators=[MinValueValidator(0)])

    # Связи
    gas_station = models.ForeignKey(GasStation, on_delete=models.SET_NULL, null=True,
                                    verbose_name=_('АЗС'))
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, verbose_name=_('Транспортное средство'))
    fuel_type = models.CharField(_('Тип топлива'), max_length=20, choices=FuelType.choices)

    # Дополнительная информация
    is_full_tank = models.BooleanField(_('Полный бак'), default=False)
    discount = models.DecimalField(_('Скидка (₽)'), max_digits=8, decimal_places=2, default=0,
                                   validators=[MinValueValidator(0)])
    comment = models.TextField(_('Комментарий'), blank=True)

    # Метаданные
    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Дата обновления'), auto_now=True)

    class Meta:
        verbose_name = _('Заправка')
        verbose_name_plural = _('Заправки')
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['vehicle']),
            models.Index(fields=['fuel_type']),
        ]

    def __str__(self):
        return f"{self.date}: {self.vehicle} - {self.fuel_quantity}л"

    def save(self, *args, **kwargs):
        # Автоматический расчет общей стоимости, если не задана
        if not self.total_cost and self.fuel_quantity and self.price_per_liter:
            self.total_cost = self.fuel_quantity * self.price_per_liter

        # Автоматическое определение месяца и квартала из даты
        if self.date:
            self.month = self.date.month
            self.quarter = ((self.date.month - 1) // 3) + 1

        super().save(*args, **kwargs)

    @property
    def effective_cost(self):
        """Эффективная стоимость с учетом скидки"""
        return self.total_cost - self.discount

    @property
    def fuel_consumption(self):
        """Расход топлива на 100 км"""
        if self.mileage > 0:
            return (self.fuel_quantity / self.mileage) * 100
        return 0


class FuelPrice(models.Model):
    """Модель для отслеживания цен на топливо"""
    date = models.DateField(_('Дата'))
    fuel_type = models.CharField(_('Тип топлива'), max_length=20, choices=FuelType.choices)
    price = models.DecimalField(_('Цена (₽/л)'), max_digits=6, decimal_places=2,
                                validators=[MinValueValidator(0)])
    gas_station = models.ForeignKey(GasStation, on_delete=models.CASCADE,
                                    verbose_name=_('АЗС'), null=True, blank=True)

    class Meta:
        verbose_name = _('Цена топлива')
        verbose_name_plural = _('Цены на топливо')
        ordering = ['-date', 'fuel_type']
        unique_together = ['date', 'fuel_type', 'gas_station']

    def __str__(self):
        station = f" на {self.gas_station}" if self.gas_station else ""
        return f"{self.date}: {self.get_fuel_type_display()} - {self.price}₽{station}"


# Модель для статистики (может быть виртуальной или материализованной)
class FuelStatistics(models.Model):
    """Модель для хранения агрегированной статистики"""
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, verbose_name=_('Транспортное средство'))
    period = models.DateField(_('Период'))  # Например, первый день месяца
    period_type = models.CharField(_('Тип периода'), max_length=10,
                                   choices=[('month', 'Месяц'), ('quarter', 'Квартал'), ('year', 'Год')])

    total_distance = models.IntegerField(_('Общий пробег (км)'), default=0)
    total_fuel = models.DecimalField(_('Общее топливо (л)'), max_digits=8, decimal_places=2, default=0)
    total_cost = models.DecimalField(_('Общая стоимость (₽)'), max_digits=10, decimal_places=2, default=0)
    avg_consumption = models.DecimalField(_('Средний расход (л/100км)'), max_digits=6, decimal_places=2, default=0)
    avg_price = models.DecimalField(_('Средняя цена (₽/л)'), max_digits=6, decimal_places=2, default=0)

    class Meta:
        verbose_name = _('Статистика расхода')
        verbose_name_plural = _('Статистика расхода')
        unique_together = ['vehicle', 'period', 'period_type']
        ordering = ['-period', 'vehicle']

    def __str__(self):
        return f"{self.vehicle} - {self.period}: {self.avg_consumption}л/100км"