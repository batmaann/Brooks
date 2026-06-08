from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from core.models import FinanceOperation, FinanceType, Project
from forge.models import Refueling


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


@receiver(post_save, sender=Refueling)
def sync_refueling_finance_operation(sender, instance, **kwargs):
    source_content_type = ContentType.objects.get_for_model(Refueling, for_concrete_model=False)
    lookup = {
        'user': instance.user,
        'source_content_type': source_content_type,
        'source_object_id': instance.pk,
    }
    if instance.effective_cost <= 0:
        FinanceOperation.objects.filter(**lookup).delete()
        return

    FinanceOperation.objects.update_or_create(
        **lookup,
        defaults={
            'date': instance.date,
            'movement_type': FinanceType.EXPENSE,
            'project': get_forge_project(instance.user),
            'amount': instance.effective_cost,
            'comment': f'Заправка: {instance.vehicle}',
        },
    )


@receiver(post_delete, sender=Refueling)
def delete_refueling_finance_operation(sender, instance, **kwargs):
    source_content_type = ContentType.objects.get_for_model(Refueling, for_concrete_model=False)
    FinanceOperation.objects.filter(
        user=instance.user,
        source_content_type=source_content_type,
        source_object_id=instance.pk,
    ).delete()
