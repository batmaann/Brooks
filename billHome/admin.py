from django.contrib import admin

from billHome import models


class ChargeInline(admin.TabularInline):
    model = models.Charge
    extra = 0
    fields = (
        "service",
        "source_name",
        "scope",
        "quantity",
        "unit",
        "tariff",
        "amount_due",
    )
    autocomplete_fields = ("service",)


class PaymentInline(admin.TabularInline):
    model = models.Payment
    extra = 0
    fields = ("paid_at", "amount", "note")


@admin.register(models.UtilityDocument)
class UtilityDocumentAdmin(admin.ModelAdmin):
    list_display = (
        "billing_period",
        "provider",
        "document_number",
        "issued_at",
        "due_at",
        "amount_due",
    )
    list_filter = ("billing_period", "provider")
    search_fields = ("provider", "document_number", "notes", "source_hash")
    date_hierarchy = "billing_period"
    readonly_fields = ("created_at", "updated_at")
    inlines = (ChargeInline, PaymentInline)


@admin.register(models.UtilityService)
class UtilityServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "default_unit", "is_optional")
    list_filter = ("category", "is_optional")
    search_fields = ("name",)
    list_editable = ("category", "default_unit", "is_optional")


@admin.register(models.Charge)
class ChargeAdmin(admin.ModelAdmin):
    list_display = (
        "document",
        "service",
        "scope",
        "calculation_method",
        "quantity",
        "unit",
        "tariff",
        "amount_due",
    )
    list_filter = ("scope", "calculation_method", "service__category")
    search_fields = (
        "source_name",
        "service__name",
        "document__provider",
        "document__document_number",
    )
    autocomplete_fields = ("document", "service")
    list_select_related = ("document", "service")


@admin.register(models.Meter)
class MeterAdmin(admin.ModelAdmin):
    list_display = (
        "service",
        "serial_number",
        "kind",
        "unit",
        "verification_due_at",
        "active",
    )
    list_filter = ("kind", "active", "service__category")
    search_fields = ("serial_number", "service__name", "notes")
    autocomplete_fields = ("service",)
    list_select_related = ("service",)


@admin.register(models.MeterReading)
class MeterReadingAdmin(admin.ModelAdmin):
    list_display = (
        "reading_date",
        "meter",
        "tariff_zone",
        "previous_value",
        "current_value",
        "consumption",
        "document",
    )
    list_filter = ("reading_date", "meter__service__category")
    search_fields = (
        "meter__serial_number",
        "meter__service__name",
        "tariff_zone",
        "document__provider",
    )
    date_hierarchy = "reading_date"
    autocomplete_fields = ("meter", "document")
    list_select_related = ("meter", "meter__service", "document")


@admin.register(models.Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("paid_at", "amount", "document", "note", "created_at")
    list_filter = ("paid_at",)
    search_fields = (
        "note",
        "document__provider",
        "document__document_number",
    )
    date_hierarchy = "paid_at"
    autocomplete_fields = ("document",)
    list_select_related = ("document",)
    readonly_fields = ("created_at",)
