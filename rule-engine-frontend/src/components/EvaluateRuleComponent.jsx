import { useState, useEffect, useRef } from "react";
import { evaluateRule, getRules } from "../services/api";
import { AiOutlineCheckCircle, AiOutlineCloseCircle } from "react-icons/ai";
import { FiChevronDown } from "react-icons/fi";

function EvaluateRuleComponent() {
  const [rules, setRules] = useState([]);
  const [selectedRule, setSelectedRule] = useState(null);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [userData, setUserData] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const dropdownRef = useRef(null);

  useEffect(() => {
    fetchRules();
  }, []);

  const fetchRules = async () => {
    try {
      const response = await getRules();
      setRules(response.data.results || []);
    } catch (err) {
      setError("Failed to fetch rules.");
      console.error(err);
    }
  };

  const handleOutsideClick = (event) => {
    if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
      setIsDropdownOpen(false);
    }
  };

  useEffect(() => {
    document.addEventListener("mousedown", handleOutsideClick);
    return () => document.removeEventListener("mousedown", handleOutsideClick);
  }, []);

  const handleEvaluateRule = async (e) => {
    e.preventDefault();
    setError("");
    setResult(null);

    if (!selectedRule) {
      setError("Please select a rule to evaluate.");
      return;
    }

    try {
      const parsedUserData = JSON.parse(userData);
      setLoading(true);
      const response = await evaluateRule(selectedRule.id, parsedUserData);
      setResult(response.data.result);
    } catch (err) {
      if (err instanceof SyntaxError) {
        setError("Invalid JSON format.");
      } else if (err.response && err.response.data && err.response.data.error) {
        setError(err.response.data.error.message || "An error occurred.");
      } else {
        setError("An unexpected error occurred.");
      }
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const filteredRules = rules.filter((rule) =>
    rule.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="max-w-2xl mx-auto p-8 mt-10 bg-white rounded-lg shadow-lg">
      <h2 className="text-3xl font-extrabold text-gray-800 mb-6">
        Evaluate Rule
      </h2>

      {error && (
        <div className="flex items-center text-red-600 bg-red-100 p-4 rounded mb-4">
          <AiOutlineCloseCircle className="mr-2" size={24} />
          <span>{error}</span>
        </div>
      )}

      <form onSubmit={handleEvaluateRule} className="space-y-6">
        <div ref={dropdownRef} className="relative">
          <label className="block text-lg font-semibold mb-2">
            Select Rule
          </label>
          <div
            className="border border-gray-300 px-4 py-3 rounded-lg shadow-sm cursor-pointer flex items-center justify-between"
            onClick={() => setIsDropdownOpen(!isDropdownOpen)}
          >
            <span>
              {selectedRule
                ? `${selectedRule.name}: ${selectedRule.rule_string}`
                : "-- Select a rule --"}
            </span>
            <FiChevronDown className="text-gray-400" />
          </div>

          {isDropdownOpen && (
            <div className="absolute z-10 w-full bg-white border border-gray-300 mt-1 rounded-lg shadow-lg max-h-60 overflow-y-auto">
              <input
                type="text"
                placeholder="Search rules..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full px-4 py-2 border-b focus:outline-none"
              />
              <ul className="divide-y divide-gray-100">
                {filteredRules.map((rule) => (
                  <li
                    key={rule.id}
                    className="px-4 py-2 hover:bg-gray-300 cursor-pointer"
                    onClick={() => {
                      setSelectedRule(rule);
                      setIsDropdownOpen(false);
                    }}
                  >
                    {rule.name}: {rule.rule_string}
                  </li>
                ))}
                {filteredRules.length === 0 && (
                  <li className="px-4 py-2 text-gray-500">No matching rules</li>
                )}
              </ul>
            </div>
          )}
        </div>

        <div>
          <label className="block text-lg font-semibold mb-2">
            User Data (JSON format)
          </label>
          <textarea
            className="w-full border border-gray-300 px-4 py-3 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={userData}
            onChange={(e) => setUserData(e.target.value)}
            placeholder='{"age": 35, "department": "Sales", "salary": 60000, "experience": 3}'
            required
            rows="6"
          ></textarea>
          <p className="text-sm text-gray-500 mt-2">
            Ensure the JSON is properly formatted.
          </p>
        </div>

        <button
          type="submit"
          className={`w-full bg-blue-500 text-white px-4 py-3 rounded-lg font-semibold transition-all duration-300 hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 ${
            loading ? "opacity-50 cursor-not-allowed" : ""
          }`}
          disabled={loading}
        >
          {loading ? "Evaluating..." : "Evaluate Rule"}
        </button>
      </form>

      {result !== null && (
        <div className="mt-8">
          <div
            className={`flex items-center ${
              result ? "text-green-600 bg-green-100" : "text-red-600 bg-red-100"
            } p-4 rounded-lg`}
          >
            {result ? (
              <AiOutlineCheckCircle className="mr-2" size={24} />
            ) : (
              <AiOutlineCloseCircle className="mr-2" size={24} />
            )}
            <span className="text-lg">
              The user data {result ? "matches" : "does not match"} the rule.
            </span>
          </div>
        </div>
      )}
    </div>
  );
}

export default EvaluateRuleComponent;
