// src/pages/SignIn.jsx
import { useState } from "react";
import { useNavigate, useLocation, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { motion } from "framer-motion";
import PasswordField from "../components/ui/PasswordField";

export const Error = (props) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="1em"
    height="1em"
    viewBox="0 0 2048 2048"
    {...props}
  >
    <path
      fill="currentColor"
      d="M960 0q133 0 255 34t230 96t194 150t150 195t97 229t34 256q0 133-34 255t-96 230t-150 194t-195 150t-229 97t-256 34q-133 0-255-34t-230-96t-194-150t-150-195t-97-229T0 960q0-133 34-255t96-230t150-194t195-150t229-97T960 0zm0 1792q114 0 220-30t199-84t169-130t130-168t84-199t30-221q0-114-30-220t-84-199t-130-169t-168-130t-199-84t-221-30q-115 0-221 30t-198 84t-169 130t-130 168t-84 199t-30 221q0 114 30 220t84 199t130 169t168 130t199 84t221 30zM896 512h128v640H896V512zm0 768h128v128H896v-128z"
    ></path>
  </svg>
);

export default function SignIn() {
  const { signIn, resetPassword } = useAuth();
  const [email, setEmail] = useState("");
  const [pw, setPw] = useState("");
  const [err, setErr] = useState("");
  const [notice, setNotice] = useState("");
  const [loading, setLoading] = useState(false);
  const nav = useNavigate();
  const location = useLocation();
  const from = location.state?.from?.pathname || "/chat";

  async function handleSubmit(e) {
    e.preventDefault();
    setErr(""); setNotice(""); setLoading(true);
    try {
      await signIn(email, pw);
      nav(from, { replace: true });
    } catch (e) {
      setErr(e.message || "Failed to sign in");
    } finally {
      setLoading(false);
    }
  }

  async function handleForgot() {
    setErr(""); setNotice("");
    if (!email) { setErr("Enter your email first to receive a reset link."); return; }
    try {
      await resetPassword(email);
      setNotice("Password reset email sent. Check your inbox.");
    } catch (e) {
      setErr(e.message || "Could not send reset email");
    }
  }

  return (
    <div className="flex min-h-[70vh] items-center justify-center px-4">
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md rounded-2xl border border-gray-200 bg-white p-6 shadow-sm"
      >
        <h1 className="text-2xl font-semibold text-gray-900">Sign in</h1>
        <p className="mt-1 text-sm text-gray-500">Welcome back to MedAI-RAG</p>

        <form onSubmit={handleSubmit} className="mt-5 space-y-3">
          <input
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500"
            type="email" placeholder="Email"
            value={email} onChange={(e)=>setEmail(e.target.value)}
          />

          <PasswordField
            value={pw}
            onChange={(e)=>setPw(e.target.value)}
            placeholder="Password"
          />

          {err && (
            <div className="flex items-center gap-2 rounded border border-red-200 bg-red-50 p-2 text-sm text-red-700">
              <Error className="text-red-700" />
              <span>Email or password invalid</span>
            </div>
          )}          
          {notice && <div className="rounded border border-teal-200 bg-teal-50 p-2 text-sm text-teal-700">{notice}</div>}
          <button
            disabled={loading}
            className={`w-full rounded-lg bg-blue-600 px-3 py-2 text-white ${loading ? 'opacity-60' : 'hover:bg-blue-700'}`}
          >
            {loading ? "Signing in…" : "Sign in"}
          </button>
        </form>

        <div className="mt-3 flex items-center justify-between text-xs">
          <button onClick={handleForgot} className="text-blue-600 hover:underline">
            Forgot password?
          </button>
          <Link to="/signup" className="text-gray-600 hover:underline">
            Create account
          </Link>
        </div>
      </motion.div>
    </div>
  );
}
