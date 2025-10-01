import React, { createContext, useContext, useState, useEffect } from "react";
import jwtDecode from "jwt-decode";

const AuthCtx = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(localStorage.getItem("token"));
  const [user, setUser] = useState(token ? jwtDecode(token) : null);

  useEffect(() => {
    if (token) {
      localStorage.setItem("token", token);
      setUser(jwtDecode(token));
    } else {
      localStorage.removeItem("token");
      setUser(null);
    }
  }, [token]);

  return <AuthCtx.Provider value={{ token, setToken, user }}>{children}</AuthCtx.Provider>;
}

export function useAuth() {
  return useContext(AuthCtx);
}
