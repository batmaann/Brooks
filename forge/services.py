from django.contrib.contenttypes.models import ContentType

from core.models import FinanceOperation, FinanceType, Project


FORGE_PROJECT_SLUG = 'forge'


def get_forge_project(user):
    project = Project.objects.filter(user=user, slug=FORGE_PROJECT_SLUG).first()
    if project is None:
        project = Project.objects.filter(user=user, name__iexact='Forge').first()
    if project is not None:
        return project
    return Project.objects.create(
        user=user,
        name='Forge',
        slug=FORGE_PROJECT_SLUG,
        description='Расходы на транспорт, рассчитанные приложением Forge.',
    )


def sync_refueling_finance_operation(refueling):
    """Create or update the core expense represented by a refueling."""
    source_content_type = ContentType.objects.get_for_model(
        refueling,
        for_concrete_model=False,
    )
    FinanceOperation.objects.update_or_create(
        user=refueling.user,
        source_content_type=source_content_type,
        source_object_id=refueling.pk,
        defaults={
            'date': refueling.date,
            'movement_type': FinanceType.EXPENSE,
            'project': get_forge_project(refueling.user),
            'amount': refueling.total_cost,
            'comment': f'Заправка: {refueling.vehicle}',
        },
    )


def delete_refueling_finance_operation(refueling):
    source_content_type = ContentType.objects.get_for_model(
        refueling,
        for_concrete_model=False,
    )
    FinanceOperation.objects.filter(
        user_id=refueling.user_id,
        source_content_type=source_content_type,
        source_object_id=refueling.pk,
    ).delete()
