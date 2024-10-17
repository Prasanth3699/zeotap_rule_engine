from django.db import models
from rule_engine_core.rule_functions import create_rule, ast_to_json
from rule_engine_core.rule_functions import ParseError, TokenizationError
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

class Rule(models.Model):
    name = models.CharField(max_length=100, unique=True)
    rule_string = models.TextField()
    ast_json = models.JSONField(null=True, blank=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        # Validate rule_string before saving
        try:
            ast = create_rule(self.rule_string)
            if ast is None:
                raise ValidationError("Rule string cannot be empty.")
        except (ParseError, TokenizationError) as e:
            raise ValidationError(f"Invalid rule string: {e}")

    def save(self, *args, **kwargs):
        if not self.rule_string.strip():
            raise ValidationError("Rule string cannot be empty or just whitespace.")

        self.full_clean()
        try:
            with transaction.atomic():
                ast = create_rule(self.rule_string)
                self.ast_json = ast_to_json(ast)
                super().save(*args, **kwargs)
        except ValidationError as ve:
            raise ve
        except Exception as e:
            raise ValidationError(f"Error saving rule: {e}")



    def __str__(self):
        return self.name

    class Meta:
        indexes = [
            models.Index(fields=['name']),
        ]