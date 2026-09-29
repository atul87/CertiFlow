import { apiRequest } from "./client";
import { VerificationResult } from "@/types";

export const verificationApi = {
  verify: (certificateId: string, verificationCode: string) =>
    apiRequest<VerificationResult>("/api/v1/public/verify", {
      method: "POST",
      body: JSON.stringify({
        certificate_id: certificateId,
        verification_code: verificationCode,
      }),
    }),

  verifyPublic: (code: string) =>
    apiRequest<VerificationResult>(`/api/v1/public/certificates/${code}`),

  verifyCode: (code: string) =>
    apiRequest<VerificationResult>(`/api/v1/public/certificates/${code}`),

  getVC: (id: string) =>
    apiRequest<any>(`/api/v1/public/credentials/${id}`),

  verifyFile: (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return apiRequest<any>("/api/v1/public/verify/file", {
      method: "POST",
      body: formData,
    });
  },

  verifyPayload: (payload: any) =>
    apiRequest<any>("/api/v1/public/verify/payload", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
};
