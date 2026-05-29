from rest_framework import serializers
from expenses import models


class ExpenseCategory(serializers.ModelSerializer):
    class Meta:
        model = models.ExpenseCategory
        fields = '__all__'


class Expense(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    source_app = serializers.CharField(read_only=True)
    source_model = serializers.CharField(read_only=True)
    source_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.Expense
        fields = '__all__'
        read_only_fields = ['user', 'source_app', 'source_model', 'source_id', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
