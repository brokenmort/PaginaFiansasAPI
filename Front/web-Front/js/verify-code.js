document.addEventListener("DOMContentLoaded", () => {
  const API_URL = "https://pagina-web-finansas-b6474cfcee14.herokuapp.com/api/auth/password-verify/";
  const form = document.getElementById("verifyForm");
  const messageDiv = document.getElementById("message");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const token = document.getElementById("code").value.trim();
    const email = sessionStorage.getItem("resetEmail");

    if (!token || !email) {
      messageDiv.style.color = "red";
      messageDiv.textContent = "Faltan datos para verificar";
      return;
    }

    messageDiv.style.color = "black";
    messageDiv.textContent = "Verificando código...";

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, token })
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

      if (response.ok && data.valid) {
        sessionStorage.setItem("resetToken", token);
        messageDiv.style.color = "green";
        messageDiv.textContent = "✅ Código verificado. Redirigiendo...";
        setTimeout(() => { window.location.href = "new-password.html"; }, 1500);
      } else {
        messageDiv.style.color = "red";
        messageDiv.textContent = "❌ Código inválido o expirado";
      }

    } catch (err) {
      messageDiv.style.color = "red";
      messageDiv.textContent = "❌ Error de conexión: " + err.message;
    }
  });
});
