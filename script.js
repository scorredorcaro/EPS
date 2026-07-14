// Lógica de Pestañas
        function switchTab(tabId) {
            document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
            
            document.getElementById(tabId).classList.add('active');
            event.currentTarget.classList.add('active');
        }

        // Lógica del Chatbot
        function toggleChat() {
            document.getElementById('chat-window').classList.toggle('open');
        }

        function handleKeyPress(e) {
            if (e.key === 'Enter') sendMessage();
        }

        async function sendMessage() {
            const input = document.getElementById('user-input');
            const messageText = input.value.trim();
            if (!messageText) return;

            // Mostrar mensaje del usuario en pantalla
            appendMessage(messageText, 'user');
            input.value = '';

            try {
                // Conexión dinámica con el backend de Python (Flask)
                const response = await fetch('http://127.0.0.1:5000/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: messageText })
                });
                const data = await response.json();
                
                // Mostrar respuesta del bot
                appendMessage(data.reply, 'bot');

                // Si la cita fue exitosa, la añade dinámicamente a la tabla de inicio
                if(data.appointment) {
                    addAppointmentToTable(data.appointment);
                }
            } catch (error) {
                appendMessage("Lo siento, tengo problemas para conectar con mi servidor. Por favor verifica que el backend de Python esté ejecutándose.", 'bot');
            }
        }

        function appendMessage(text, sender) {
            const chatBox = document.getElementById('chat-box');
            const msgDiv = document.createElement('div');
            msgDiv.classList.add('msg', sender);
            msgDiv.innerText = text;
            chatBox.appendChild(msgDiv);
            chatBox.scrollTop = chatBox.scrollHeight;
        }

        function addAppointmentToTable(app) {
            const tbody = document.querySelector('#citas-table tbody');
            const row = document.createElement('tr');
            row.innerHTML = `<td>${app.specialty}</td><td>${app.doctor}</td><td>${app.date}</td>`;
            tbody.appendChild(row);
        }