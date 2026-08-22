"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";

export default function AuthPage() {
  const router = useRouter();
  const { user, loading: authLoading, signIn, signUp, verifyEmail } = useAuth();

  const [isSignUp, setIsSignUp] = useState(false);
  const [showVerification, setShowVerification] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [otp, setOtp] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Redirect to dashboard if logged in
  useEffect(() => {
    if (!authLoading && user) {
      router.replace("/");
    }
  }, [user, authLoading, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);

    if (!email || !password) {
      setErrorMessage("Please enter both email and password.");
      return;
    }

    if (password.length < 6) {
      setErrorMessage("Password must be at least 6 characters long.");
      return;
    }

    setSubmitting(true);
    try {
      if (isSignUp) {
        const result = await signUp(email, password, name.trim() || undefined);
        if (!result.success) {
          setErrorMessage(result.error || "Failed to create account.");
        } else if (result.requireVerification) {
          setShowVerification(true);
        } else {
          router.replace("/");
        }
      } else {
        const result = await signIn(email, password);
        if (!result.success) {
          setErrorMessage(result.error || "Invalid credentials.");
        } else {
          router.replace("/");
        }
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Authentication failed.";
      setErrorMessage(msg);
    } finally {
      setSubmitting(false);
    }
  };

  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);

    if (!otp || otp.length !== 6) {
      setErrorMessage("Please enter a valid 6-digit verification code.");
      return;
    }

    setSubmitting(true);
    try {
      const result = await verifyEmail(email, otp);
      if (!result.success) {
        setErrorMessage(result.error || "Failed to verify email. Please try again.");
      } else {
        router.replace("/");
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Verification failed.";
      setErrorMessage(msg);
    } finally {
      setSubmitting(false);
    }
  };

  if (authLoading) {
    return (
      <div className="min-h-screen bg-[#030712] flex items-center justify-center text-gray-400">
        <div className="flex items-center space-x-3 bg-slate-900/50 border border-slate-800 px-5 py-3 rounded-xl shadow-xl backdrop-blur-md">
          <div className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
          <span className="text-sm font-medium text-slate-300">Checking session...</span>
        </div>
      </div>
    );
  }

  return (
    <main className="min-h-screen flex items-center justify-center bg-[#030712] bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-950/30 via-[#030712] to-[#030712] px-4 selection:bg-blue-600/30">
      <div className="w-full max-w-[390px] glass-panel rounded-2xl p-8 shadow-2xl space-y-6 animate-fadeIn">
        
        {errorMessage && (
          <div className="p-3 bg-red-950/40 border border-red-900/40 rounded-xl text-xs text-red-300 text-center animate-fadeIn">
            {errorMessage}
          </div>
        )}

        {showVerification ? (
          /* OTP Verification Form */
          <form onSubmit={handleVerify} className="space-y-4">
            <div className="space-y-1">
              <h1 className="text-2xl font-bold text-white tracking-tight">Verify email</h1>
              <p className="text-xs text-slate-400">
                Enter the 6-digit code sent to your email
              </p>
            </div>

            <div className="space-y-3">
              <input
                type="email"
                disabled
                value={email}
                className="w-full px-3.5 py-2.5 bg-[#030712] border border-slate-800/80 rounded-xl text-sm text-slate-400 cursor-not-allowed focus:outline-none"
              />
              <input
                type="text"
                required
                maxLength={6}
                value={otp}
                onChange={(e) => setOtp(e.target.value.replace(/\D/g, ""))}
                placeholder="482310"
                className="w-full px-3.5 py-2.5 bg-[#030712] border border-slate-800 rounded-xl text-sm text-white focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 font-mono tracking-widest text-center"
              />
            </div>

            <button
              type="submit"
              disabled={submitting}
              className="w-full py-2.5 px-4 bg-[#2563eb] hover:bg-blue-500 active:scale-[0.99] disabled:bg-blue-800/60 disabled:cursor-not-allowed text-white font-medium text-sm rounded-xl transition-all duration-150 shadow-lg shadow-blue-600/25 flex items-center justify-center"
            >
              {submitting ? "Verifying..." : "Verify email"}
            </button>

            <div className="text-center pt-2">
              <button
                type="button"
                onClick={() => {
                  setShowVerification(false);
                  setIsSignUp(false);
                  setErrorMessage(null);
                  setOtp("");
                }}
                className="text-xs text-slate-400 hover:text-white transition-colors"
              >
                Back to sign in
              </button>
            </div>
          </form>
        ) : isSignUp ? (
          /* Sign Up / Create Account Form */
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-1">
              <h1 className="text-2xl font-bold text-white tracking-tight">Create account</h1>
              <p className="text-xs text-slate-400">
                Access the AI Kubernetes troubleshooting dashboard
              </p>
            </div>

            <div className="space-y-3">
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Email"
                className="w-full px-3.5 py-2.5 bg-[#030712] border border-slate-800 rounded-xl text-sm text-white focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 placeholder-slate-600 transition-all"
              />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Password"
                className="w-full px-3.5 py-2.5 bg-[#030712] border border-slate-800 rounded-xl text-sm text-white focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 placeholder-slate-600 transition-all"
              />
            </div>

            <button
              type="submit"
              disabled={submitting}
              className="w-full py-2.5 px-4 bg-[#2563eb] hover:bg-blue-500 active:scale-[0.99] disabled:bg-blue-800/60 disabled:cursor-not-allowed text-white font-medium text-sm rounded-xl transition-all duration-150 shadow-lg shadow-blue-600/25"
            >
              {submitting ? "Creating account..." : "Create account"}
            </button>

            <div className="text-center pt-2 text-xs text-slate-400">
              Already have an account?{" "}
              <button
                type="button"
                onClick={() => {
                  setIsSignUp(false);
                  setErrorMessage(null);
                }}
                className="text-blue-500 hover:text-blue-400 font-medium hover:underline transition-colors"
              >
                Sign in
              </button>
            </div>
          </form>
        ) : (
          /* Sign In Form */
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-1">
              <h1 className="text-2xl font-bold text-white tracking-tight">Sign in</h1>
              <p className="text-xs text-slate-400">
                Access the AI Kubernetes troubleshooting dashboard
              </p>
            </div>

            <div className="space-y-3">
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Email"
                className="w-full px-3.5 py-2.5 bg-[#030712] border border-slate-800 rounded-xl text-sm text-white focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 placeholder-slate-600 transition-all"
              />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Password"
                className="w-full px-3.5 py-2.5 bg-[#030712] border border-slate-800 rounded-xl text-sm text-white focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 placeholder-slate-600 transition-all"
              />
            </div>

            <button
              type="submit"
              disabled={submitting}
              className="w-full py-2.5 px-4 bg-[#2563eb] hover:bg-blue-500 active:scale-[0.99] disabled:bg-blue-800/60 disabled:cursor-not-allowed text-white font-medium text-sm rounded-xl transition-all duration-150 shadow-lg shadow-blue-600/25"
            >
              {submitting ? "Signing in..." : "Sign in"}
            </button>

            <div className="text-center pt-2 text-xs text-slate-400">
              No account?{" "}
              <button
                type="button"
                onClick={() => {
                  setIsSignUp(true);
                  setErrorMessage(null);
                }}
                className="text-blue-500 hover:text-blue-400 font-medium hover:underline transition-colors"
              >
                Create account
              </button>
            </div>
          </form>
        )}
      </div>
    </main>
  );
}
