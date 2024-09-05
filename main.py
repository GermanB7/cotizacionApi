import base64
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import EmailStr
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

def process_pdf_file(pdf_file: UploadFile):
    """Función para procesar un archivo PDF y convertirlo en base64."""
    try:
        # Depuración: nombre del archivo
        print(f"Procesando archivo: {pdf_file.filename}")
        
        # Mover el puntero al inicio por si fue leído previamente
        pdf_file.file.seek(0)
        
        # Leer el contenido del archivo y mantenerlo en memoria
        file_content = pdf_file.file.read()
        
        # Depuración: imprimir tamaño del archivo
        print(f"Tamaño del archivo: {len(file_content)} bytes")
        
        if not file_content:
            raise ValueError(f"El archivo {pdf_file.filename} está vacío")
        
        # Convertir el contenido a base64
        pdf_data = base64.b64encode(file_content).decode('utf-8')
        return {"content": pdf_data, "name": pdf_file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar el archivo {pdf_file.filename}: {str(e)}")

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

@app.post("/send-email-with-pdfs/")
def send_custom_email_with_pdfs(
    nombre: str = Form(...),
    apellido: str = Form(...),
    correo: EmailStr = Form(...),
    area: str = Form(...),
    cotizacion: float = Form(...),
    cotizacion_pdf: UploadFile = File(...),
    planos_pdf: UploadFile = File(...),
    planos_3d_pdf: UploadFile = File(...)
):
    subject_cliente = f"Cotización para {area}"
    body_cliente = (f"Hola {nombre} {apellido},\n\n"
                    f"Gracias por tu interés en nuestro servicio. Adjunto encontrarás la cotización para el área de {area} "
                    f"con un valor de ${cotizacion}.\n\nSaludos cordiales.")

    # Procesar y enviar correo al cliente con solo la cotización
    pdf_cotizacion = [process_pdf_file(cotizacion_pdf)]
    send_email_via_api(correo, subject_cliente, body_cliente, pdf_cotizacion)
    
    # Preparar el segundo correo para "cotizacionescad8@gmail.com"
    subject_interno = f"Detalles de cotización para {nombre} {apellido} - {area}"
    body_interno = (f"Se ha registrado una nueva cotización.\n\n"
                    f"Nombre: {nombre} {apellido}\n"
                    f"Correo: {correo}\n"
                    f"Área: {area}\n"
                    f"Cotización: ${cotizacion}\n\n"
                    f"Se adjuntan los archivos de la cotización, planos y planos 3D.")

    # Procesar todos los archivos para el correo interno
    pdf_internos = [
        process_pdf_file(cotizacion_pdf),
        process_pdf_file(planos_pdf),
        process_pdf_file(planos_3d_pdf)
    ]

    # Enviar correo interno con todos los archivos
    send_email_via_api("cotizacionescad8@gmail.com", subject_interno, body_interno, pdf_internos)
    
    return {"message": "Correos enviados exitosamente"}
