import { createClient } from "@insforge/sdk";

const url = process.env.NEXT_PUBLIC_INSFORGE_URL;
const anonKey = process.env.NEXT_PUBLIC_INSFORGE_ANON_KEY;

let client: any;
if (url) {
  try {
    client = createClient({ baseUrl: url, anonKey: anonKey ?? "" });
  } catch (e) {
    console.warn("Failed to create InsForge client", e);
    client = null;
  }
} else {
  console.warn("NEXT_PUBLIC_INSFORGE_URL is not set; InsForge features disabled.");
}

// Graceful no-op fallback so the app still builds/runs without InsForge configured.
const noop = () => ({});
const fallback: any = {
  auth: {
    getCurrentUser: async () => ({ data: null, error: new Error("InsForge not configured") }),
    signInWithPassword: async () => ({ data: null, error: new Error("InsForge not configured") }),
    signUp: async () => ({ data: null, error: new Error("InsForge not configured") }),
    verifyEmail: async () => ({ data: null, error: new Error("InsForge not configured") }),
    signOut: async () => {},
    onAuthStateChange: () => () => {},
  },
  database: {
    from: () => ({
      select: () => ({ eq: () => ({ order: async () => ({ data: [], error: null }) }) }),
      insert: async () => ({ data: null, error: null }),
    }),
  },
  realtime: {
    subscribe: async () => {},
    unsubscribe: async () => {},
    on: () => {},
  },
};

export const insforge: any = client ?? fallback;
