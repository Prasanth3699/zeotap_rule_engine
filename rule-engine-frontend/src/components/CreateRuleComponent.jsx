import { useState } from "react";
import { createRule } from "../services/api";
import { AiOutlineCheckCircle, AiOutlineCloseCircle } from "react-icons/ai"; // Icons

function CreateRuleComponent() {
  const [name, setName] = useState("");
  const [ruleString, setRuleString] = useState("");
  const [message, setMessage] = useState("");
  const [ast, setAst] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleCreateRule = async (e) => {
    e.preventDefault();
    setError("");
    setMessage("");
    setAst(null);

    if (!name.trim() || !ruleString.trim()) {
      setError("Both name and rule string are required.");
      return;
    }

    try {
      setLoading(true);

      const response = await createRule(name.trim(), ruleString.trim());

      setMessage("Rule created successfully.");
      setAst(response.data.ast_json);
      setName("");
      setRuleString("");
    } catch (err) {
      if (err.response && err.response.data && err.response.data.error) {
        setError(err.response.data.error.message || "An error occurred.");
      } else {
        setError("An unexpected error occurred.");
      }
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto bg-white shadow-lg rounded-lg p-8 mt-10">
      <h2 className="text-3xl font-extrabold text-gray-800 mb-6">
        Create Rule
      </h2>

      {/* Success and Error Messages */}
      {error && (
        <div className="flex items-center text-red-600 bg-red-100 p-4 rounded mb-4">
          <AiOutlineCloseCircle className="mr-2" size={24} />
          <span>{error}</span>
        </div>
      )}
      {message && (
        <div className="flex items-center text-green-600 bg-green-100 p-4 rounded mb-4">
          <AiOutlineCheckCircle className="mr-2" size={24} />
          <span>{message}</span>
        </div>
      )}

      {/* Create Rule Form */}
      <form onSubmit={handleCreateRule} className="space-y-6">
        <div>
          <label className="block text-lg font-semibold mb-2">Rule Name</label>
          <input
            type="text"
            className="w-full border border-gray-300 px-4 py-3 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Enter rule name"
            required
          />
        </div>

        <div>
          <label className="block text-lg font-semibold mb-2">
            Rule String
          </label>
          <textarea
            className="w-full border border-gray-300 px-4 py-3 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={ruleString}
            onChange={(e) => setRuleString(e.target.value)}
            placeholder="Enter rule string (e.g., (age > 30 AND department = 'Sales'))"
            required
            rows="5"
          ></textarea>
          <p className="text-sm text-gray-500 mt-2">
            Ensure the rule string follows the correct syntax.
          </p>
        </div>

        <button
          type="submit"
          className={`w-full bg-blue-500 text-white px-4 py-3 rounded-lg font-semibold transition-all duration-300 hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 ${
            loading ? "opacity-50 cursor-not-allowed" : ""
          }`}
          disabled={loading}
        >
          {loading ? "Creating..." : "Create Rule"}
        </button>
      </form>

      {/* Display AST Representation */}
      {ast && (
        <div className="mt-8">
          <h3 className="text-xl font-bold text-gray-800 mb-2">
            AST Representation:
          </h3>
          <pre className="bg-gray-100 p-4 rounded-lg overflow-x-auto">
            {JSON.stringify(ast, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}

export default CreateRuleComponent;
