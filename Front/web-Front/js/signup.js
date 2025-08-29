document.getElementById("signup-btn").addEventListener("click", async function () {
    const email = document.getElementById("email").value;
    const firstName = document.getElementById("firstname").value;
    const lastName = document.getElementById("lastname").value;
    const birthday = document.getElementById("birthday").value;
    const phone = document.getElementById("phone").value;
    const country = document.getElementById("country").value;
    const password = document.getElementById("password").value;
    const confirmPassword = document.getElementById("confirm-password").value;

    // Validación básica
    if (!email || !birthday || !phone || !country || !password || !confirmPassword) {
        alert("Por favor completa todos los campos obligatorios.");
        return;
    }

    if (password !== confirmPassword) {
        alert("Las contraseñas no coinciden.");
        return;
    }

    // Objeto de datos requerido por la API
    const data = {
        email: email,
        password: password,
        birthday: birthday,
        phone: phone,
        country: country,
        first_name: firstName || "",
        last_name: lastName || ""
    };

    try {
        const response = await fetch("https://pagina-web-finansas-b6474cfcee14.herokuapp.com/api/auth/register/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            alert("Cuenta creada con éxito. Serás redirigido al login.");
            window.location.href = "index.html";
        } else {
            const errorData = await response.json();
            alert("Error: " + JSON.stringify(errorData));
        }
    } catch (error) {
        console.error("Error en la solicitud:", error);
        alert("Error en la conexión con el servidor.");
    }
});
