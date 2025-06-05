from telegram.ext import Application, ContextTypes, MessageHandler, filters, CommandHandler
from telegram import Update
import asyncio # Importar asyncio para ejecutar la función principal
import json # Importar el módulo json para trabajar con archivos JSON
import os # Importar el módulo os para la ruta del archivo

# Define la ruta al archivo JSON que contendrá los nombres permitidos
# Se asume que el archivo 'nombres_permitidos.json' está en el mismo directorio que el script.
NOMBRES_FILE = "nombres_permitidos.json"
NOMBRES_PERMITIDOS = [] # Inicializar la lista, se llenará desde el JSON

# Función para cargar los nombres desde el archivo JSON
def cargar_nombres_desde_json(file_path):
    # Verificar si el archivo existe
    if not os.path.exists(file_path):
        print(f"Error: El archivo '{file_path}' no se encontró. Creando uno vacío.")
        # Crear un archivo JSON vacío si no existe
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump([], f) # Guardar una lista vacía
        return [] # Retornar una lista vacía

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            nombres = json.load(f)
            if not isinstance(nombres, list):
                print(f"Advertencia: El archivo '{file_path}' no contiene una lista JSON válida. Asegúrate de que el contenido sea un array de cadenas.")
                return []
            return nombres
    except json.JSONDecodeError:
        print(f"Error: No se pudo decodificar el JSON de '{file_path}'. Asegúrate de que el formato sea válido.")
        return []
    except Exception as e:
        print(f"Error al cargar el archivo '{file_path}': {e}")
        return []

# Define la función asíncrona para el comando /start
# Esta función mostrará las instrucciones al usuario
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = (
        "¡Hola! Soy tu bot de verificación de usuarios y nombres de webcams estafadoras.\n\n"
        "Para usarme, simplemente escribe un nombre o usuario (sin @) y yo te diré si se encuentra en mi lista de nombres de 'ESTAFADORAS'.\n\n"
        "Si el nombre no está en la lista pero tiene al menos 3 caracteres, te mostraré sugerencias de nombres similares."
    )
    await update.message.reply_text(welcome_message)

# Define la función asíncrona para verificar el nombre
# Esta función será llamada cuando el bot reciba un mensaje de texto
async def verificar_nombre(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Obtener el texto del mensaje del usuario y convertirlo a minúsculas para una comparación sin distinción entre mayúsculas y minúsculas
    nombre_usuario = update.message.text.strip().lower()

    # Convertir los nombres de la lista de permitidos (cargada desde JSON) a minúsculas para la comparación
    nombres_permitidos_lower = [nombre.lower() for nombre in NOMBRES_PERMITIDOS]

    # Verificar si el nombre del usuario está en la lista de nombres permitidos
    if nombre_usuario in nombres_permitidos_lower:
        respuesta = "ESTAFADORA"
    else:
        # Si el nombre no está en la lista
        if len(nombre_usuario) >= 3:
            # Buscar nombres en la lista que contengan el texto ingresado por el usuario
            sugerencias = [
                nombre_original for nombre_original, nombre_lower in zip(NOMBRES_PERMITIDOS, nombres_permitidos_lower)
                if nombre_usuario in nombre_lower
            ]

            if sugerencias:
                # Si se encuentran sugerencias, listarlas con un salto de línea adicional antes
                respuesta = "NO SE ENCUENTRA EN LA LISTA.\n\nQuizás quisiste decir:\n" + "\n".join(sugerencias)
            else:
                # Si no hay sugerencias, mantener el mensaje original
                respuesta = "NO SE ENCUENTRA EN LA LISTA"
        else:
            # Si el texto es menor a 3 caracteres y no se encuentra, mantener el mensaje original
            respuesta = "NO SE ENCUENTRA EN LA LISTA"

    # Responder al usuario con la respuesta generada
    await update.message.reply_text(respuesta)

# Define la función principal para configurar y ejecutar el bot
def main():
    global NOMBRES_PERMITIDOS # Declarar NOMBRES_PERMITIDOS como global para modificarla

    # Cargar los nombres desde el archivo JSON al iniciar el bot
    NOMBRES_PERMITIDOS = cargar_nombres_desde_json(NOMBRES_FILE)
    if not NOMBRES_PERMITIDOS:
        print("La lista de nombres permitidos está vacía o hubo un error al cargarla. El bot funcionará, pero no encontrará ningún nombre.")
        print("Asegúrate de crear un archivo 'nombres_permitidos.json' con el formato: [\"nombre1\", \"nombre2\", \"nombre3\"]")

    # Tu token de bot de Telegram. Asegúrate de que sea correcto y seguro.
    bot_token = "8150668407:AAGJIVm4LQekjFRB1Ya_X9AsJHppZet6YJ4"

    # Crea el constructor de la aplicación con tu token de bot
    bot_app = Application.builder().token(bot_token).build()

    # Agrega un manejador de comandos para /start
    bot_app.add_handler(CommandHandler("start", start))

    # Agrega un manejador de mensajes:
    # Escucha los mensajes de texto que no son comandos (ej. no /start)
    # Cuando se recibe un mensaje de este tipo, llama a la función 'verificar_nombre'
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, verificar_nombre))

    # Inicia el bot. Esto consultará las actualizaciones de Telegram y se ejecutará indefinidamente.
    # allowed_updates=Update.ALL_TYPES asegura que se procesen todos los tipos de actualizaciones.
    bot_app.run_polling(allowed_updates=Update.ALL_TYPES)

# Este es el punto de entrada estándar de Python.
# Asegura que main() se llame solo cuando el script se ejecuta directamente.
if __name__ == "__main__":
    # Llama a la función principal para iniciar el bot
    main()
