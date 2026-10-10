"use client";

import React, { createContext, useContext, useEffect, useState, useCallback } from "react";
import { useRouter, usePathname } from "next/navigation";
import { api, tokenStorage, orgStorage } from "@/lib/api-client";

export interface AuthUser {
  id: string;
  email: string;
  name: string;
  role?: string;
  avatar_url?: string;
  organization_id?: string;
}

interface AuthContextType {
  user: AuthUser | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const router = useRouter();
  const pathname = usePathname();

  const isAuthRoute = pathname === "/login" || pathname === "/signup" || pathname.startsWith("/forgot-password") || pathname.startsWith("/reset-password");
  const isAppRoute = pathname.startsWith("/app");

  const refreshUser = useCallback(async () => {
    if (tokenStorage.isDemoMode()) {
      setUser({
        id: "usr_demo_01",
        email: "admin@certiflow.io",
        name: "Admin User",
        role: "owner",
      });
      setIsLoading(false);
      return;
    }

    try {
      const resp = await api.auth.me();
      const u = (resp as any)?.user || resp;
      setUser(u);
    } catch {
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshUser();
  }, [refreshUser]);

  // Auth redirection logic based on verified server session (P13.1)
  useEffect(() => {
    if (isLoading) return;

    const authenticated = !!user || tokenStorage.isDemoMode();

    if (isAppRoute && !authenticated) {
      router.push(`/login?redirect=${encodeURIComponent(pathname)}`);
    } else if (isAuthRoute && authenticated) {
      router.push("/app");
    }
  }, [isLoading, user, pathname, isAppRoute, isAuthRoute, router]);

  const logout = async () => {
    try {
      await api.auth.logout();
    } catch {
      // ignore
    } finally {
      tokenStorage.clearTokens();
      orgStorage.clearOrgId();
      setUser(null);
      router.push("/login");
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user || tokenStorage.isAuthenticated(),
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
