import {
  LayoutDashboard,
  FileText,
  Upload,
  Zap,
  Archive,
  ShieldCheck,
  Mail,
  BarChart3,
  FileBarChart,
  Users,
  Code2,
  CreditCard,
  Settings,
} from "lucide-react";

export interface NavItemConfig {
  label: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  exact?: boolean;
  permission?: string;
  badge?: string;
}

export interface NavSectionConfig {
  section: string;
  items: NavItemConfig[];
}

export const NAVIGATION_CONFIG: NavSectionConfig[] = [
  {
    section: "Workspace",
    items: [
      {
        label: "Dashboard",
        href: "/app",
        icon: LayoutDashboard,
        exact: true,
        permission: "dashboard:read",
      },
      {
        label: "Templates",
        href: "/app/templates",
        icon: FileText,
        permission: "templates:read",
      },
      {
        label: "Imports",
        href: "/app/imports",
        icon: Upload,
        permission: "imports:read",
      },
      {
        label: "Issuance",
        href: "/app/issuance",
        icon: Zap,
        permission: "issuance:read",
      },
      {
        label: "Certificates",
        href: "/app/certificates",
        icon: Archive,
        permission: "certificates:read",
      },
    ],
  },
  {
    section: "Trust & Delivery",
    items: [
      {
        label: "Digital Credentials",
        href: "/app/credentials",
        icon: ShieldCheck,
        permission: "credentials:read",
      },
      {
        label: "Email",
        href: "/app/email",
        icon: Mail,
        permission: "email:read",
      },
      {
        label: "Analytics",
        href: "/app/analytics",
        icon: BarChart3,
        permission: "analytics:read",
      },
      {
        label: "Reports",
        href: "/app/reports",
        icon: FileBarChart,
        permission: "reports:read",
      },
    ],
  },
  {
    section: "Organization",
    items: [
      {
        label: "Team",
        href: "/app/team",
        icon: Users,
        permission: "team:read",
      },
      {
        label: "Developer",
        href: "/app/developer",
        icon: Code2,
        permission: "developer:read",
      },
      {
        label: "Billing",
        href: "/app/billing",
        icon: CreditCard,
        permission: "billing:read",
      },
      {
        label: "Settings",
        href: "/app/settings",
        icon: Settings,
        permission: "settings:read",
      },
    ],
  },
];
