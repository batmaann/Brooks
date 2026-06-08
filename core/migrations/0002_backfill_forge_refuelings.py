from decimal import Decimal

from django.db import migrations


FORGE_PROJECT_SLUG = 'forge'


def backfill_forge_refuelings(apps, schema_editor):
    ContentType = apps.get_model('contenttypes', 'ContentType')
    FinanceOperation = apps.get_model('core', 'FinanceOperation')
    Project = apps.get_model('core', 'Project')
    Refueling = apps.get_model('forge', 'Refueling')

    source_content_type, _ = ContentType.objects.get_or_create(
        app_label='forge', model='refueling',
    )

    for refueling in Refueling.objects.select_related('vehicle').iterator():
        amount = (refueling.total_cost or Decimal('0')) - (refueling.discount or Decimal('0'))
        if amount <= 0:
            continue

        project = Project.objects.filter(
            user_id=refueling.user_id,
            slug=FORGE_PROJECT_SLUG,
        ).first()
        if project is None:
            project = Project.objects.create(
                user_id=refueling.user_id,
                name='Forge',
                slug=FORGE_PROJECT_SLUG,
                description='Расходы на транспорт, рассчитанные приложением Forge.',
            )

        FinanceOperation.objects.update_or_create(
            user_id=refueling.user_id,
            source_content_type_id=source_content_type.pk,
            source_object_id=refueling.pk,
            defaults={
                'date': refueling.date,
                'month': refueling.date.month,
                'quarter': ((refueling.date.month - 1) // 3) + 1,
                'movement_type': 'expense',
                'project_id': project.pk,
                'amount': amount,
                'comment': f'Заправка: {refueling.vehicle}',
            },
        )


def remove_backfilled_operations(apps, schema_editor):
    ContentType = apps.get_model('contenttypes', 'ContentType')
    FinanceOperation = apps.get_model('core', 'FinanceOperation')
    source_content_type = ContentType.objects.filter(
        app_label='forge', model='refueling',
    ).first()
    if source_content_type:
        FinanceOperation.objects.filter(source_content_type_id=source_content_type.pk).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0001_initial'),
        ('forge', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(backfill_forge_refuelings, remove_backfilled_operations),
    ]
