from datetime import date
from decimal import Decimal

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.test import RequestFactory, TestCase
from django.urls import reverse

from core.admin import FinanceOperationAdmin, ProjectAdmin
from core.models import FinanceOperation, FinanceType, Project


class CoreAdminTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.superuser = user_model.objects.create_superuser(
            username='admin', password='password', email='admin@example.com',
        )
        self.staff_user = user_model.objects.create_user(
            username='staff', password='password', is_staff=True,
        )
        self.other_user = user_model.objects.create_user(
            username='other', password='password',
        )
        self.staff_project = Project.objects.create(name='Staff project', user=self.staff_user)
        self.other_project = Project.objects.create(name='Other project', user=self.other_user)
        self.factory = RequestFactory()

    def test_core_admin_pages_open(self):
        self.client.force_login(self.superuser)
        for name in ('core_project_changelist', 'core_banklabel_changelist',
                     'core_financeoperation_changelist'):
            response = self.client.get(reverse(f'admin:{name}'))
            self.assertEqual(response.status_code, 200)

    def test_staff_sees_only_own_projects(self):
        request = self.factory.get('/admin/core/project/')
        request.user = self.staff_user
        model_admin = ProjectAdmin(Project, admin.site)

        self.assertQuerySetEqual(
            model_admin.get_queryset(request),
            [self.staff_project],
        )

    def test_sourced_operation_cannot_be_deleted_from_admin(self):
        operation = FinanceOperation.objects.create(
            date=date(2024, 5, 1), movement_type=FinanceType.EXPENSE,
            project=self.staff_project, amount=Decimal('100.00'),
            user=self.staff_user,
            source_content_type=ContentType.objects.get_for_model(Project),
            source_object_id=self.staff_project.pk,
        )
        request = self.factory.get('/admin/core/financeoperation/')
        request.user = self.superuser
        model_admin = FinanceOperationAdmin(FinanceOperation, admin.site)

        self.assertFalse(model_admin.has_delete_permission(request, operation))
