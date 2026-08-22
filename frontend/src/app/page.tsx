"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { insforge } from "@/lib/insforge";
import { investigateCluster, getClusters } from "@/services/api";
import type {
  FullDiagnosisResponse,
  InvestigationHistoryRecord,
  RealtimeProgressPayload,
} from "@/types";

export default function DashboardPage() {
  const router = useRouter();
  const { user, loading: authLoading, signOut } = useAuth();

  // Investigation state
  const [isInvestigating, setIsInvestigating] = useState(false);
  const [status, setStatus] = useState<"Ready" | "Investigating" | "Completed" | "Error">("Ready");
  const [clusters, setClusters] = useState<string[]>([]);
  const [selectedCluster, setSelectedCluster] = useState<string>("");
  const [namespace, setNamespace] = useState("");
  const [progressMessages, setProgressMessages] = useState<string[]>([]);
  const [currentDiagnosis, setCurrentDiagnosis] = useState<FullDiagnosisResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // History state
  const [history, setHistory] = useState<InvestigationHistoryRecord[]>([]);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [selectedHistoryId, setSelectedHistoryId] = useState<string | null>(null);
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

  const activeChannelRef = useRef<string | null>(null);
  const progressEndRef = useRef<HTMLDivElement | null>(null);

  // Fetch available Kubernetes clusters from kubeconfig
  useEffect(() => {
    (async () => {
      const res = await getClusters();
      if (res.clusters && res.clusters.length > 0) {
        setClusters(res.clusters);
        setSelectedCluster(res.current_context || res.clusters[0]);
      }
    })();
  }, []);

  // Redirect to /auth if not logged in
  useEffect(() => {
    if (!authLoading && !user) {
      router.replace("/auth");
    }
  }, [user, authLoading, router]);

  // Scroll to bottom of progress log
  useEffect(() => {
    progressEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [progressMessages]);

  const loadHistoryData = async (userId: string) => {
    setLoadingHistory(true);
    try {
      const { data, error } = await insforge.database
        .from("investigations")
        .select("*")
        .eq("user_id", userId)
        .order("created_at", { ascending: false });

      if (!error && Array.isArray(data) && data.length > 0) {
        setHistory(data as InvestigationHistoryRecord[]);
      } else {
        const local = localStorage.getItem(`k8s_history_${userId}`);
        if (local) {
          try {
            setHistory(JSON.parse(local));
          } catch {
            setHistory([]);
          }
        }
      }
    } catch {
      const local = localStorage.getItem(`k8s_history_${userId}`);
      if (local) {
        try {
          setHistory(JSON.parse(local));
        } catch {
          setHistory([]);
        }
      }
    } finally {
      setLoadingHistory(false);
    }
  };

  // Fetch history on user login
  useEffect(() => {
    if (!user?.id) return;
    const userId = user.id;

    let isMounted = true;
    (async () => {
      try {
        const { data, error } = await insforge.database
          .from("investigations")
          .select("*")
          .eq("user_id", userId)
          .order("created_at", { ascending: false });

        if (!isMounted) return;

        if (!error && Array.isArray(data) && data.length > 0) {
          setHistory(data as InvestigationHistoryRecord[]);
        } else {
          const local = localStorage.getItem(`k8s_history_${userId}`);
          if (local) {
            try {
              setHistory(JSON.parse(local));
            } catch {
              setHistory([]);
            }
          }
        }
      } catch {
        if (!isMounted) return;
        const local = localStorage.getItem(`k8s_history_${userId}`);
        if (local) {
          try {
            setHistory(JSON.parse(local));
          } catch {
            setHistory([]);
          }
        }
      }
    })();

    return () => {
      isMounted = false;
    };
  }, [user?.id]);

  // Cleanup realtime subscription on unmount
  useEffect(() => {
    return () => {
      if (activeChannelRef.current) {
        try {
          insforge.realtime.unsubscribe(activeChannelRef.current);
        } catch {
          // ignore cleanup errors
        }
      }
    };
  }, []);

  const handleInvestigate = async () => {
    if (isInvestigating) return;

    setErrorMessage(null);
    setIsInvestigating(true);
    setStatus("Investigating");
    setCurrentDiagnosis(null);
    setSelectedHistoryId(null);
    setProgressMessages(["Initiating cluster diagnostic pipeline..."]);

    const investigationId = Date.now().toString();
    const channelName = `investigation:${investigationId}`;
    activeChannelRef.current = channelName;

    // 1. Subscribe to Realtime channel
    try {
      await insforge.realtime.subscribe(channelName);
      
      const onProgress = (payload: unknown) => {
        let msg = "";
        if (typeof payload === "string") {
          msg = payload;
        } else if (payload && typeof payload === "object") {
          const p = payload as RealtimeProgressPayload & { payload?: { message?: string }; message?: string };
          msg = p.payload?.message || p.message || JSON.stringify(p);
        }
        if (msg) {
          setProgressMessages((prev) => [...prev, msg]);
        }
      };

      insforge.realtime.on("progress", onProgress);
    } catch (realtimeErr) {
      console.warn("Realtime subscription notice:", realtimeErr);
    }

    // 2. Call Backend API
    try {
      const responseData = await investigateCluster(investigationId, namespace, selectedCluster);
      setCurrentDiagnosis(responseData);
      setStatus("Completed");
      setProgressMessages((prev) => [
        ...prev,
        "AI SRE analysis and diagnosis complete.",
      ]);

      // 3. Save result to history
      if (user?.id) {
        const newRecord: InvestigationHistoryRecord = {
          id: investigationId,
          user_id: user.id,
          created_at: new Date().toISOString(),
          result: responseData,
        };

        const diag = responseData?.diagnosis;
        const rootCauseVal = diag?.root_cause || responseData?.root_cause || "Unknown";
        const confidenceVal = diag?.confidence ?? responseData?.confidence ?? 0;

        // Try inserting into InsForge Database
        try {
          await insforge.database.from("investigations").insert({
            id: investigationId,
            user_id: user.id,
            timestamp: new Date().toISOString(),
            root_cause: rootCauseVal,
            namespace: namespace || "all",
            confidence: confidenceVal,
            status: "Completed",
            result: responseData,
          });
        } catch (dbErr) {
          console.warn("Database save notice:", dbErr);
        }

        // Also save to local state and localStorage for instant reactivity
        setHistory((prev) => {
          const updated = [newRecord, ...prev.filter((h) => h.id !== investigationId)];
          try {
            localStorage.setItem(`k8s_history_${user.id}`, JSON.stringify(updated));
          } catch {
            // ignore localStorage quota
          }
          return updated;
        });
      }
    } catch (err: unknown) {
      const msg =
        err instanceof Error
          ? err.message
          : "Failed to connect to investigation backend.";
      setErrorMessage(msg);
      setStatus("Error");
      setProgressMessages((prev) => [
        ...prev,
        `❌ Investigation failed: ${msg}`,
      ]);
    } finally {
      setIsInvestigating(false);
      try {
        insforge.realtime.unsubscribe(channelName);
      } catch {
        // ignore
      }
    }
  };

  const copyToClipboard = (text: string, index: number) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  const handleSelectHistory = (record: InvestigationHistoryRecord) => {
    setSelectedHistoryId(record.id);
    setCurrentDiagnosis(record.result);
    setProgressMessages([]);
    setStatus("Completed");
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  if (authLoading || !user) {
    return (
      <div className="min-h-screen bg-[#030712] flex items-center justify-center text-gray-400">
        <div className="flex items-center space-x-3 bg-slate-900/50 border border-slate-800 px-5 py-3 rounded-xl shadow-xl backdrop-blur-md">
          <div className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
          <span className="text-sm font-medium text-slate-300">Loading session...</span>
        </div>
      </div>
    );
  }

  // Extract diagnosis information safely
  const diag = currentDiagnosis?.diagnosis;
  const rootCause = diag?.root_cause || currentDiagnosis?.root_cause;
  const explanation = diag?.explanation;
  const fix = diag?.fix;
  const suggestions = currentDiagnosis?.suggestions || [];
  const kubectlCmds = diag?.kubectl_commands || [];
  const prevention = diag?.prevention;
  const confidence = diag?.confidence ?? currentDiagnosis?.confidence;

  return (
    <div className="min-h-screen bg-[#030712] bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-950/20 via-[#030712] to-[#030712] text-slate-100 flex flex-col selection:bg-blue-600/30">
      
      {/* Top Navbar */}
      <header className="w-full border-b border-slate-800/40 bg-[#030712]/60 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded-lg bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400 shadow-md">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
            </div>
            <span className="text-xs font-mono text-blue-400 bg-blue-950/40 border border-blue-800/40 px-3 py-1 rounded-full">
              {user.email}
            </span>
          </div>

          <button
            onClick={() => signOut()}
            className="text-xs text-slate-400 hover:text-white transition-colors bg-slate-900/60 hover:bg-slate-800/80 px-3.5 py-1.5 rounded-lg border border-slate-800 flex items-center space-x-1.5"
          >
            <span>Sign out</span>
            <svg className="w-3.5 h-3.5 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
          </button>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-3xl w-full mx-auto px-6 py-12 flex flex-col items-center space-y-10">
        
        {/* Hero Section */}
        <section className="text-center space-y-6 w-full animate-fadeIn">
          <div className="space-y-3">
            <h1 className="text-4xl sm:text-5xl font-extrabold text-white tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-100 to-blue-300">
              AI Kubernetes Agent
            </h1>
            <p className="text-sm text-slate-400 font-light max-w-md mx-auto">
              Automated Site Reliability Engineering & Real-time Diagnostic Console
            </p>
          </div>

          {/* Cluster Selector & Namespace Controls Card */}
          <div className="glass-panel p-6 rounded-2xl space-y-4 w-full max-w-md mx-auto shadow-2xl">
            {clusters.length > 0 && (
              <div className="w-full flex flex-col space-y-1.5 text-left">
                <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider flex items-center space-x-1">
                  <span>Target Kubernetes Cluster</span>
                </label>
                <div className="relative">
                  <select
                    value={selectedCluster}
                    onChange={(e) => setSelectedCluster(e.target.value)}
                    disabled={isInvestigating}
                    className="w-full px-3.5 py-2.5 bg-[#030712] border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 cursor-pointer font-mono appearance-none pr-8"
                  >
                    {clusters.map((c) => (
                      <option key={c} value={c} className="bg-[#0b1329] text-white">
                        ☸ {c}
                      </option>
                    ))}
                  </select>
                  <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-slate-500 text-xs">
                    ▼
                  </div>
                </div>
              </div>
            )}

            <div className="w-full flex flex-col space-y-1.5 text-left">
              <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                Namespace Filter
              </label>
              <input
                type="text"
                placeholder="All namespaces (default)"
                value={namespace}
                onChange={(e) => setNamespace(e.target.value)}
                disabled={isInvestigating}
                className="w-full px-3.5 py-2.5 bg-[#030712] border border-slate-800 rounded-xl text-xs text-white placeholder-slate-600 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 font-mono transition-all"
              />
            </div>

            <button
              onClick={handleInvestigate}
              disabled={isInvestigating}
              className="w-full py-3 px-6 bg-[#2563eb] hover:bg-blue-500 active:scale-[0.99] disabled:bg-blue-800/60 disabled:cursor-not-allowed text-white font-semibold text-sm rounded-xl transition-all duration-150 shadow-lg shadow-blue-600/25 flex items-center justify-center space-x-2 mt-2"
            >
              {isInvestigating ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                  <span>Investigating Cluster...</span>
                </>
              ) : (
                <>
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                  <span>Investigate Cluster</span>
                </>
              )}
            </button>
          </div>
        </section>

        {/* Error Banner */}
        {errorMessage && (
          <div className="w-full bg-red-950/30 border border-red-900/40 rounded-2xl p-4 text-xs text-red-300 text-center animate-fadeIn shadow-lg backdrop-blur-md">
            {errorMessage}
          </div>
        )}

        {/* Live Progress Terminal */}
        {progressMessages.length > 0 && (
          <section className="w-full glass-panel rounded-2xl p-6 shadow-2xl space-y-4 font-mono text-xs text-left animate-fadeIn">
            <div className="flex items-center justify-between border-b border-slate-800/60 pb-3">
              <div className="flex items-center space-x-2">
                <span className="w-2.5 h-2.5 rounded-full bg-blue-500 animate-ping" />
                <span className="text-[11px] font-bold text-slate-300 tracking-wider">DIAGNOSTIC PIPELINE LOGS</span>
              </div>
              {isInvestigating ? (
                <span className="text-[10px] bg-blue-950/80 border border-blue-800/50 text-blue-400 px-2.5 py-0.5 rounded-full font-semibold animate-pulse">
                  ● RUNNING
                </span>
              ) : (
                <span className="text-[10px] bg-emerald-950/80 border border-emerald-800/50 text-emerald-400 px-2.5 py-0.5 rounded-full font-semibold">
                  ✓ DONE
                </span>
              )}
            </div>
            
            <div className="space-y-2 max-h-64 overflow-y-auto pr-1 scrollbar-thin">
              {progressMessages.map((msg, i) => (
                <div key={i} className="flex items-start space-x-2 text-slate-300 bg-[#030712]/60 p-2.5 rounded-lg border border-slate-800/40">
                  <span className="text-blue-400 shrink-0 select-none">›</span>
                  <span className="leading-relaxed">{msg}</span>
                </div>
              ))}
              <div ref={progressEndRef} />
            </div>
          </section>
        )}

        {/* Active Diagnosis Card */}
        {currentDiagnosis && (
          <section className="w-full glass-panel rounded-2xl p-7 shadow-2xl space-y-6 text-left animate-fadeIn">
            <div className="flex items-center justify-between border-b border-slate-800/60 pb-4">
              <div className="flex items-center space-x-2.5">
                <div className="w-7 h-7 rounded-lg bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400">
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                </div>
                <h2 className="text-lg font-bold text-white tracking-tight">Diagnosis Report</h2>
              </div>

              {confidence !== undefined && (
                <span className={`text-xs px-3 py-1 rounded-full font-mono font-bold tracking-wide shadow-md ${
                  confidence >= 80 ? "bg-emerald-950/80 border border-emerald-700/50 text-emerald-400 shadow-emerald-900/20" :
                  confidence >= 50 ? "bg-yellow-950/80 border border-yellow-700/50 text-yellow-400 shadow-yellow-900/20" : "bg-red-950/80 border border-red-700/50 text-red-400 shadow-red-900/20"
                }`}>
                  {confidence}% Confidence
                </span>
              )}
            </div>

            {/* Root Cause */}
            <div className="space-y-2">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Root Cause</span>
              <div className="text-sm font-semibold text-white bg-[#030712] p-4 rounded-xl border border-slate-800 leading-relaxed shadow-inner">
                {rootCause || "No anomaly detected in cluster check."}
              </div>
            </div>

            {/* Explanation */}
            {explanation && (
              <div className="space-y-2">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Detailed Analysis</span>
                <p className="text-xs text-slate-300 leading-relaxed bg-[#030712] p-4 rounded-xl border border-slate-800">
                  {explanation}
                </p>
              </div>
            )}

            {/* Fix */}
            {fix && (
              <div className="space-y-2">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Suggested Fix</span>
                <div className="text-xs text-emerald-300 bg-emerald-950/20 p-4 rounded-xl border border-emerald-900/40 leading-relaxed font-medium">
                  {fix}
                </div>
              </div>
            )}

            {/* Kubectl Commands */}
            {kubectlCmds.length > 0 && (
              <div className="space-y-2">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Recommended Kubectl Commands</span>
                <div className="space-y-2">
                  {kubectlCmds.map((cmdStr, idx) => (
                    <div
                      key={idx}
                      className="flex items-center justify-between bg-[#030712] border border-slate-800 px-4 py-2.5 rounded-xl font-mono text-xs text-blue-300 group hover:border-slate-700 transition-colors"
                    >
                      <span className="truncate pr-3">$ {cmdStr}</span>
                      <button
                        onClick={() => copyToClipboard(cmdStr, idx)}
                        className="shrink-0 text-[10px] px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg transition-colors border border-slate-700"
                      >
                        {copiedIndex === idx ? "Copied!" : "Copy"}
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Prevention */}
            {prevention && (
              <div className="space-y-2">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Prevention Recommendations</span>
                <p className="text-xs text-slate-400 bg-[#030712] p-4 rounded-xl border border-slate-800 leading-relaxed">
                  {prevention}
                </p>
              </div>
            )}
          </section>
        )}

        {/* Previous Investigations Section */}
        <section className="w-full space-y-4 pt-4 text-center animate-fadeIn">
          <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Previous Investigations</h3>
          
          {history.length === 0 ? (
            <div className="text-xs text-slate-500 py-8 bg-[#0b1329]/40 border border-slate-800/40 rounded-2xl">
              No previous investigations yet.
            </div>
          ) : (
            <div className="space-y-2.5 w-full">
              {history.map((record) => {
                const isSelected = selectedHistoryId === record.id;
                const recordDiag = record.result?.diagnosis;
                const recordRC = recordDiag?.root_cause || record.result?.root_cause || "Unknown";
                const recordConf = recordDiag?.confidence ?? record.result?.confidence;
                const date = new Date(record.created_at || Date.now());

                return (
                  <div
                    key={record.id}
                    onClick={() => handleSelectHistory(record)}
                    className={`cursor-pointer p-4 rounded-2xl border transition-all duration-150 flex items-center justify-between text-left ${
                      isSelected
                        ? "bg-blue-950/30 border-blue-500/60 shadow-lg shadow-blue-950/50 ring-1 ring-blue-500/30"
                        : "glass-card hover:bg-slate-900/60 hover:border-slate-700/60"
                    }`}
                  >
                    <div className="space-y-1 min-w-0 pr-4">
                      <div className="text-xs font-semibold text-white truncate max-w-md">
                        {recordRC}
                      </div>
                      <div className="text-[10px] text-slate-400 font-mono">
                        {date.toLocaleString()}
                      </div>
                    </div>

                    <div className="flex items-center space-x-3 shrink-0">
                      {recordConf !== undefined && (
                        <span className="text-[10px] px-2.5 py-0.5 rounded-full font-mono bg-blue-950/60 border border-blue-800/40 text-blue-400 font-medium">
                          {recordConf}%
                        </span>
                      )}
                      <span className="text-slate-500 text-xs">→</span>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </section>

      </main>
    </div>
  );
}
