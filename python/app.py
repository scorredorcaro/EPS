from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Permite que el HTML local se comunique con el backend sin bloqueos de seguridad

# Memoria temporal para rastrear el estado de la conversación por usuario
# Estructura del flujo: 0 (Esperando Especialidad) -> 1 (Esperando Confirmación de Fecha) -> 2 (Finalizado)
user_session = {
    "step": 0,
    "specialty": None,
    "doctor": None,
    "date": "Próximo lunes - 08:00 AM" # Simulación de asignación de agenda inmediata
}

DOCTORS_MAPPING = {
    "medicina general": "Dra. Eliana Restrepo",
    "odontologia": "Dr. Sergio Barrios",
    "pediatria": "Dra. Amalia Ruiz"
}

@app.route('/api/chat', methods=['POST'])
def chat_hub():
    data = request.json
    user_message = data.get("message", "").strip().lower()
    
    global user_session

    # PASO 0: Selección de Especialidad
    if user_session["step"] == 0:
        found_specialty = None
        for spec in DOCTORS_MAPPING.keys():
            if spec in user_message:
                found_specialty = spec
                break
        
        if found_specialty:
            user_session["specialty"] = found_specialty.title()
            user_session["doctor"] = DOCTORS_MAPPING[found_specialty]
            user_session["step"] = 1
            
            reply = f"Perfecto. Tengo disponibilidad en {user_session['specialty']} con el especialista {user_session['doctor']} para el {user_session['date']}. ¿Te sirve este horario? (Responde con SI o NO)"
            return jsonify({"reply": reply})
        else:
            return jsonify({"reply": "Por favor, indícame una opción válida de las disponibles: Medicina General, Odontología o Pediatría."})

    # PASO 1: Confirmación de agenda o reinicio
    elif user_session["step"] == 1:
        if "si" in user_message or "sí" in user_message:
            user_session["step"] = 0 # Reseteamos el flujo para futuras interacciones
            
            appointment_data = {
                "specialty": user_session["specialty"],
                "doctor": user_session["doctor"],
                "date": user_session["date"]
            }
            
            reply = f"¡Excelente! Tu cita para {appointment_data['specialty']} ha sido agendada con éxito. Ya puedes verla reflejada en tu panel de inicio."
            return jsonify({"reply": reply, "appointment": appointment_data})
        
        elif "no" in user_message:
            user_session["step"] = 0
            return jsonify({"reply": "Entendido. Proceso cancelado. ¿Qué otra especialidad te gustaría consultar?"})
        else:
            return jsonify({"reply": "Por favor responde con 'SI' para confirmar la cita o 'NO' para cancelar el proceso."})

    return jsonify({"reply": "Hola de nuevo. ¿En qué especialidad deseas agendar tu cita?"})

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)