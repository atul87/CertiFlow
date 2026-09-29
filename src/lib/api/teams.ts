import { apiRequest } from "./client";
import { Member, Invitation, Role, MemberRole } from "@/types";

export const teamsApi = {
  listMembers: () => apiRequest<Member[]>("/api/v1/members"),

  updateMemberRole: (memberId: string, role: MemberRole) =>
    apiRequest<Member>(`/api/v1/members/${memberId}`, {
      method: "PATCH",
      body: JSON.stringify({ role }),
    }),

  removeMember: (memberId: string) =>
    apiRequest(`/api/v1/members/${memberId}`, { method: "DELETE" }),

  listInvitations: () => apiRequest<Invitation[]>("/api/v1/invitations"),

  inviteMember: (
    emailOrPayload: string | { email: string; role: MemberRole },
    maybeRole?: MemberRole
  ) => {
    const payload =
      typeof emailOrPayload === "string"
        ? { email: emailOrPayload, role: maybeRole || "member" }
        : emailOrPayload;

    return apiRequest<Invitation>("/api/v1/invitations", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  cancelInvite: (invitationId: string) =>
    apiRequest(`/api/v1/invitations/${invitationId}`, { method: "DELETE" }),

  resendInvite: (invitationId: string) =>
    apiRequest(`/api/v1/invitations/${invitationId}/resend`, { method: "POST" }),

  listRoles: () => apiRequest<Role[]>("/api/v1/roles"),
};
