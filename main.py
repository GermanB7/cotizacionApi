import base64
import requests
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from fastapi import FastAPI, HTTPException, Form
from pydantic import EmailStr
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

def download_pdf_from_drive(drive_link: str):
    """Descargar el archivo PDF desde un enlace de Google Drive."""
    try:
        # Transformar el enlace de Google Drive en un enlace de descarga directo
        if "drive.google.com" in drive_link:
            file_id = drive_link.split("/d/")[1].split("/")[0]
            download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        else:
            raise ValueError("El enlace proporcionado no es válido para Google Drive")

        # Descargar el archivo
        response = requests.get(download_url)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail=f"Error al descargar el archivo desde Google Drive: {drive_link}")

        return response.content  # Devolver el contenido del archivo
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar el enlace de Google Drive: {str(e)}")

def send_email_via_api(to_email: str, subject: str, body: str, attachments: list):
    try:
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = os.getenv("SENDINBLUE_API_KEY")

        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
        from_email = {"email": "cotizacionescad8@gmail.com"}
        to = [{"email": to_email}]

        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=to,
            html_content=body,
            sender=from_email,
            subject=subject,
            attachment=attachments
        )

        try:
            api_response = api_instance.send_transac_email(send_smtp_email)
            print("Correo enviado exitosamente:", api_response)
        except ApiException as e:
            raise HTTPException(status_code=500, detail=f"Error al enviar el correo: {str(e)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en la configuración de la API: {str(e)}")

@app.post("/send-email-with-drive-links/")
def send_custom_email_with_drive_links(
    nombre: str = Form(...),
    apellido: str = Form(...),
    correo: EmailStr = Form(...),
    area: str = Form(...),
    cotizacion: float = Form(...),
    cotizacion_drive_link: str = Form(...),
    planos_drive_link: str = Form(...),
    planos_3d_drive_link: str = Form(...)
):
    subject_cliente = f"Cotización para {area}"
    body_cliente = (f"Hola {nombre} {apellido},\n\n"
                    f"Gracias por tu interés en nuestro servicio. Adjunto encontrarás la cotización para el área de {area} "
                    f"con un valor de ${cotizacion}.\n\nSaludos cordiales.")

    # Descargar los archivos desde los enlaces de Google Drive
    cotizacion_pdf_content = download_pdf_from_drive(cotizacion_drive_link)
    planos_pdf_content = download_pdf_from_drive(planos_drive_link)
    planos_3d_pdf_content = download_pdf_from_drive(planos_3d_drive_link)

    # Crear los archivos adjuntos
    attachments = [
        {"content": base64.b64encode(cotizacion_pdf_content).decode('utf-8'), "name": "Cotización.pdf"},
        {"content": base64.b64encode(planos_pdf_content).decode('utf-8'), "name": "Planos.pdf"},
        {"content": base64.b64encode(planos_3d_pdf_content).decode('utf-8'), "name": "Planos3D.pdf"}
    ]
    
    # Enviar correo al cliente con solo la cotización
    send_email_via_api(correo, subject_cliente, body_cliente, [attachments[0]])
    
    # Preparar el segundo correo para "cotizacionescad8@gmail.com"
    subject_interno = f"Detalles de cotización para {nombre} {apellido} - {area}"
    body_interno = (f"Se ha registrado una nueva cotización.\n\n"
                    f"Nombre: {nombre} {apellido}\n"
                    f"Correo: {correo}\n"
                    f"Área: {area}\n"
                    f"Cotización: ${cotizacion}\n\n"
                    f"Se adjuntan los archivos de la cotización, planos y planos 3D.")

    # Enviar correo interno con todos los archivos
    send_email_via_api("cotizacionescad8@gmail.com", subject_interno, body_interno, attachments)
    
    return {"message": "Correos enviados exitosamente"}
