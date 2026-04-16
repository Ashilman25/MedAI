// src/pages/SignUp.jsx
import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { motion } from "framer-motion";
import PasswordField from "../components/ui/PasswordField";

export default function SignUp() {
  const { signUp } = useAuth();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    setErr(""); setLoading(true);
    try {
      await signUp(email, password, name);
      navigate("/chat");
    } catch (e) {
      setErr(e.message || "Failed to sign up");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-[70vh] items-center justify-center px-4">
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md rounded-2xl border border-gray-200 bg-white p-6 shadow-sm"
      >
        <h1 className="text-2xl font-semibold text-gray-900">Create account</h1>
        <p className="mt-1 text-sm text-gray-500">Join Med-Pal AI</p>

        <form onSubmit={handleSubmit} className="mt-5 space-y-3">
          <input
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500"
            type="text" placeholder="Name (optional)"
            value={name} onChange={(e)=>setName(e.target.value)}
          />
          <input
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500"
            type="email" placeholder="Email"
            value={email} onChange={(e)=>setEmail(e.target.value)}
          />
          <PasswordField
            value={password}
            onChange={(e)=>setPassword(e.target.value)}
            placeholder="Password (min 6 chars)"
          />

          {err && <div className="rounded border border-red-200 bg-red-50 p-2 text-sm text-red-700">{err}</div>}
          <button
            disabled={loading}
            className={`w-full rounded-lg bg-blue-600 px-3 py-2 text-white ${loading ? 'opacity-60' : 'hover:bg-blue-700'}`}
          >
            {loading ? "Creating…" : "Create account"}
          </button>
        </form>

        <div className="mt-4 text-center text-sm text-gray-600">
          Already have an account?{" "}
          <Link to="/signin" className="text-blue-600 hover:underline">Sign in</Link>
        </div>
      </motion.div>
    </div>
  );
}
