from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import EmailStr
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

app = FastAPI()

# Ruta para la URL raíz
@app.get("/")
def read_root():
    return {"message": "Bienvenido a la API de Cotización. Usa /send-email-with-pdf/ para enviar un correo."}

# Función para enviar correo electrónico con un PDF adjunto
def send_email(to_email: str, subject: str, body: str, pdf_file: UploadFile):
    from_email = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASSWORD")
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT", 587))

    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email

    # Agregar cuerpo del mensaje
    msg.attach(MIMEText(body, "plain"))

    # Procesar y adjuntar el archivo PDF
    try:
        pdf_data = pdf_file.file.read()
        part = MIMEApplication(pdf_data, Name=pdf_file.filename)
        part['Content-Disposition'] = f'attachment; filename="{pdf_file.filename}"'
        msg.attach(part)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar el PDF: {str(e)}")

    # Enviar el correo
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(from_email, password)
            server.sendmail(from_email, to_email, msg.as_string())
    except smtplib.SMTPException as e:
        raise HTTPException(status_code=500, detail=f"Error al enviar el correo: {str(e)}")

# Endpoint para enviar el correo con el PDF adjunto
@app.post("/send-email-with-pdf/")
def send_custom_email_with_pdf(
    nombre: str = Form(...),
    apellido: str = Form(...),
    correo: EmailStr = Form(...),
    area: str = Form(...),
    cotizacion: float = Form(...),
    pdf_file: UploadFile = File(...)
):
    subject = f"Cotización para {area}"
    body = (f"Hola {nombre} {apellido},\n\n"
            f"Gracias por tu interés en nuestro servicio. Adjunto encontrarás la cotización para el área de {area} "
            f"con un valor de ${cotizacion}.\n\nSaludos cordiales.")

    send_email(correo, subject, body, pdf_file)
    
    return {"message": "Correo con PDF enviado exitosamente"}
