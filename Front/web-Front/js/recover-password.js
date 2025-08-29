const API_URL = "https://pagina-web-finansas-b6474cfcee14.herokuapp.com/api/auth/password-reset/";
const form = document.getElementById("resetForm");
const messageDiv = document.getElementById("message");

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const email = document.getElementById("usuario").value.trim();

  if (!email) {
    showMessage("Por favor ingresa un correo válido", "red");
    return;
  }

  showMessage("Enviando código...", "black");

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email })
    });

    const data = await parseJSON(response);

    if (response.ok) {
      sessionStorage.setItem("resetEmail", email);
      showMessage("✅ Te enviamos un código de verificación a tu correo", "green");
      setTimeout(() => { window.location.href = "verify-code.html"; }, 1500);
    } else {
      showMessage("❌ " + (data.detail || data.error || "Error enviando correo"), "red");
    }

  } catch (err) {
    showMessage("❌ Error de conexión: " + err.message, "red");
  }
});

function showMessage(text, color) {
  messageDiv.style.color = color;
  messageDiv.textContent = text;
}

async function parseJSON(response) {
  const contentType = response.headers.get("content-type");
  if (contentType && contentType.includes("application/json")) {
    return await response.json();
  }
  const text = await response.text();
  console.error("Respuesta no JSON:", text);
  throw new Error("El servidor respondió HTML o formato inesperado.");
}
