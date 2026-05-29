from django.db.models import Sum
from expenses import filters, models, serializers
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet


class ExpenseCategory(ModelViewSet):
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)
    queryset = models.ExpenseCategory.objects.all()
    serializer_class = serializers.ExpenseCategory


class Expense(ModelViewSet):
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.Expense
    filterset_class = filters.Expense

    def get_queryset(self):
        return models.Expense.objects.filter(user=self.request.user).select_related('category')

    @action(detail=False, methods=['get'])
    def summary(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        data = queryset.values('date', 'category__slug', 'category__name').annotate(
            total_amount=Sum('amount'),
        ).order_by('-date', 'category__name')
        return Response(data)
