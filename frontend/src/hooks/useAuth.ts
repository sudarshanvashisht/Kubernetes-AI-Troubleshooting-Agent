"use client";

import { useEffect, useState, useCallback } from "react";
import { insforge } from "@/lib/insforge";
import type { UserSchema } from "@insforge/sdk";

export function useAuth() {
  const [user, setUser] = useState<UserSchema | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchUser = useCallback(async () => {
    try {
      const { data, error: userError } = await insforge.auth.getCurrentUser();
      if (userError) {
        setUser(null);
      } else {
        setUser(data?.user ?? null);
      }
    } catch {
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    let isMounted = true;

    const checkUser = async () => {
      try {
        const { data, error: userError } = await insforge.auth.getCurrentUser();
        if (!isMounted) return;
        if (userError) {
          setUser(null);
        } else {
          setUser(data?.user ?? null);
        }
      } catch {
        if (isMounted) setUser(null);
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    checkUser();

    // Subscribe to auth state change if available
    const unsubscribe = insforge.auth.onAuthStateChange(() => {
      checkUser();
    });

    return () => {
      isMounted = false;
      if (typeof unsubscribe === "function") {
        unsubscribe();
      }
    };
  }, []);

  const signIn = async (email: string, password: string) => {
    setError(null);
    setLoading(true);
    try {
      const { data, error: signInError } =
        await insforge.auth.signInWithPassword({
          email,
          password,
        });

      if (signInError) {
        const msg = signInError.message || "Failed to sign in";
        setError(msg);
        return { success: false, error: msg };
      }

      if (data?.user) {
        setUser(data.user);
      } else {
        await fetchUser();
      }

      return { success: true, user: data?.user ?? null };
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Sign in failed";
      setError(msg);
      return { success: false, error: msg };
    } finally {
      setLoading(false);
    }
  };

  const signUp = async (email: string, password: string, name?: string) => {
    setError(null);
    setLoading(true);
    try {
      const { data, error: signUpError } = await insforge.auth.signUp({
        email,
        password,
        name,
      });

      if (signUpError) {
        const msg = signUpError.message || "Failed to sign up";
        setError(msg);
        return { success: false, error: msg };
      }

      if (data?.requireEmailVerification) {
        return { success: true, requireVerification: true, email };
      }

      // Automatically sign in after signup if a user was created
      if (data?.user) {
        setUser(data.user);
      } else {
        // Attempt sign in with the new credentials
        await insforge.auth.signInWithPassword({ email, password });
        await fetchUser();
      }

      return { success: true, user: data?.user ?? null };
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Sign up failed";
      setError(msg);
      return { success: false, error: msg };
    } finally {
      setLoading(false);
    }
  };

  const verifyEmail = async (email: string, otp: string) => {
    setError(null);
    setLoading(true);
    try {
      const { data, error: verifyError } = await insforge.auth.verifyEmail({
        email,
        otp,
      });

      if (verifyError) {
        const msg = verifyError.message || "Verification failed";
        setError(msg);
        return { success: false, error: msg };
      }

      if (data?.user) {
        setUser(data.user);
      } else {
        await fetchUser();
      }

      return { success: true, user: data?.user ?? null };
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Verification failed";
      setError(msg);
      return { success: false, error: msg };
    } finally {
      setLoading(false);
    }
  };

  const signOut = async () => {
    setLoading(true);
    try {
      await insforge.auth.signOut();
      setUser(null);
      return { success: true };
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Sign out failed";
      return { success: false, error: msg };
    } finally {
      setLoading(false);
    }
  };

  return {
    user,
    loading,
    error,
    signIn,
    signUp,
    verifyEmail,
    signOut,
    refreshUser: fetchUser,
  };
}
