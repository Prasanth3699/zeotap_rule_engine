from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Rule
from .serializers import RuleSerializer, CombineRulesSerializer, EvaluateRuleSerializer
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from rule_engine_core.rule_functions import ast_to_json, json_to_ast
import logging

logger = logging.getLogger(__name__)

@api_view(['GET', 'POST'])
def rules_list_create_view(request):
    """
    GET: List all rules with pagination.
    POST: Create a new rule.
    """
    if request.method == 'GET':
        rules = Rule.objects.all().order_by('-created_at')
        paginator = PageNumberPagination()
        paginator.page_size = 10  # Adjust as needed
        result_page = paginator.paginate_queryset(rules, request)
        serializer = RuleSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    elif request.method == 'POST':
        serializer = RuleSerializer(data=request.data)
        if serializer.is_valid():
            print(serializer)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['PUT', 'PATCH', 'DELETE'])
def rule_detail_view(request, rule_id):
    """
    Update or delete a rule.
    """
    rule = get_object_or_404(Rule, id=rule_id)

    if request.method in ['PUT', 'PATCH']:
        serializer = RuleSerializer(rule, data=request.data, partial=True)  # Allow partial updates
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        rule.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



@api_view(['POST'])
def combine_rules_view(request):
    serializer = CombineRulesSerializer(data=request.data)
    if serializer.is_valid():
        try:
            # Save and get the combined object
            combined = serializer.save()
            print(f"Combined object: {combined}")  # Debugging line

            # Ensure 'combined_ast' is a Node object, not a dict
            combined_ast = combined.get('combined_ast')
            if isinstance(combined_ast, dict):
                # Convert the dict back into a Node object, if necessary
                combined_ast = json_to_ast(combined_ast)

            # Now convert the valid Node object to JSON
            combined_ast_json = ast_to_json(combined_ast)
            new_rule_id = combined.get('new_rule_id')

            return Response({
                'combined_ast': combined_ast_json,
                'new_rule_id': new_rule_id
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error combining rules: {e}", exc_info=True)
            return Response(
                {"error": "An unexpected error occurred while combining rules."}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





@api_view(['POST'])
def evaluate_rule_view(request):
    """
    POST: Evaluate a rule against user data.
    """
    serializer = EvaluateRuleSerializer(data=request.data)
    if serializer.is_valid():
        evaluation = serializer.save()
        return Response({
            'result': evaluation['result'],
            'details': evaluation['details']
        }, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
