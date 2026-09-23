const json = async (response: Response) => {
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = body.detail;
    throw new Error(typeof detail === "string" ? detail : detail ? JSON.stringify(detail) : "Error de API");
  }
  return body;
};

export const api = {
  get: (path: string, token?: string) =>
    fetch(path, { headers: token ? { Authorization: `Bearer ${token}` } : {} }).then(json),
  post: (path: string, data?: unknown, token?: string) =>
    fetch(path, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: data ? JSON.stringify(data) : "{}",
    }).then(json),
  patch: (path: string, data: unknown, token: string) =>
    fetch(path, {
      method: "PATCH",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
      body: JSON.stringify(data),
    }).then(json),
  delete: (path: string, token: string) =>
    fetch(path, { method: "DELETE", headers: { Authorization: `Bearer ${token}` } }).then(json),
};

export const storage = {
  playerToken: () => localStorage.getItem("mr_player") || "",
  setPlayerToken: (token: string) => localStorage.setItem("mr_player", token),
  adminToken: () => localStorage.getItem("mr_admin") || "",
  setAdminToken: (token: string) => localStorage.setItem("mr_admin", token),
  clearPlayer: () => localStorage.removeItem("mr_player"),
  clearAdmin: () => localStorage.removeItem("mr_admin"),
};
