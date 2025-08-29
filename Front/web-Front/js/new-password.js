document.addEventListener("DOMContentLoaded", () => {
  const API_URL = "https://pagina-web-finansas-b6474cfcee14.herokuapp.com/api/auth/password-reset-confirm/";
  const form = document.getElementById("newPassForm");
  const messageDiv = document.getElementById("message");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const newPassword = document.getElementById("newPassword").value.trim();
    const confirmPassword = document.getElementById("confirmPassword").value.trim();
    const email = sessionStorage.getItem("resetEmail");
    const token = sessionStorage.getItem("resetToken");

    if (!newPassword || !confirmPassword || !email || !token) {
      messageDiv.style.color = "red";
      messageDiv.textContent = "Faltan datos para cambiar la contraseña";
      return;
    }

    if (newPassword !== confirmPassword) {
      messageDiv.style.color = "red";
      messageDiv.textContent = "❌ Las contraseñas no coinciden";
      return;
    }

    messageDiv.style.color = "black";
    messageDiv.textContent = "Cambiando contraseña...";

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, token, new_password: newPassword })
      });

      const contentType = response.headers.get("content-type");
      let data = {};
      if (contentType && contentType.includes("application/json")) {
        data = await response.json();
      } else {
        const text = await response.text();
        console.error("Respuesta no JSON:", text);
        throw new Error("El servidor respondió HTML, revisa la URL o la configuración del servidor.");
      }

      if (response.ok) {
        messageDiv.style.color = "green";
        messageDiv.textContent = "✅ Contraseña cambiada correctamente. Redirigiendo a login...";
        setTimeout(() => { window.location.href = "index.html"; }, 2000);
      } else {
        messageDiv.style.color = "red";
        messageDiv.textContent = "❌ " + (data.error || "Error cambiando contraseña");
      }

    } catch (err) {
      messageDiv.style.color = "red";
      messageDiv.textContent = "❌ Error de conexión: " + err.message;
    }
  });
});
