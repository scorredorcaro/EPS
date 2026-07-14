// Tab switching logic
        function switchTab(tab) {
            const tabs = document.querySelectorAll('.tab-btn');
            const panels = document.querySelectorAll('.form-panel');
            const alertBox = document.getElementById('alert-box');
            
            // Hide alerts when switching
            alertBox.style.display = 'none';

            if (tab === 'login') {
                tabs[0].classList.add('active');
                tabs[1].classList.remove('active');
                document.getElementById('login-panel').classList.add('active');
                document.getElementById('register-panel').classList.remove('active');
            } else {
                tabs[0].classList.remove('active');
                tabs[1].classList.add('active');
                document.getElementById('login-panel').classList.remove('active');
                document.getElementById('register-panel').classList.add('active');
            }
        }

        // Toggle password visibility
        function togglePasswordVisibility(id) {
            const input = document.getElementById(id);
            const icon = input.nextElementSibling;
            if (input.type === 'password') {
                input.type = 'text';
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            } else {
                input.type = 'password';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            }
        }

        // Handle show alerts
        function showAlert(message, type) {
            const alertBox = document.getElementById('alert-box');
            const alertIcon = document.getElementById('alert-icon');
            const alertMessage = document.getElementById('alert-message');

            alertBox.className = 'alert'; // reset
            alertBox.classList.add(type === 'success' ? 'alert-success' : 'alert-error');
            
            alertIcon.className = 'fa-solid';
            alertIcon.classList.add(type === 'success' ? 'fa-circle-check' : 'fa-triangle-exclamation');
            
            alertMessage.textContent = message;
            alertBox.style.display = 'flex';
        }

        // POST URL placeholder (will connect to Flask / Render)
        const BASE_URL = 'https://saludmass-backend.onrender.com/api';
        // Para pruebas locales en tu máquina:
        //const BASE_URL = 'http://127.0.0.1:5000/api';

        // Submit Login handler
        async function handleLogin(e) {
            e.preventDefault();
            const email = document.getElementById('login-email').value.trim();
            const password = document.getElementById('login-password').value;

            try {
                // Temporary simulator or direct call to Render when the endpoints are active
                const response = await fetch(`${BASE_URL}/login`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password })
                });

                const data = await response.json();

                if (response.ok) {
                    showAlert('¡Inicio de sesión exitoso! Redirigiendo...', 'success');
                    // Store token/user session in localStorage
                    localStorage.setItem('user_session', JSON.stringify(data.user));
                    
                    // Redirect to the dashboard page after 1.5 seconds
                    setTimeout(() => {
                        window.location.href = 'index.html';
                    }, 1500);
                } else {
                    showAlert(data.message || 'Credenciales incorrectas.', 'error');
                }
            } catch (error) {
                // Fallback simulator for phase 1 testing (remove once app.py is updated with database)
                console.error("Error conectando con Render:", error);
                showAlert('El backend en Render aún no tiene activada la base de datos de usuarios. Iniciando simulación local de prueba...', 'success');
                
                setTimeout(() => {
                    localStorage.setItem('user_session', JSON.stringify({ name: 'Sebastián Corredor', email: email }));
                    window.location.href = 'index.html';
                }, 2000);
            }
        }

        // Submit Register handler
        async function handleRegister(e) {
            e.preventDefault();
            const name = document.getElementById('reg-name').value.trim();
            const documentNum = document.getElementById('reg-document').value.trim();
            const email = document.getElementById('reg-email').value.trim();
            const password = document.getElementById('reg-password').value;

            try {
                const response = await fetch(`${BASE_URL}/register`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, document: documentNum, email, password })
                });

                const data = await response.json();

                if (response.ok) {
                    showAlert('¡Registro completado con éxito! Ya puedes iniciar sesión.', 'success');
                    document.getElementById('register-form').reset();
                    setTimeout(() => {
                        switchTab('login');
                    }, 2000);
                } else {
                    showAlert(data.message || 'Error al registrar el usuario.', 'error');
                }
            } catch (error) {
                console.error("Error conectando con Render:", error);
                showAlert('El servidor en Render no pudo procesar la solicitud (DB no configurada). Registrando de forma simulada...', 'success');
                
                setTimeout(() => {
                    switchTab('login');
                    document.getElementById('login-email').value = email;
                }, 2000);
            }
        }