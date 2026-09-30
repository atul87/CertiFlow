import { apiRequest } from "./client";
import { Organization, OrganizationMember } from "@/types";

export const organizationsApi = {
  list: () => apiRequest<Organization>("/api/v1/organizations/me"),

  get: (id: string) => apiRequest<Organization>(`/api/v1/organizations/${id}`),

  getMe: () => apiRequest<Organization>("/api/v1/organizations/me"),

  update: (id: string, payload: Partial<Organization>) =>
    apiRequest<Organization>(`/api/v1/organizations/${id}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    }),

  listMembers: (id: string) =>
    apiRequest<OrganizationMember[]>(`/api/v1/organizations/${id}/members`),
};
