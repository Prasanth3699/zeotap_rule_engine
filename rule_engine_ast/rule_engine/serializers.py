from rest_framework import serializers
from .models import Rule
from rule_engine_core.rule_functions import (
    ParseError,
    TokenizationError,
    EvaluationError,
    ast_to_json,
    json_to_ast,
    combine_rules,
    evaluate_rule,
    create_rule,
    evaluate_rule_with_details
)
from rule_engine_core.parser import VALID_ATTRIBUTES

class RuleSerializer(serializers.ModelSerializer):
    """
    Serializer for the Rule model.
    Handles validation and serialization of Rule instances.
    """
    ast_json = serializers.JSONField(required=False)

    class Meta:
        model = Rule
        fields = ['id', 'name', 'rule_string', 'ast_json', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, data):
        """
        Validate the rule string or AST JSON.

        Ensures that either 'rule_string' or 'ast_json' is provided and valid.
        Parses the rule string into an AST to verify its correctness.

        Args:
            data (dict): The data to validate.

        Returns:
            dict: The validated data.

        Raises:
            serializers.ValidationError: If validation fails.
        """
        if 'rule_string' in data:
            # Validate the rule string by attempting to parse it into an AST
            try:
                ast = create_rule(data['rule_string'])
                if ast is None:
                    raise serializers.ValidationError({"rule_string": "Rule string cannot be empty."})
            except (ParseError, TokenizationError) as e:
                raise serializers.ValidationError({"rule_string": f"Invalid rule string: {e}"})
        elif 'ast_json' in data:
            # Validate the AST JSON by attempting to reconstruct the AST
            try:
                ast = json_to_ast(data['ast_json'])
                if ast is None:
                    raise serializers.ValidationError({"ast_json": "AST cannot be empty."})
            except EvaluationError as e:
                raise serializers.ValidationError({"ast_json": f"Invalid AST: {e}"})
        else:
            # Neither 'rule_string' nor 'ast_json' provided
            raise serializers.ValidationError("Either 'rule_string' or 'ast_json' must be provided.")
        return data

    def create(self, validated_data):
        """
        Create a new Rule instance.

        Args:
            validated_data (dict): The validated data from the serializer.

        Returns:
            Rule: The newly created Rule instance.

        Raises:
            serializers.ValidationError: If 'rule_string' is missing or invalid.
        """
        rule_string = validated_data.get('rule_string')

        if rule_string:
            # Generate the AST from the rule string
            ast = create_rule(rule_string)
            # Serialize the AST to JSON for storage
            validated_data['ast_json'] = ast_to_json(ast)
        else:
            raise serializers.ValidationError({"rule_string": "This field cannot be blank."})

        # Call the superclass method to create the instance
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Update an existing Rule instance.

        Args:
            instance (Rule): The Rule instance to update.
            validated_data (dict): The validated data with updates.

        Returns:
            Rule: The updated Rule instance.

        Raises:
            serializers.ValidationError: If the updated 'rule_string' is invalid.
        """
        # Update the instance's fields with validated data
        instance.name = validated_data.get('name', instance.name)
        instance.rule_string = validated_data.get('rule_string', instance.rule_string)

        # Regenerate the AST from the updated rule string
        try:
            ast = create_rule(instance.rule_string)
            instance.ast_json = ast_to_json(ast)
        except Exception as e:
            raise serializers.ValidationError({"error": f"Failed to generate AST: {e}"})

        # Save the updated instance
        instance.save()
        return instance

class CombineRulesSerializer(serializers.Serializer):
    """
    Serializer to handle combining multiple rules into a new rule.

    Validates the input rule IDs and operator, combines the rules,
    and creates a new Rule instance with the combined AST.
    """
    rule_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=True,
        help_text="List of rule IDs to combine."
    )
    operator = serializers.ChoiceField(
        choices=['AND', 'OR'],
        default='OR',
        required=False,
        help_text="Logical operator to combine rules."
    )
    name = serializers.CharField(
        write_only=True,
        required=True,
        help_text="Name for the combined rule."
    )
    combined_ast = serializers.SerializerMethodField(read_only=True)
    new_rule_id = serializers.IntegerField(read_only=True)

    def validate_rule_ids(self, value):
        """
        Validate that all provided rule IDs exist in the database.

        Args:
            value (list): The list of rule IDs to validate.

        Returns:
            list: The validated list of rule IDs.

        Raises:
            serializers.ValidationError: If any rule IDs do not exist.
        """
        if not value:
            raise serializers.ValidationError("At least one rule ID must be provided.")

        # Fetch existing rule IDs from the database
        existing_ids = set(Rule.objects.filter(id__in=value).values_list('id', flat=True))
        missing_ids = set(value) - existing_ids

        if missing_ids:
            raise serializers.ValidationError(f"Rule IDs not found: {', '.join(map(str, missing_ids))}")
        return value

    def create(self, validated_data):
        """
        Combine the specified rules into a new rule.

        Args:
            validated_data (dict): The validated data containing rule IDs, operator, and name.

        Returns:
            dict: A dictionary containing the combined AST and new rule ID.

        Raises:
            serializers.ValidationError: If combining rules fails.
        """
        rule_ids = validated_data['rule_ids']
        operator = validated_data.get('operator', 'OR')
        name = validated_data['name']

        # Fetch the Rule instances from the database
        rules = Rule.objects.filter(id__in=rule_ids)

        # Create combined rule string by joining individual rule strings
        rule_expressions = [f"({rule.rule_string})" for rule in rules]
        combined_rule_string = f" {operator} ".join(rule_expressions)

        try:
            # Combine the ASTs of the individual rules
            rule_strings = [rule.rule_string for rule in rules]
            combined_ast = combine_rules(rule_strings, operator=operator)

            # Create a new Rule instance with the combined rule string and AST
            new_rule = Rule.objects.create(
                name=name,
                rule_string=combined_rule_string
            )
            new_rule.ast_json = ast_to_json(combined_ast)
            new_rule.save()

            return {
                'combined_ast': combined_ast,
                'new_rule_id': new_rule.id
            }
        except Exception as e:
            print(f"Error combining rules: {e}")  # Consider replacing with logging
            raise serializers.ValidationError({"error": "An unexpected error occurred while combining rules."})

class EvaluateRuleSerializer(serializers.Serializer):
    """
    Serializer to evaluate a rule against provided user data.

    Validates the rule ID and user data, then performs the evaluation.
    """
    rule_id = serializers.IntegerField(required=True)
    user_data = serializers.DictField(required=True)

    result = serializers.BooleanField(read_only=True)
    details = serializers.DictField(read_only=True)

    def validate_rule_id(self, value):
        """
        Ensure that the specified rule exists.

        Args:
            value (int): The rule ID to validate.

        Returns:
            int: The validated rule ID.

        Raises:
            serializers.ValidationError: If the rule does not exist.
        """
        if not Rule.objects.filter(id=value).exists():
            raise serializers.ValidationError(f"Rule with ID {value} does not exist.")
        return value

    def validate_user_data(self, value):
        """
        Validate that the user data contains only valid attributes.

        Args:
            value (dict): The user data to validate.

        Returns:
            dict: The validated user data.

        Raises:
            serializers.ValidationError: If invalid attributes are present.
        """
        # Identify any invalid attributes not in the allowed list
        invalid_attrs = set(value.keys()) - VALID_ATTRIBUTES
        if invalid_attrs:
            raise serializers.ValidationError(f"Invalid attributes in user data: {', '.join(invalid_attrs)}")
        return value

    def create(self, validated_data):
        """
        Evaluate the specified rule against the provided user data.

        Args:
            validated_data (dict): The validated data containing rule ID and user data.

        Returns:
            dict: A dictionary containing the evaluation result and details.

        Raises:
            serializers.ValidationError: If evaluation fails.
        """
        rule_id = validated_data['rule_id']
        user_data = validated_data['user_data']

        # Retrieve the Rule instance
        rule = Rule.objects.get(id=rule_id)
        # Reconstruct the AST from stored JSON
        ast = json_to_ast(rule.ast_json)
        try:
            # Evaluate the rule and collect details
            result, details = evaluate_rule_with_details(ast, user_data)
        except EvaluationError as e:
            raise serializers.ValidationError(f"Error during evaluation: {e}")

        return {'result': result, 'details': details}
