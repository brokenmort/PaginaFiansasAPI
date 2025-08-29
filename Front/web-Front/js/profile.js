document.addEventListener("DOMContentLoaded", () => {
  const token = sessionStorage.getItem("authToken");
  if (!token) {
    window.location.href = "index.html";
    return;
  }

  // ---- DOM ----
  const inputs = document.querySelectorAll(".profile-input");
  const editBtn = document.getElementById("edit-btn");
  const saveBtn = document.getElementById("save-btn");
  const cancelBtn = document.getElementById("cancel-btn");

  const profileImageInput = document.getElementById("profile_image");
  const profileImage = document.getElementById("profileImage");
  const profileIcon = document.getElementById("profileIcon");
  const chooseBtn = document.querySelector("label.custom-file-upload");

  const confirmModal = document.getElementById("confirmModal");
  const successModal = document.getElementById("successModal");
  const confirmChangesBtn = document.getElementById("confirmChangesBtn");
  const cancelChangesBtn = document.getElementById("cancelChangesBtn");
  const successOkBtn = document.getElementById("successOkBtn");

  const API_BASE = "https://pagina-web-finansas-b6474cfcee14.herokuapp.com";

  // ---- Estado ----
  let originalValues = {};
  let profileImageFile = null;
  let currentImgObjectUrl = null;

  // ---- Helpers UI ----
  function setEditMode(enabled) {
    inputs.forEach((input) => { input.disabled = !enabled; });
    if (editBtn) editBtn.style.display = enabled ? "none" : "inline-block";
    if (saveBtn) saveBtn.style.display = enabled ? "inline-block" : "none";
    if (cancelBtn) cancelBtn.style.display = enabled ? "inline-block" : "none";
    if (chooseBtn) chooseBtn.style.display = enabled ? "inline-flex" : "none";
  }

  if (confirmModal) confirmModal.style.display = "none";
  if (successModal) successModal.style.display = "none";
  setEditMode(false);

  function revokeBlobUrl() {
    if (currentImgObjectUrl) {
      try { URL.revokeObjectURL(currentImgObjectUrl); } catch (_) {}
      currentImgObjectUrl = null;
    }
  }

  // --- Carga inteligente de imagen ---
  // 1) prueba pública (img.src) -> onerror
  // 2) si falla, prueba fetch con Authorization y blob:
  // 3) reintentos (para latencias de propagación) con cache-bust
  async function loadImageSmart(url, { retries = 2, delayMs = 500 } = {}) {
    revokeBlobUrl();

    const tryPublic = () => new Promise((resolve, reject) => {
      const bust = url + (url.includes("?") ? "&" : "?") + "t=" + Date.now();
      profileImage.onload = () => {
        profileImage.style.display = "block";
        profileIcon.style.display = "none";
        resolve("public");
      };
      profileImage.onerror = () => reject(new Error("public-load-failed"));
      profileImage.src = bust;
    });

    const tryAuthBlob = async () => {
      try {
        const res = await fetch(url, { headers: { Authorization: "Bearer " + token } });
        if (!res.ok) throw new Error("HTTP " + res.status);
        const blob = await res.blob();
        currentImgObjectUrl = URL.createObjectURL(blob);
        profileImage.onload = null;
        profileImage.onerror = null;
        profileImage.src = currentImgObjectUrl;
        profileImage.style.display = "block";
        profileIcon.style.display = "none";
        return "auth";
      } catch (e) {
        throw new Error("auth-load-failed: " + e.message);
      }
    };

    // Intento público primero, luego auth si falla.
    try {
      await tryPublic();
      return;
    } catch (_) {
      // público falló, probamos auth
    }

    try {
      await tryAuthBlob();
      return;
    } catch (err1) {
      if (retries > 0) {
        await new Promise(r => setTimeout(r, delayMs));
        return loadImageSmart(url, { retries: retries - 1, delayMs: delayMs * 2 });
      }
      // Ambos métodos fallaron
      profileImage.style.display = "none";
      profileIcon.style.display = "block";
      // Opcional: log de ayuda
      console.warn("No se pudo cargar la imagen de perfil:", err1.message);
    }
  }

  // ---- Cargar perfil ----
  const loadProfile = async () => {
    try {
      const res = await fetch(API_BASE + "/api/auth/me/", {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Bearer " + token,
        },
      });
      if (!res.ok) throw new Error("No autorizado");

      const data = await res.json();

      const display = document.getElementById("displayName");
      if (display) display.textContent = data.first_name || "PROFILE";

      Object.keys(data).forEach((key) => {
        const input = document.getElementById(key);
        if (input && input.type !== "file") {
          const val = data[key] ?? "";
          input.value = typeof val === "string" ? val : String(val);
        }
      });

      if (data.profile_image) {
        const raw = data.profile_image;
        const base =
          typeof raw === "string" && /^https?:\/\//i.test(raw)
            ? raw
            : API_BASE + (String(raw).startsWith("/") ? "" : "/") + String(raw);

        // Guardamos para restauraciones
        sessionStorage.setItem("profileImageUrl", base);
        await loadImageSmart(base, { retries: 2, delayMs: 400 });
      } else {
        profileImage.style.display = "none";
        profileIcon.style.display = "block";
      }

      setEditMode(false);
    } catch (err) {
      alert("❌ No se pudieron cargar los datos: " + err.message);
    }
  };

  // Llamada inicial
  loadProfile();

  // ---- Vista previa al seleccionar nueva imagen ----
  if (profileImageInput) {
    profileImageInput.addEventListener("change", (e) => {
      const file = e.target.files && e.target.files[0];
      if (file) {
        profileImageFile = file;
        revokeBlobUrl();

        const reader = new FileReader();
        reader.onload = (ev) => {
          profileImage.src = ev.target.result;
          profileImage.style.display = "block";
          profileIcon.style.display = "none";
        };
        reader.readAsDataURL(file);
      }
    });
  }

  // ---- Editar perfil ----
  if (editBtn) {
    editBtn.onclick = () => {
      inputs.forEach((input) => {
        originalValues[input.id] = input.value;
        input.disabled = false;
      });
      setEditMode(true);
    };
  }

  // ---- Guardar (abre modal) ----
  if (saveBtn) {
    saveBtn.onclick = () => {
      if (confirmModal) confirmModal.style.display = "flex";
    };
  }

  // ---- Confirmar cambios ----
  if (confirmChangesBtn) {
    confirmChangesBtn.onclick = async () => {
      const formData = new FormData();
      const allowed = new Set(["first_name","last_name","birthday","phone","country"]);

      inputs.forEach((input) => {
        if (allowed.has(input.id)) formData.append(input.id, input.value);
      });

      if (profileImageFile) formData.append("profile_image", profileImageFile);

      try {
        const res = await fetch(API_BASE + "/api/auth/me/", {
          method: "PUT",
          headers: { Authorization: "Bearer " + token },
          body: formData,
        });

        if (!res.ok) throw new Error("Error al guardar cambios");

        // Limpiar selección local y cerrar modal
        profileImageFile = null;
        if (profileImageInput) profileImageInput.value = "";
        if (confirmModal) confirmModal.style.display = "none";

        // Recargar perfil (esto actualizará la URL y reintentará imagen)
        await loadProfile();

        if (successModal) successModal.style.display = "flex";
      } catch (err) {
        alert("❌ " + err.message);
        if (confirmModal) confirmModal.style.display = "none";
      }
    };
  }

  // ---- Cancelar en el modal de confirmación ----
  if (cancelChangesBtn) {
    cancelChangesBtn.onclick = () => {
      if (confirmModal) confirmModal.style.display = "none";
    };
  }

  // ---- Aceptar en el modal de éxito ----
  if (successOkBtn) {
    successOkBtn.onclick = () => {
      if (successModal) successModal.style.display = "none";
      setEditMode(false);
    };
  }

  // ---- Cancelar edición (sin perder imagen del servidor) ----
  if (cancelBtn) {
    cancelBtn.onclick = () => {
      inputs.forEach((input) => {
        input.value = originalValues[input.id];
        input.disabled = true;
      });

      // Si estaba en vista previa local, restauramos la del servidor
      if (profileImageFile) {
        profileImageFile = null;
        if (profileImageInput) profileImageInput.value = "";
        const saved = sessionStorage.getItem("profileImageUrl");
        if (saved) {
          loadImageSmart(saved, { retries: 1, delayMs: 300 });
        } else {
          profileImage.style.display = "none";
          profileIcon.style.display = "block";
        }
      }

      setEditMode(false);
    };
  }

  // ---- Limpieza al salir ----
  window.addEventListener("beforeunload", () => {
    revokeBlobUrl();
  });
});
