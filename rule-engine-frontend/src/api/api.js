import axios from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1/";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000, // Increased timeout for better reliability
});

// Fetch rules with optional URL for pagination
export const getRules = (url = "rules/") => apiClient.get(url);

// Other API functions remain unchanged
export const createRule = (name, ruleString) =>
  apiClient.post("rules/", { name, rule_string: ruleString });
export const updateRule = (ruleId, updatedFields) =>
  apiClient.put(`rules/${ruleId}/`, updatedFields);
export const deleteRule = (ruleId) => apiClient.delete(`rules/${ruleId}/`);
export const combineRules = (ruleIds, operator = "OR", name) =>
  apiClient.post("rules/combine/", { rule_ids: ruleIds, operator, name });
export const evaluateRule = (ruleId, userData) =>
  apiClient.post("rules/evaluate/", { rule_id: ruleId, user_data: userData });

export default apiClient;
