 Proyecto de Envío de Correos con PDF usando FastAPI y Sendinblue

Este proyecto es una aplicación web desarrollada con FastAPI que permite enviar correos electrónicos con archivos PDF adjuntos utilizando la API de Sendinblue.

## Requisitos Previos

- Python 3.7 o superior
- Una cuenta en Sendinblue
- Clave API de Sendinblue

## Instalación

### 1. Clonar el Repositorio

bash
git clone https://github.com/tu_usuario/tu_repositorio.git
cd tu_repositorio
2. Crear y Activar un Entorno Virtual
En Windows:
bash
Copiar código
python -m venv venv
venv\Scripts\activate
En macOS/Linux:
bash
Copiar código
python3 -m venv venv
source venv/bin/activate
3. Instalar las Dependencias
bash
Copiar código
pip install -r requirements.txt
4. Configurar las Variables de Entorno
Crea un archivo .env en la raíz del proyecto y añade las siguientes variables:


SENDINBLUE_API_KEY=tu_clave_api_de_sendinblue
Asegúrate de reemplazar tu_clave_api_de_sendinblue con tu clave API real obtenida desde tu cuenta de Sendinblue.
