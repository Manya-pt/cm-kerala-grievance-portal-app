// Keeps the logged-in user available to every page.
import { createContext, useContext, useState } from "react";
import api from "./api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem("user"));
    } catch {
      return null;
    }
  });

  const saveSession = ({ token, user }) => {
    localStorage.setItem("token", token);
    localStorage.setItem("user", JSON.stringify(user));
    setUser(user);
    return user;
  };

  const login = async (email, password) =>
    saveSession((await api.post("/auth/login", { email, password })).data);

  const register = async (form) => saveSession((await api.post("/auth/register", form)).data);

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout }}>{children}</AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);

export const dashboardPath = (role) =>
  ({ citizen: "/citizen", cmo: "/cmo", officer: "/officer" })[role] || "/";
