document.addEventListener("DOMContentLoaded", () => {
  const token = sessionStorage.getItem("authToken");

  if (!token) {
    window.location.href = "index.html";
    return;
  }

  // GET /me con Bearer
  fetch("https://pagina-web-finansas-b6474cfcee14.herokuapp.com/api/auth/me/", {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      "Authorization": "Bearer " + token
    }
  })
  .then(res => {
    if (!res.ok) throw new Error("No autorizado");
    return res.json();
  })
  .then(data => {
    document.getElementById("username").textContent = data.first_name || "Usuario";
  })
  .catch(err => {
    console.error("Error al cargar datos:", err);
  });

  // Logout
  const logoutBtn = document.getElementById("logoutBtn");
  logoutBtn.addEventListener("click", () => {
    sessionStorage.removeItem("authToken");
    sessionStorage.removeItem("firstName");
    window.location.href = "index.html";
  });
});
