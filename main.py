import base64
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import EmailStr
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

def send_email_via_api(to_email: str, subject: str, body: str, pdf_file: UploadFile):
    try:
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = os.getenv("SENDINBLUE_API_KEY")

        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
        from_email = {"email": "cotizacionescad8@gmail.com"}  # Usar el remitente verificado
        to = [{"email": to_email}]
        
        # Procesar y adjuntar el archivo PDF (codificación base64)
        try:
            pdf_data = base64.b64encode(pdf_file.file.read()).decode('utf-8')
            attachment = [{"content": pdf_data, "name": pdf_file.filename}]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al procesar el PDF: {str(e)}")

        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=to,
            html_content=body,
            sender=from_email,
            subject=subject,
            attachment=attachment
        )

        # Enviar el correo
        try:
            api_response = api_instance.send_transac_email(send_smtp_email)
            print("Correo enviado exitosamente:", api_response)
        except ApiException as e:
            raise HTTPException(status_code=500, detail=f"Error al enviar el correo: {str(e)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en la configuración de la API: {str(e)}")


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

    send_email_via_api(correo, subject, body, pdf_file)
    
    return {"message": "Correo con PDF enviado exitosamente"}
