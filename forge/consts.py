from django.db import models
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


class FuelType(models.TextChoices):
    AI92 = 'АИ-92', _('АИ-92')
    AI95 = 'АИ-95', _('АИ-95')
    AI98 = 'АИ-98', _('АИ-98')
    DIESEL = 'ДТ', _('Дизель')
    GAS = 'ГАЗ', _('Газ')
