from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import Rule

class RuleAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.rule1 = Rule.objects.create(
            name="Rule 1",
            rule_string="age > 30 AND department = 'Sales'"
        )
        self.rule2 = Rule.objects.create(
            name="Rule 2",
            rule_string="age < 25 AND department = 'Marketing'"
        )
        self.valid_user_data = {
            "age": 35,
            "department": "Sales",
            "salary": 60000,
            "experience": 3
        }
        self.invalid_user_data = {
            "age": "thirty-five",
            "department": "Sales",
            "salary": 60000,
            "experience": 3,
            "invalid_attr": "test"
        }

    def test_create_rule(self):
        url = reverse('rules_list_create')
        data = {
            "name": "Rule 3",
            "rule_string": "salary > 50000 OR experience > 5"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Rule.objects.count(), 3)
        self.assertEqual(Rule.objects.get(id=response.data['id']).name, "Rule 3")

    def test_create_rule_invalid(self):
        url = reverse('rules_list_create')
        data = {
            "name": "Rule Invalid",
            "rule_string": "invalid syntax here"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('rule_string', response.data)

    def test_list_rules(self):
        url = reverse('rules_list_create')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  

    def test_update_rule(self):
        url = reverse('rule_detail', args=[self.rule1.id])
        data = {
            "rule_string": "age >= 35 AND department = 'Sales'"
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_rule = Rule.objects.get(id=self.rule1.id)
        self.assertEqual(updated_rule.rule_string, "age >= 35 AND department = 'Sales'")

    def test_delete_rule(self):
        url = reverse('rule_detail', args=[self.rule2.id])
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Rule.objects.count(), 1)

    def test_combine_rules(self):
        url = reverse('combine_rules')
        data = {
            "rule_ids": [self.rule1.id, self.rule2.id],
            "operator": "OR" ,
             "name": "Combined Rule Test"
        }
        response = self.client.post(url, data, format='json')
        if response.status_code != status.HTTP_200_OK:
            print("Response data:", response.data)  # Add this line to debug
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('combined_ast', response.data)

    def test_combine_rules_invalid_operator(self):
        url = reverse('combine_rules')
        data = {
            "rule_ids": [self.rule1.id, self.rule2.id],
            "operator": "NOT"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('operator', response.data)

    def test_evaluate_rule_success(self):
        url = reverse('evaluate_rule')
        data = {
            "rule_id": self.rule1.id,
            "user_data": self.valid_user_data
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['result'])

    def test_evaluate_rule_failure(self):
        url = reverse('evaluate_rule')
        data = {
            "rule_id": self.rule1.id,
            "user_data": {
                "age": 25,
                "department": "HR",
                "salary": 40000,
                "experience": 2
            }
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['result'])

    def test_evaluate_rule_invalid_user_data(self):
        url = reverse('evaluate_rule')
        data = {
            "rule_id": self.rule1.id,
            "user_data": self.invalid_user_data
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('user_data', response.data)

    def test_evaluate_rule_missing_rule(self):
        url = reverse('evaluate_rule')
        data = {
            "rule_id": 999,  # Non-existent rule ID
            "user_data": self.valid_user_data
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('rule_id', response.data)
