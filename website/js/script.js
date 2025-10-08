function previewFile() {
    const file = document.getElementById('fileInput').files[0];
    const reader = new FileReader();

    reader.onload = function(e) {
        document.getElementById('emailContent').value = e.target.result;
    };

    if (file) {
        reader.readAsText(file);
    }
}
async function adminLoginPrompt() {
const email = prompt("Enter admin email:");
if (!email) return alert("Login cancelled.");

const password = prompt("Enter password:");
if (!password) return alert("Login cancelled.");

try {
const response = await fetch('/admin-login-json', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username: email, password: password })
});

const result = await response.json();

if (result.success) {
    window.location.href = "/admin";
} else {
    alert("Login failed: " + result.error);
}
} catch (err) {
alert("An error occurred during login.");
}
}