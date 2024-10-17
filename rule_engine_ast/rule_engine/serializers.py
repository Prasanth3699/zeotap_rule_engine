from rest_framework import serializers
from .models import Rule
from rule_engine_core.rule_functions import ParseError, TokenizationError, EvaluationError
from rule_engine_core.rule_functions import ast_to_json, json_to_ast, combine_rules
from rule_engine_core.rule_functions import evaluate_rule, create_rule, evaluate_rule_with_details
from rule_engine_core.parser import VALID_ATTRIBUTES

class RuleSerializer(serializers.ModelSerializer):
    ast_json = serializers.JSONField(required=False)

    class Meta:
        model = Rule
        fields = ['id', 'name', 'rule_string', 'ast_json', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, data):
        """
        Validate the rule string or ast_json.
        """
        if 'rule_string' in data:
            
            try:
                ast = create_rule(data['rule_string'])
                if ast is None:
                    raise serializers.ValidationError({"rule_string": "Rule string cannot be empty."})
            except (ParseError, TokenizationError) as e:
                raise serializers.ValidationError({"rule_string": f"Invalid rule string: {e}"})
        elif 'ast_json' in data:

            try:
                ast = json_to_ast(data['ast_json'])
                if ast is None:
                    raise serializers.ValidationError({"ast_json": "AST cannot be empty."})
            except EvaluationError as e:
                raise serializers.ValidationError({"ast_json": f"Invalid AST: {e}"})
        else:
            raise serializers.ValidationError("Either rule_string or ast_json must be provided.")
        return data

    def create(self, validated_data):
        rule_string = validated_data.get('rule_string')

        if rule_string:
            ast = create_rule(rule_string)
            validated_data['ast_json'] = ast_to_json(ast)
        else:
            raise serializers.ValidationError({"rule_string": "This field cannot be blank."})

        return super().create(validated_data)


    def update(self, instance, validated_data):
        # Apply the updates to the instance
        instance.name = validated_data.get('name', instance.name)
        instance.rule_string = validated_data.get('rule_string', instance.rule_string)

        # Regenerate the AST from the new rule string
        try:
            ast = create_rule(instance.rule_string)
            instance.ast_json = ast_to_json(ast)
        except Exception as e:
            raise serializers.ValidationError({"error": f"Failed to generate AST: {e}"})

        instance.save()
        return instance




class CombineRulesSerializer(serializers.Serializer):
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
    name = serializers.CharField(write_only=True, required=True, help_text="Name for the combined rule.")
    combined_ast = serializers.SerializerMethodField(read_only=True)
    new_rule_id = serializers.IntegerField(read_only=True)

    def validate_rule_ids(self, value):
        """Ensure all provided rule IDs exist."""
        if not value:
            raise serializers.ValidationError("At least one rule ID must be provided.")
        
        # Get existing IDs from the database
        existing_ids = set(Rule.objects.filter(id__in=value).values_list('id', flat=True))
        missing_ids = set(value) - existing_ids
        
        if missing_ids:
            raise serializers.ValidationError(f"Rule IDs not found: {', '.join(map(str, missing_ids))}")
        return value

    def create(self, validated_data):
        rule_ids = validated_data['rule_ids']
        operator = validated_data.get('operator', 'OR')
        name = validated_data['name']

        # Fetch the rules from the database
        rules = Rule.objects.filter(id__in=rule_ids)

        # Combine the rule strings into a valid expression
        rule_expressions = [f"({rule.rule_string})" for rule in rules]
        combined_rule_string = f" {operator} ".join(rule_expressions)

        try:
            # Combine the ASTs of the rules
            rule_strings = [rule.rule_string for rule in rules]
            combined_ast = combine_rules(rule_strings, operator=operator)

            # Create a new rule with the combined string and AST
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
            print(f"Error combining rules: {e}")
            raise serializers.ValidationError({"error": "An unexpected error occurred while combining rules."})


class EvaluateRuleSerializer(serializers.Serializer):
    rule_id = serializers.IntegerField(required=True)
    user_data = serializers.DictField(required=True)

    result = serializers.BooleanField(read_only=True)
    details = serializers.DictField(read_only=True)

    def validate_rule_id(self, value):
        """
        Ensure the rule exists.
        """
        if not Rule.objects.filter(id=value).exists():
            raise serializers.ValidationError(f"Rule with ID {value} does not exist.")
        return value

    def validate_user_data(self, value):
        """
        Ensure user data contains valid attributes.
        """
        

        invalid_attrs = set(value.keys()) - VALID_ATTRIBUTES
        if invalid_attrs:
            raise serializers.ValidationError(f"Invalid attributes in user data: {', '.join(invalid_attrs)}")
        return value

    def create(self, validated_data):
        """
        Evaluate the rule against the user data.
        """
        

        rule_id = validated_data['rule_id']
        user_data = validated_data['user_data']

        rule = Rule.objects.get(id=rule_id)
        ast = json_to_ast(rule.ast_json)
        try:
            result, details = evaluate_rule_with_details(ast, user_data)
        except EvaluationError as e:
            raise serializers.ValidationError(f"Error during evaluation: {e}")

        return {'result': result, 'details': details}



