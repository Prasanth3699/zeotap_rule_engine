import { useState, useEffect } from "react";
import { getRules, combineRules } from "../services/api";
import { AiOutlineCheckCircle, AiOutlineCloseCircle } from "react-icons/ai"; // Icons

function CombineRulesComponent() {
  const [rules, setRules] = useState([]);
  const [selectedRuleIds, setSelectedRuleIds] = useState([]);
  const [operator, setOperator] = useState("OR");
  const [name, setName] = useState("");
  const [combinedAst, setCombinedAst] = useState(null);
  const [newRuleId, setNewRuleId] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchRules();
  }, []);

  const fetchRules = async () => {
    try {
      setLoading(true);
      const response = await getRules();
      setRules(response.data.results);
    } catch (err) {
      setError("Failed to fetch rules.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleRuleSelection = (ruleId) => {
    setSelectedRuleIds((prevSelected) =>
      prevSelected.includes(ruleId)
        ? prevSelected.filter((id) => id !== ruleId)
        : [...prevSelected, ruleId]
    );
  };

  const handleCombine = async () => {
    if (selectedRuleIds.length < 2) {
      setError("Select at least two rules to combine.");
      return;
    }
    if (!name.trim()) {
      setError("Please provide a name for the combined rule.");
      return;
    }

    try {
      setLoading(true);
      const response = await combineRules(
        selectedRuleIds,
        operator,
        name.trim()
      );
      setCombinedAst(response.data.combined_ast);
      setNewRuleId(response.data.new_rule_id);
      setError("");
      setSelectedRuleIds([]);
      setOperator("OR");
      setName("");
      fetchRules(); // Refresh the rules list
    } catch (err) {
      if (err.response && err.response.data) {
        setError(Object.values(err.response.data).join(" "));
      } else {
        setError("Failed to combine rules.");
      }
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto p-8 mt-10 bg-white rounded-lg shadow-lg">
      <h2 className="text-3xl font-extrabold text-gray-800 mb-6">
        Combine Rules
      </h2>

      {error && (
        <div className="flex items-center text-red-600 bg-red-100 p-4 rounded mb-4">
          <AiOutlineCloseCircle className="mr-2" size={24} />
          <span>{error}</span>
        </div>
      )}

      {newRuleId && (
        <div className="flex items-center text-green-600 bg-green-100 p-4 rounded mb-4">
          <AiOutlineCheckCircle className="mr-2" size={24} />
          <span>Combined rule created successfully with ID: {newRuleId}</span>
        </div>
      )}

      <div className="mb-6">
        <label className="block mb-2 font-semibold">
          Select Rules to Combine
        </label>
        <div className="grid grid-cols-1 gap-3 max-h-60 overflow-y-auto border border-gray-300 p-4 rounded-lg">
          {rules.map((rule) => (
            <label key={rule.id} className="flex items-center space-x-3">
              <input
                type="checkbox"
                checked={selectedRuleIds.includes(rule.id)}
                onChange={() => handleRuleSelection(rule.id)}
                className="form-checkbox h-5 w-5 text-blue-600 rounded"
              />
              <span className="text-gray-700">{rule.name}</span>
            </label>
          ))}
        </div>
      </div>

      <div className="mb-6">
        <label className="block mb-2 font-semibold">Combine Operator</label>
        <select
          value={operator}
          onChange={(e) => setOperator(e.target.value)}
          className="w-full border border-gray-300 px-4 py-3 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="AND">AND</option>
          <option value="OR">OR</option>
        </select>
      </div>

      <div className="mb-6">
        <label className="block mb-2 font-semibold">Combined Rule Name</label>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Enter name for the combined rule"
          className="w-full border border-gray-300 px-4 py-3 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <button
        onClick={handleCombine}
        className={`w-full bg-green-500 text-white px-4 py-3 rounded-lg font-semibold transition-all duration-300 hover:bg-green-600 focus:outline-none focus:ring-2 focus:ring-green-500 ${
          loading || selectedRuleIds.length < 2 || !name.trim()
            ? "opacity-50 cursor-not-allowed"
            : ""
        }`}
        disabled={loading || selectedRuleIds.length < 2 || !name.trim()}
      >
        {loading ? "Combining..." : "Combine Rules"}
      </button>

      {combinedAst && (
        <div className="mt-8">
          <h3 className="text-xl font-bold text-gray-800 mb-2">
            Combined AST:
          </h3>
          <pre className="bg-gray-100 p-4 rounded-lg overflow-x-auto">
            {JSON.stringify(combinedAst, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}

export default CombineRulesComponent;
