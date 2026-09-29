export type MemberRole = "owner" | "admin" | "member" | "viewer";

export interface Member {
  id: string;
  user_id: string;
  name: string;
  email: string;
  role: MemberRole;
  joined_at: string;
  last_active?: string;
}

export interface Invitation {
  id: string;
  email: string;
  role: MemberRole;
  status: "pending" | "accepted" | "expired" | "cancelled";
  invited_at: string;
  expires_at: string;
}

export interface Role {
  id: string;
  name: string;
  display_name: string;
  description: string;
  permissions: string[];
  is_system: boolean;
}
