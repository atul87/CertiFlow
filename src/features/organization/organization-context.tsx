"use client";

import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import { api, tokenStorage } from "@/lib/api-client";

export interface Organization {
  id: string;
  name: string;
  slug: string;
  role?: "owner" | "admin" | "editor" | "viewer";
  plan?: string;
  logo_url?: string;
  created_at?: string;
}

interface OrganizationContextType {
  organizations: Organization[];
  currentOrganization: Organization | null;
  isLoading: boolean;
  switchOrganization: (orgId: string) => void;
  refreshOrganizations: () => Promise<void>;
}

const OrganizationContext = createContext<OrganizationContextType | undefined>(undefined);

const DEMO_ORGANIZATIONS: Organization[] = [
  {
    id: "org_default_01",
    name: "Acme Academy",
    slug: "acme-academy",
    role: "owner",
    plan: "Growth",
  },
  {
    id: "org_global_02",
    name: "CertiFlow Enterprise",
    slug: "certiflow-enterprise",
    role: "admin",
    plan: "Scale",
  },
  {
    id: "org_staging_03",
    name: "TechSkills Foundation",
    slug: "techskills",
    role: "editor",
    plan: "Starter",
  },
];

export function OrganizationProvider({ children }: { children: React.ReactNode }) {
  const [organizations, setOrganizations] = useState<Organization[]>(DEMO_ORGANIZATIONS);
  const [currentOrganization, setCurrentOrganization] = useState<Organization | null>(DEMO_ORGANIZATIONS[0]);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const syncOrgToStorage = (org: Organization | null) => {
    if (typeof window !== "undefined") {
      if (org) {
        localStorage.setItem("certiflow_org_id", org.id);
      } else {
        localStorage.removeItem("certiflow_org_id");
      }
    }
  };

  const refreshOrganizations = useCallback(async () => {
    if (!tokenStorage.isAuthenticated()) {
      setIsLoading(false);
      return;
    }

    if (tokenStorage.isDemoMode()) {
      setIsLoading(false);
      return;
    }

    try {
      setIsLoading(true);
      const res = await api.organizations.list();
      const orgList: Organization[] = Array.isArray(res) ? res : res ? [res] : DEMO_ORGANIZATIONS;
      if (orgList.length > 0) {
        setOrganizations(orgList);
        const savedId = typeof window !== "undefined" ? localStorage.getItem("certiflow_org_id") : null;
        const matching = orgList.find(o => o.id === savedId) || orgList[0];
        setCurrentOrganization(matching);
        syncOrgToStorage(matching);
      }
    } catch {
      // Fallback to local demo organizations if backend offline
      const savedId = typeof window !== "undefined" ? localStorage.getItem("certiflow_org_id") : null;
      const matching = DEMO_ORGANIZATIONS.find(o => o.id === savedId) || DEMO_ORGANIZATIONS[0];
      setOrganizations(DEMO_ORGANIZATIONS);
      setCurrentOrganization(matching);
      syncOrgToStorage(matching);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshOrganizations();
  }, [refreshOrganizations]);

  const switchOrganization = useCallback((orgId: string) => {
    const selected = organizations.find(o => o.id === orgId);
    if (selected) {
      setCurrentOrganization(selected);
      syncOrgToStorage(selected);
      // Optional: notify or trigger query refetches
    }
  }, [organizations]);

  return (
    <OrganizationContext.Provider
      value={{
        organizations,
        currentOrganization,
        isLoading,
        switchOrganization,
        refreshOrganizations,
      }}
    >
      {children}
    </OrganizationContext.Provider>
  );
}

export function useOrganization() {
  const context = useContext(OrganizationContext);
  if (!context) {
    throw new Error("useOrganization must be used within an OrganizationProvider");
  }
  return context;
}
