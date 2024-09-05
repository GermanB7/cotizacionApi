import base64
import requests
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from fastapi import FastAPI, HTTPException, Form
from pydantic import EmailStr
from dotenv import load_dotenv
import os

# Cargar las variables de entorno
load_dotenv()

app = FastAPI()

def download_pdf_from_bucket(bucket_link: str):
    """Descargar el archivo PDF desde un enlace público del bucket de Google Cloud."""
    try:
        # Descargar el archivo desde el enlace del bucket
        response = requests.get(bucket_link)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail=f"Error al descargar el archivo desde el bucket: {bucket_link}. Status code: {response.status_code}, Response: {response.text}")
        
        # Retorna el contenido del archivo descargado
        return response.content  
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar el enlace del bucket: {str(e)}")

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

@app.post("/send-email-with-bucket-links/")
def send_custom_email_with_bucket_links(
    nombre: str = Form(...),
    apellido: str = Form(...),
    correo: EmailStr = Form(...),
    area: str = Form(...),
    cotizacion: float = Form(...),
    cotizacion_bucket_link: str = Form(...),
    planos_bucket_link: str = Form(...),
    planos_3d_bucket_link: str = Form(...)
):
    subject_cliente = f"Cotización para {area}"
    body_cliente = (f"Hola {nombre} {apellido},\n\n"
                    f"Gracias por tu interés en nuestro servicio. Adjunto encontrarás la cotización para el área de {area} "
                    f"con un valor de ${cotizacion}.\n\nSaludos cordiales.")

    # Descargar los archivos desde los enlaces del bucket de Google Cloud
    cotizacion_pdf_content = download_pdf_from_bucket(cotizacion_bucket_link)
    planos_pdf_content = download_pdf_from_bucket(planos_bucket_link)
    planos_3d_pdf_content = download_pdf_from_bucket(planos_3d_bucket_link)

    # Crear los archivos adjuntos en formato base64
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
