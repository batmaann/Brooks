from django.contrib import admin
from expenses import models


@admin.register(models.ExpenseCategory)
class ExpenseCategory(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'slug')


@admin.register(models.Expense)
class Expense(admin.ModelAdmin):
    list_display = ('date', 'category', 'amount', 'user', 'source_app', 'source_model', 'source_id')
    list_filter = ('category', 'date')
    search_fields = ('description', 'category__name', 'user__username')
