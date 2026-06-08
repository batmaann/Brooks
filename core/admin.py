from django import forms
from django.contrib import admin
from django.db import models
from django.db.models import Count
from django.utils.html import format_html

admin.site.site_header = 'Brooks — управление финансами'
admin.site.site_title = 'Brooks Admin'
admin.site.index_title = 'Управление приложениями'

from core.models import BankLabel, FinanceOperation, FinanceType, Project


class UserOwnedAdminMixin:
    """Limit staff users to their own finance records."""

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(user=request.user)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if not request.user.is_superuser and 'user' not in readonly_fields:
            readonly_fields.append('user')
        return readonly_fields

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        initial.setdefault('user', request.user.pk)
        return initial

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            obj.user = request.user
        super().save_model(request, obj, form, change)


@admin.register(Project)
class ProjectAdmin(UserOwnedAdminMixin, admin.ModelAdmin):
    list_display = (
        'name', 'user', 'is_active', 'operation_count',
        'started_at', 'finished_at', 'updated_at',
    )
    list_filter = ('is_active', 'started_at', 'finished_at')
    search_fields = ('name', 'slug', 'description', 'user__username')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')
    list_select_related = ('user',)
    list_per_page = 50
    save_on_top = True
    fieldsets = (
        ('Проект', {'fields': ('name', 'slug', 'description', 'user')}),
        ('Период и состояние', {
            'fields': ('started_at', 'finished_at', 'is_active'),
        }),
        ('Служебная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            _operation_count=Count('finance_operations'),
        )

    @admin.display(description='Операций', ordering='_operation_count')
    def operation_count(self, obj):
        return obj._operation_count


@admin.register(BankLabel)
class BankLabelAdmin(UserOwnedAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'user', 'color_preview', 'icon', 'is_active', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'slug', 'description', 'user__username')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at', 'color_preview')
    list_select_related = ('user',)
    list_per_page = 50
    save_on_top = True
    fieldsets = (
        ('Метка', {'fields': ('name', 'slug', 'user', 'description')}),
        ('Оформление', {'fields': ('color', 'color_preview', 'icon', 'is_active')}),
        ('Служебная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Цвет', ordering='color')
    def color_preview(self, obj):
        if not obj or not obj.color:
            return '—'
        style = f'display:inline-block;width:1.2rem;height:1.2rem;border-radius:3px;background:{obj.color};vertical-align:middle;'
        return format_html('<span style="{}"></span> {}', style, obj.color)


@admin.register(FinanceOperation)
class FinanceOperationAdmin(UserOwnedAdminMixin, admin.ModelAdmin):
    list_display = (
        'date', 'month_display', 'quarter_display', 'movement_type',
        'project', 'formatted_amount', 'bank_label', 'source_display', 'user',
    )
    list_filter = (
        'movement_type', 'date', 'quarter', 'month', 'project', 'bank_label',
    )
    search_fields = (
        'project__name', 'comment', 'bank_label__name', 'user__username',
    )
    date_hierarchy = 'date'
    ordering = ('-date', '-created_at')
    list_select_related = (
        'project', 'bank_label', 'user', 'source_content_type',
    )
    readonly_fields = (
        'month', 'quarter', 'source_display', 'source_content_type',
        'source_object_id', 'created_at', 'updated_at',
    )
    list_per_page = 100
    save_on_top = True
    fieldsets = (
        ('Операция', {
            'fields': ('date', 'movement_type', 'project', 'amount', 'user'),
        }),
        ('Дополнительно', {'fields': ('bank_label', 'comment')}),
        ('Расчётный период', {
            'fields': ('month', 'quarter'),
            'classes': ('collapse',),
        }),
        ('Связанная запись', {
            'fields': ('source_display', 'source_content_type', 'source_object_id'),
            'classes': ('collapse',),
        }),
        ('Служебная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    formfield_overrides = {
        models.DecimalField: {
            'widget': forms.NumberInput(attrs={'min': '0.01', 'step': '0.01'}),
        },
        models.TextField: {
            'widget': forms.Textarea(attrs={'rows': 4}),
        },
    }

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj and obj.source_content_type_id:
            readonly_fields.extend(('date', 'movement_type', 'project', 'amount', 'user'))
        return tuple(dict.fromkeys(readonly_fields))

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if not request.user.is_superuser:
            if db_field.name == 'project':
                kwargs['queryset'] = Project.objects.filter(user=request.user, is_active=True)
            elif db_field.name == 'bank_label':
                kwargs['queryset'] = BankLabel.objects.filter(user=request.user, is_active=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def has_delete_permission(self, request, obj=None):
        if obj and obj.source_content_type_id:
            return False
        return super().has_delete_permission(request, obj)

    def get_actions(self, request):
        actions = super().get_actions(request)
        actions.pop('delete_selected', None)
        return actions

    @admin.display(description='Месяц', ordering='month')
    def month_display(self, obj):
        return obj.get_month_display()

    @admin.display(description='Квартал', ordering='quarter')
    def quarter_display(self, obj):
        return obj.get_quarter_display()

    @admin.display(description='Сумма, RUB', ordering='amount')
    def formatted_amount(self, obj):
        color = '#b91c1c' if obj.movement_type == FinanceType.EXPENSE else '#15803d'
        sign = '−' if obj.movement_type == FinanceType.EXPENSE else '+'
        amount = f'{obj.amount:,.2f}'.replace(',', ' ').replace('.', ',')
        return format_html('<strong style="color:{}">{}{} ₽</strong>', color, sign, amount)

    @admin.display(description='Источник')
    def source_display(self, obj):
        if not obj or not obj.source_content_type_id:
            return 'Вручную'
        source = obj.source
        if source is None:
            return f'{obj.source_content_type} #{obj.source_object_id} (удалён)'
        return f'{obj.source_content_type} #{obj.source_object_id}: {source}'
