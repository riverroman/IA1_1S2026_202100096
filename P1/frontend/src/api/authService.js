export const login = (username, password) => {
  if (username === "admin" && password === "admin123") {
    const user = { role: "ADMIN", name: "Administrador" };
    localStorage.setItem("user", JSON.stringify(user));
    return true;
  }
  return false;
}
