from django.urls import path
from . import views

urlpatterns = [
    path('rules/', views.rules_list_create_view, name='rules_list_create'),
    path('rules/<int:rule_id>/', views.rule_detail_view, name='rule_detail'),
    path('rules/combine/', views.combine_rules_view, name='combine_rules'),
    path('rules/evaluate/', views.evaluate_rule_view, name='evaluate_rule'),
]
