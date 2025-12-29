import { useState } from "react";
import { apiPost } from "./api";

export interface AuthState {
  role: string | null;
  token: string | null;
  companyName: string | null;
}

export function useAuth() {
  const [state, setState] = useState<AuthState>(() => ({
    role: localStorage.getItem("role"),
    token: localStorage.getItem("token"),
    companyName: localStorage.getItem("companyName"),
  }));

  const login = async (email: string, password: string) => {
    const res = await apiPost<{ access_token: string; role: string; company_name: string }>(
      "/auth/login",
      { email, password }
    );
    localStorage.setItem("token", res.access_token);
    localStorage.setItem("role", res.role);
    localStorage.setItem("companyName", res.company_name);
    setState({ role: res.role, token: res.access_token, companyName: res.company_name });
  };

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("role");
    localStorage.removeItem("companyName");
    setState({ role: null, token: null, companyName: null });
  };

  return { ...state, login, logout };
}
