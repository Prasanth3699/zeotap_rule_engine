/* eslint-disable react/prop-types */
import { useState } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Link,
  NavLink,
} from "react-router-dom";
import CreateRuleComponent from "./components/CreateRuleComponent";
import CombineRulesComponent from "./components/CombineRulesComponent";
import EvaluateRuleComponent from "./components/EvaluateRuleComponent";
import RuleListComponent from "./components/RuleListComponent";
import EditRuleComponent from "./components/EditRuleComponent";
import {
  AiOutlineHome,
  AiOutlinePlus,
  AiOutlineLink,
  AiOutlineCheckSquare,
  AiOutlineMenu,
  AiOutlineClose,
} from "react-icons/ai";

function App() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen((prev) => !prev);
  };

  const closeMobileMenu = () => {
    setIsMobileMenuOpen(false);
  };

  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        {/* Navbar */}
        <nav className="bg-white shadow sticky top-0 z-50">
          <div className="container mx-auto px-6 py-4">
            <div className="flex justify-between items-center">
              {/* Logo and Title */}
              <Link
                to="/"
                className="text-2xl font-extrabold text-blue-600 flex items-center space-x-2"
                onClick={closeMobileMenu}
              >
                <AiOutlineHome className="text-blue-500" size={28} />
                <span>Rule Engine</span>
              </Link>

              {/* Desktop Links */}
              <div className="hidden md:flex space-x-6 text-lg">
                <CustomNavLink
                  to="/create-rule"
                  label="Create Rule"
                  icon={AiOutlinePlus}
                />
                <CustomNavLink
                  to="/combine-rules"
                  label="Combine Rules"
                  icon={AiOutlineLink}
                />
                <CustomNavLink
                  to="/evaluate-rule"
                  label="Evaluate Rule"
                  icon={AiOutlineCheckSquare}
                />
              </div>

              {/* Hamburger Menu Icon (Mobile) */}
              <button
                className="md:hidden focus:outline-none"
                onClick={toggleMobileMenu}
              >
                {isMobileMenuOpen ? (
                  <AiOutlineClose size={28} className="text-blue-500" />
                ) : (
                  <AiOutlineMenu size={28} className="text-blue-500" />
                )}
              </button>
            </div>

            {/* Mobile Menu */}
            {isMobileMenuOpen && (
              <div className="md:hidden mt-4 space-y-4">
                <CustomNavLink
                  to="/create-rule"
                  label="Create Rule"
                  icon={AiOutlinePlus}
                  onClick={closeMobileMenu}
                />
                <CustomNavLink
                  to="/combine-rules"
                  label="Combine Rules"
                  icon={AiOutlineLink}
                  onClick={closeMobileMenu}
                />
                <CustomNavLink
                  to="/evaluate-rule"
                  label="Evaluate Rule"
                  icon={AiOutlineCheckSquare}
                  onClick={closeMobileMenu}
                />
              </div>
            )}
          </div>
        </nav>

        {/* Main Content */}
        <div className="container mx-auto px-6 py-8">
          <Routes>
            <Route path="/" element={<RuleListComponent />} />
            <Route path="/create-rule" element={<CreateRuleComponent />} />
            <Route path="/combine-rules" element={<CombineRulesComponent />} />
            <Route path="/evaluate-rule" element={<EvaluateRuleComponent />} />
            <Route path="/rules/:ruleId/edit" element={<EditRuleComponent />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

// Custom NavLink Component for Modern Links with Icons
const CustomNavLink = ({ to, label, icon: Icon, onClick }) => (
  <NavLink
    to={to}
    onClick={onClick}
    className={({ isActive }) =>
      `flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors duration-300 ${
        isActive
          ? "bg-blue-100 text-blue-600"
          : "text-gray-600 hover:bg-gray-100 hover:text-blue-500"
      }`
    }
  >
    <Icon size={22} />
    <span>{label}</span>
  </NavLink>
);

// 404 Not Found Component
const NotFound = () => (
  <div className="flex flex-col items-center justify-center h-[70vh] text-center">
    <h2 className="text-4xl font-extrabold text-gray-800 mb-4">
      404 - Page Not Found
    </h2>
    <p className="text-lg text-gray-600 mb-6">
      The page you are looking for does not exist.
    </p>
    <Link
      to="/"
      className="bg-blue-500 text-white px-6 py-3 rounded-lg hover:bg-blue-600 transition-all duration-300"
    >
      Go Home
    </Link>
  </div>
);

export default App;
