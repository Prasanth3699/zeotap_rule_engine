import { useState, useEffect } from "react";
import { getRules, deleteRule } from "../services/api";
import { Link } from "react-router-dom";
import { AiOutlineEdit, AiOutlineDelete } from "react-icons/ai"; // Icons

function RuleListComponent() {
  const [rules, setRules] = useState([]);
  const [count, setCount] = useState(0);
  const [nextPage, setNextPage] = useState(null);
  const [previousPage, setPreviousPage] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");

  useEffect(() => {
    fetchRules();
  }, []);

  const fetchRules = async (url = "/rules/") => {
    try {
      setLoading(true);
      const response = await getRules(url);
      setRules(response.data.results);
      setCount(response.data.count);
      setNextPage(response.data.next);
      setPreviousPage(response.data.previous);
    } catch (err) {
      setError("Failed to fetch rules.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (ruleId) => {
    if (!window.confirm("Are you sure you want to delete this rule?")) return;
    try {
      await deleteRule(ruleId);
      setRules(rules.filter((rule) => rule.id !== ruleId));
      setCount(count - 1);
    } catch (err) {
      setError("Failed to delete the rule.");
      console.error(err);
    }
  };

  const filteredRules = rules.filter(
    (rule) =>
      rule.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      rule.rule_string.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h2 className="text-3xl font-extrabold mb-6 text-gray-800">
        Existing Rules
      </h2>
      {error && <div className="text-red-500 mb-4">{error}</div>}
      <div className="relative mb-6">
        <input
          type="text"
          className="w-full border border-gray-300 px-4 py-3 rounded-lg shadow focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Search rules..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      {loading ? (
        <p className="text-center text-gray-500">Loading rules...</p>
      ) : (
        <>
          {filteredRules.length === 0 ? (
            <p className="text-center text-gray-500">No rules found.</p>
          ) : (
            <div className="grid grid-cols-1 gap-6">
              {filteredRules.map((rule) => (
                <div
                  key={rule.id}
                  className="p-6 bg-white rounded-lg shadow hover:shadow-lg transition-shadow duration-300"
                >
                  <div className="flex justify-between items-center">
                    <div>
                      <h3 className="text-xl font-semibold text-gray-800">
                        {rule.name}
                      </h3>
                      <p className="mt-2 text-gray-600">{rule.rule_string}</p>
                    </div>
                    <div className="flex space-x-4">
                      <Link
                        to={`/rules/${rule.id}/edit`}
                        className="text-blue-600 hover:text-blue-800"
                      >
                        <AiOutlineEdit size={24} />
                      </Link>
                      <button
                        onClick={() => handleDelete(rule.id)}
                        className="text-red-600 hover:text-red-800"
                      >
                        <AiOutlineDelete size={24} />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Pagination Controls */}
          <div className="flex justify-between mt-8">
            <button
              onClick={() => fetchRules(previousPage)}
              disabled={!previousPage}
              className={`px-4 py-2 rounded-lg ${
                previousPage
                  ? "bg-blue-500 text-white hover:bg-blue-600"
                  : "bg-gray-300 text-gray-600 cursor-not-allowed"
              }`}
            >
              Previous
            </button>
            <button
              onClick={() => fetchRules(nextPage)}
              disabled={!nextPage}
              className={`px-4 py-2 rounded-lg ${
                nextPage
                  ? "bg-blue-500 text-white hover:bg-blue-600"
                  : "bg-gray-300 text-gray-600 cursor-not-allowed"
              }`}
            >
              Next
            </button>
          </div>
          <p className="mt-4 text-center text-sm text-gray-500">
            Total Rules: {count}
          </p>
        </>
      )}
    </div>
  );
}

export default RuleListComponent;
