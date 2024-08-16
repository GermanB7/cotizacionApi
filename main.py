from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
import smtplib
from email.mime.text import MIMEText

app = FastAPI()

class UserData(BaseModel):
    nombre: str
    apellido: str
    correo: EmailStr
    area: str
    cotizacion: float

def send_email(to_email: str, subject: str, body: str):
    from_email = "tu_correo@example.com"  # Cambia esto por tu correo real
    password = "tu_contraseña"  # Cambia esto por tu contraseña real

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email

    try:
        with smtplib.SMTP("smtp.example.com", 587) as server:  # Cambia smtp.example.com por tu servidor SMTP
            server.starttls()
            server.login(from_email, password)
            server.sendmail(from_email, to_email, msg.as_string())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al enviar el correo: {str(e)}")

@app.post("/send-email/")
def send_custom_email(user_data: UserData):
    subject = f"Cotización para {user_data.area}"
    body = f"Hola {user_data.nombre} {user_data.apellido},\n\nGracias por tu interés en nuestro servicio. La cotización para el área de {user_data.area} es de ${user_data.cotizacion}.\n\nSaludos cordiales."
    
    send_email(user_data.correo, subject, body)
    
    return {"message": "Correo enviado exitosamente"}
