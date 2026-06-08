from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.models import FinanceOperation, FinanceType, Project
from forge.models import Refueling, Vehicle


class FinanceOperationTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='finance-user', password='test-password',
        )
        self.project = Project.objects.create(name='Okozukai', user=self.user)

    def test_month_and_quarter_are_derived_from_date(self):
        operation = FinanceOperation.objects.create(
            date=date(2024, 5, 1), movement_type=FinanceType.EXPENSE,
            project=self.project, amount=Decimal('11689.00'), user=self.user,
        )
        self.assertEqual(operation.month, 5)
        self.assertEqual(operation.quarter, 2)
        self.assertEqual(operation.signed_amount, Decimal('-11689.00'))

    def test_project_slug_is_generated(self):
        self.assertEqual(self.project.slug, 'okozukai')

    def test_refueling_is_synchronized_with_finance_operation(self):
        vehicle = Vehicle.objects.create(name='Test car', user=self.user)
        refueling = Refueling.objects.create(
            date=date(2024, 5, 1), mileage=300, fuel_quantity=Decimal('40.00'),
            price_per_liter=Decimal('50.00'), discount=Decimal('100.00'),
            vehicle=vehicle, user=self.user,
        )

        operation = FinanceOperation.objects.get(source_object_id=refueling.pk)
        self.assertEqual(operation.project.slug, 'forge')
        self.assertEqual(operation.amount, Decimal('1900.00'))

        refueling.discount = Decimal('200.00')
        refueling.save()
        operation.refresh_from_db()
        self.assertEqual(operation.amount, Decimal('1800.00'))

        refueling.delete()
        self.assertFalse(FinanceOperation.objects.filter(pk=operation.pk).exists())
