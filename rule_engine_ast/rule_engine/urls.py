# from django.urls import path
# from . import views

# urlpatterns = [
#     path('rules/', views.get_rules_view, name='list_rules'),  # GET
#     path('rules/create/', views.create_rule_view, name='create_rule'),  # POST
#     path('rules/combine/', views.combine_rules_view, name='combine_rules'),  # POST
#     path('rules/evaluate/', views.evaluate_rule_view, name='evaluate_rule'),  # POST
#     path('rules/<int:rule_id>/update/', views.update_rule_view, name='update_rule'),  # PUT
# ]




from django.urls import path
from . import views

urlpatterns = [
    path('rules/', views.rules_list_create_view, name='rules_list_create'),
    path('rules/<int:rule_id>/', views.rule_detail_view, name='rule_detail'),
    path('rules/combine/', views.combine_rules_view, name='combine_rules'),
    path('rules/evaluate/', views.evaluate_rule_view, name='evaluate_rule'),
]
