from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Rule
from .serializers import RuleSerializer, CombineRulesSerializer, EvaluateRuleSerializer
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from rule_engine_core.rule_functions import ast_to_json, json_to_ast
import logging

# Configure logging for the module
logger = logging.getLogger(__name__)

@api_view(['GET', 'POST'])
def rules_list_create_view(request):
    """
    View to list all rules or create a new rule.

    **GET**:
    - Retrieves a paginated list of all rules.
    - Returns HTTP 200 OK with serialized data.

    **POST**:
    - Creates a new rule with the provided data.
    - Returns HTTP 201 Created with serialized data.
    """
    if request.method == 'GET':
        # Retrieve all Rule objects, ordered by creation date (most recent first)
        rules = Rule.objects.all().order_by('-created_at')

        # Initialize the paginator and set the page size
        paginator = PageNumberPagination()
        paginator.page_size = 10  # Adjust the page size as needed

        # Paginate the queryset based on the request
        result_page = paginator.paginate_queryset(rules, request)

        # Serialize the paginated data
        serializer = RuleSerializer(result_page, many=True)

        # Return the paginated response with serialized data
        return paginator.get_paginated_response(serializer.data)

    elif request.method == 'POST':
        # Create a serializer instance with the request data
        serializer = RuleSerializer(data=request.data)

        # Validate the serializer data
        if serializer.is_valid():
            print(serializer)  # Debugging line; consider removing or replacing with logging
            # Save the new Rule instance
            serializer.save()
            # Return the serialized data with HTTP 201 Created status
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            # Return validation errors with HTTP 400 Bad Request status
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT', 'PATCH', 'DELETE'])
def rule_detail_view(request, rule_id):
    """
    View to update or delete a specific rule.

    **PUT/PATCH**:
    - Updates the specified rule with the provided data.
    - Allows partial updates if using PATCH.
    - Returns HTTP 200 OK with serialized data.

    **DELETE**:
    - Deletes the specified rule.
    - Returns HTTP 204 No Content.
    """
    # Retrieve the Rule object by ID or return 404 if not found
    rule = get_object_or_404(Rule, id=rule_id)

    if request.method in ['PUT', 'PATCH']:
        # Create a serializer instance with the existing Rule and request data
        serializer = RuleSerializer(rule, data=request.data, partial=True)  # `partial=True` allows partial updates

        # Validate the serializer data
        if serializer.is_valid():
            # Save the updated Rule instance
            serializer.save()
            # Return the serialized data with HTTP 200 OK status
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # Return validation errors with HTTP 400 Bad Request status
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Delete the Rule instance from the database
        rule.delete()
        # Return HTTP 204 No Content status
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
def combine_rules_view(request):
    """
    View to combine multiple rules into a new rule.

    **POST**:
    - Accepts a list of rule IDs and a logical operator ('AND' or 'OR').
    - Combines the rules into a single rule using the specified operator.
    - Returns the combined AST (Abstract Syntax Tree) and the ID of the new rule.
    - Returns HTTP 200 OK with combined data.
    """
    # Create a serializer instance with the request data
    serializer = CombineRulesSerializer(data=request.data)

    # Validate the serializer data
    if serializer.is_valid():
        try:
            # Save the combined rule and retrieve the result
            combined = serializer.save()
            print(f"Combined object: {combined}")  # Debugging line; consider removing or replacing with logging

            # Extract the combined AST from the result
            combined_ast = combined.get('combined_ast')
            if isinstance(combined_ast, dict):
                # Convert the dictionary back to a Node object if necessary
                combined_ast = json_to_ast(combined_ast)

            # Convert the Node object to JSON format
            combined_ast_json = ast_to_json(combined_ast)
            new_rule_id = combined.get('new_rule_id')

            # Return the combined AST and new rule ID with HTTP 200 OK status
            return Response({
                'combined_ast': combined_ast_json,
                'new_rule_id': new_rule_id
            }, status=status.HTTP_200_OK)

        except Exception as e:
            # Log the exception details
            logger.error(f"Error combining rules: {e}", exc_info=True)
            # Return a generic error message with HTTP 500 Internal Server Error status
            return Response(
                {"error": "An unexpected error occurred while combining rules."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    else:
        # Return validation errors with HTTP 400 Bad Request status
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def evaluate_rule_view(request):
    """
    View to evaluate a rule against provided user data.

    **POST**:
    - Accepts a rule ID and user data in JSON format.
    - Evaluates the rule using the provided user data.
    - Returns the evaluation result (True or False) and details of the evaluation.
    - Returns HTTP 200 OK with evaluation results.
    """
    # Create a serializer instance with the request data
    serializer = EvaluateRuleSerializer(data=request.data)

    # Validate the serializer data
    if serializer.is_valid():
        # Perform the evaluation and retrieve the result
        evaluation = serializer.save()
        # Return the evaluation result and details with HTTP 200 OK status
        return Response({
            'result': evaluation['result'],
            'details': evaluation['details']
        }, status=status.HTTP_200_OK)
    else:
        # Return validation errors with HTTP 400 Bad Request status
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
