import pandas as pd, openpyxl
import customtkinter as ctk
import datetime, os, dotenv, json
import mysql.connector.connection
from config import Config
from tkinter import messagebox as mx
import traceback
import subprocess

dotenv.load_dotenv()
# Configuracion ruta json
with open("rutas.json", "r") as archivo:
    rutas = json.load(archivo)
    
def escribir_registro(texto):
    # Creamos una carpeta aparte para los registros
    carpeta = "Registro"
    path_carpeta = f"{rutas['Output']}{carpeta}"

    if not os.path.exists(path_carpeta):
        os.makedirs(path_carpeta)
        print("Se creo correcctamente la carpeta registro")
    # Escribimos los errores en la carpeta que creamos
    with open(f"{path_carpeta}/registro.txt", "a",encoding="utf-8") as registro:
        otros = registro.write(f"{texto}\n")


def escribir_errores (funcion, texto):
    # Creamos una carpeta aparte para los errores
    carpeta = "Errores"
    path_carpeta = f"{rutas['Output']}{carpeta}"
    if not os.path.exists(path_carpeta):
        os.makedirs(path_carpeta)
        print("Se creo correcctamente la carpeta errores")
    # Escribimos los errores en la carpeta que creamos
    with open(f"{path_carpeta}/reporte_de_errores.txt", "a", encoding="utf-8") as registro:
        error = registro.write(f"{funcion} {texto}")

def obtener_hora_actual ():
    now = datetime.datetime.now() 
    now = datetime.datetime.strftime(now, "%Y-%m-%d %H:%M:%S")
    return now

def vpn_activa(ip_servidor):
    resultado = subprocess.run(["ping", "-n", "1", ip_servidor], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return resultado.returncode == 0

escribir_registro("\n\n")
escribir_errores("","\n\n")

class ProcesamientoDeInformacion:
    def __init__(self, file_name):
        self.df = pd.read_excel(f"{rutas['input']}Novedades {file_name}.xlsx") # Consumimos el documento generado en el script anterior
        self.df = self.df[Config.columnas_a_filtrar]

        self.host = os.getenv('DB_HOST')
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASS")
        self.database = os.getenv("DB_DATABASE")

        self.resultado_novedades = []
        self.errores_novedades = []

    def extraccion_dataset (self, tabla, query, columnas):
        try:
            cnx = conexion_db(self.host, self.user, self.password, self.database) # Conexion con base de datos
            resultado = extraccion_de_datos(cnx, query, tabla) # Extraccion de resultado
            if len(resultado) > 0:
                mx.showerror("Exportacion de datos", "La consulta a la tabla payroll vino vacia")
                exit()
                self.df_payroll = pd.DataFrame(resultado, columns=columnas) # Conversion del dataset en dataframe
                print(self.df_payroll)
        except Exception as error_conexion:
            now = obtener_hora_actual()
            escribir_errores(f"[{now}] Extraccion dataset", f"{now}")
            exit()

    def procesamiento_payroll(self, codificado, codigo_empresa, year, month, tipo_pago):
        try:    
            info_recolectada_payroll = []
            for index, row in self.df_payroll.iterrows():
                if row['codigo'] in codificado:
                    codigo = row['codigo'] 
                    info_recolectada_payroll.append({
                        "Empresa" : codigo_empresa,
                        "Legajo" : row['legajo'],
                        "Periodo" : year,
                        "Mes" : month,
                        "Concepto" : codificado[codigo],
                        "Tipo" : tipo_pago,
                        "Forzado" : 0,
                        "Cantidad" : 1
                    })

            self.df_payroll = pd.DataFrame(info_recolectada_payroll)
            self.df_payroll = self.df_payroll.groupby(by=['Empresa', 'Legajo','Periodo', 'Mes', 'Concepto', 'Tipo', 'Forzado'])["Cantidad"].sum().reset_index()
            now = obtener_hora_actual()
            escribir_registro(f"[{now}] ✅ Se codifico correctamente el dataset extraido de payroll")
        except Exception as error:
            escribir_registro("Ha ocurrido un error en el procesamiento del reporte payroll - (procesamiento_payroll)")
    def procesamiento_novedades(self, year, month, codificado):
        for i, fila in self.df.iterrows():
            for col in self.df.columns[1:]:
                try:  # Salteamos la primera columna (ID)
                    if pd.notna(fila[col]):
                        self.resultado_novedades.append({
                            "Empresa" : Config.codigo_empresa,
                            "Legajo" : fila['Legajo'],
                            "Periodo" : year,
                            "Mes" : month,
                            "Concepto" : codificado[col],
                            "Tipo" : Config.tipo_pago,
                            "Forzado" : 0,
                            "Cantidad" : fila[col]
                        })
                except Exception as error_codificacion:
                    self.errores_novedades.append({
                        "Legajo" : fila['Legajo'],
                        "Codigo" : col
                    })
                    # Captamos el error en una variable para poder imprimirlo en el registro de errores
                    error_novedades_captado = error_codificacion
            
        if len(self.errores_novedades) > 0:
            now = datetime.datetime.now()
            date = datetime.datetime.strftime(now, "%Y-%m-%d")
            df = pd.DataFrame(self.errores_novedades)
            df.to_excel(f"Procesamiento_novedades{date}.xlsx", engine='openpyxl', index=False)
            escribir_errores(f"[{now} procesamiento_novedades]", error_novedades_captado)
            mx.showwarning("Advertencia", "Algunos valores no han sido extraidos del reporte de novedades")
        else:
            now = obtener_hora_actual()
            escribir_registro(f"[{now}] ✅ Se codifico correctamente el dataset extraido de novedades")
        
        self.df_novedades = pd.DataFrame(self.resultado_novedades)
        if len(self.df_novedades) > 0:
            self.df_novedades['Legajo'] = self.df_novedades['Legajo'].astype(int)
            self.df_novedades['Cantidad'] = self.df_novedades['Cantidad'].astype(int)


    def exportacion_reporte(self, file_name):
        try:    
            df_final = pd.concat([self.df_payroll, self.df_novedades],axis=0)
            df_final = df_final.groupby(by=['Empresa', 'Legajo','Periodo', 'Mes', 'Concepto', 'Tipo', 'Forzado'])['Cantidad'].sum().reset_index()
            escribir_registro(f"> Se obtuvieron {len(self.df_novedades)} filas de novedades")
            escribir_registro(f"> Se obtuvieron {len(self.df_payroll)} filas de payroll")
            escribir_registro(f"> Se obtuvieron {len(df_final)} filas totales")
            if len(self.df_payroll) > 0 and len(self.df_novedades) > 0: # Corroboramos que ambos df tengan informacion
                df_final.to_excel(f"{rutas['Output']}E-Sueldos {file_name}.xlsx", index= False)
                escribir_registro(" - El proceso finalizo exitosamente - ")
                mx.showinfo("Exportacion completa", f"Se exporto correctamente el archivo {file_name} en el directorio {rutas['input']}")
            else:
                exit() # En caso de que no salimos del programa
        except Exception as error_exportacion:
            escribir_registro("Ocurrio un error a la hora de exportar el registo")
            escribir_errores("exportacion_reporte", f"{error_exportacion}\n")


def conexion_db(host, user, password, database):
    try:
        cnx = mysql.connector.connect(host= host, user=user, password=password, database=database)
        print("Conexion exitosa a base de datos")
        now = obtener_hora_actual()
        escribir_registro(f"[{now}] ✅ Conexion exitosa a base de datos")
        return cnx
    except Exception as conection_error:
        print(f"Se produjo un error al intentar conectarse a base de datos: \n{conection_error}")
        now = obtener_hora_actual()
        escribir_registro(f"[{now}] ❌ Ocurrio un error al conectarse a base de datos")

def extraccion_de_datos (cnx, query, tabla):
    try:
        cursor = cnx.cursor()
        cursor.execute(query)
        resultado = cursor.fetchall()
        if len(resultado) == 0:
            print("Advertencia. La consulta no trajo informacion") 
        cursor.close()
        cnx.close()
        now = obtener_hora_actual()
        escribir_registro(f"[{now}] ✅ Se extrajo correctamente la informacion a base de datos")
        print("Se extrajo la informacion correctamente de base de datos")
        return resultado
    except Exception as extract_error:
        now = obtener_hora_actual()
        print(f"Se produjo un error al extraer la informacion de base de datos {extract_error}\n {query}")
        escribir_registro(f"[{now}]❌ Ocurrio un error al extraer los datos de la tabla {tabla}")


def main (input_month, input_year):
    # Mesaje de aviso que informe que tiene que estar encendida la vpn y anteriormente realizada las novedades
    condicional_proceso = mx.askquestion("Verificaciones", "Recorda que para que funcione esta automatizacion, anteriormente debes ejecutar el programa de novedades. Si ya tenes realizada dicha planilla, recorda que tenes que tener encendida la VPN antes de ejecutar\n\n ¿Esta todo ok?¿Desea continuar?")
    if condicional_proceso is False:
        exit()
    # obtencion de valores ingresados en interfaz
    try:
        month = int(input_month.get())            
        year = int(input_year.get()) # Obtenemos el año ingresado por usuario
        date = datetime.datetime.strptime(f"{year}-{month}", "%Y-%m") # Convertimos los valores a tipo datetme
        month_str = datetime.datetime.strftime(date, "%B") # Obtenemos el nombre del mes en cuestion
        file_name = f"{month_str} {year}" # Nombre del archivo a procesar
    except Exception as error:
        mx.showerror("Obtencion de datos", "Ha ocurrido un error al procesar los datos ingresados. Corrobore los datos e intente nuevamente. En caso de que el problema persista, contacte al administrador del programa")
        now = obtener_hora_actual()
        traceback.print_exc()
        escribir_errores(f"[{now}][Creacion de variable file_name]", f"{type(error)}Ocurrio un error al intentar procesar la informacion ingresada por el usuario - Mensaje de error {error}")
    
    if not vpn_activa("172.16.20.15"):
        print("❌ No estás conectado a la VPN. Conectate antes de ejecutar el programa.")
        mx.showerror("Error de conexion", "No se obtuvo informacion de la base de datos. En caso de usar VPN, revise la conexion y si esta conectada, presione reconectar e intente nuevamente")
        exit()

    # Procesamiento de informacion
    try:
        query = Config.query_payroll(month, year)
        procesador = ProcesamientoDeInformacion(file_name)
        procesador.extraccion_dataset("payroll", query, Config.columnas_payroll)
        procesador.procesamiento_payroll(Config.codificado, Config.codigo_empresa, year, month, Config.tipo_pago)
        procesador.procesamiento_novedades(year, month, Config.codificado)
        procesador.exportacion_reporte(file_name)
    
    except FileNotFoundError as file_no_encontrado:
        mx.showerror("Archivo no encontrado", f"No se encontro el archivo {rutas['input']}Novedades {file_name}.xlsx. Recorda que antes de ejecutar este programa, tenes que realizar las novedades")   
    except Exception as error:
        now = obtener_hora_actual()
        escribir_errores(f"[{now}][Funcion Main - Procesamiento]", f"{error}\n")
        mx.showerror("Error", "Ha ocurrido un error en el procesamiento del reporte. Por favor, contactar con el administrador del programa")


if __name__ == '__main__':
    # Mesaje de aviso que informe que tiene que estar encendida la vpn y anteriormente realizada las novedades
    """ VENTANA PRINCIPAL """
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    ventana_principal = ctk.CTk()
    ventana_principal.title("Administracion de Personal - Ventana Principal")
    ventana_principal.geometry("700x400")

    # titulo
    label_title = ctk.CTkLabel(ventana_principal, text="Automatizacion E-Sueldos", font=("helvetica", 24, "bold"))
    label_title.pack(pady=35, padx=5)

    # frame_mes 
    frame_mes = ctk.CTkFrame(ventana_principal, fg_color="#2C2F33")
    frame_mes.pack(pady=15, padx=5)
    input_month = ctk.CTkEntry(frame_mes, placeholder_text="Mes (Ej: 5)",fg_color="#2C2F33" )
    input_month.pack(pady=1, padx=1)
    # frame_año 
    frame_año = ctk.CTkFrame(ventana_principal, fg_color="#2C2F33")
    frame_año.pack(pady=15, padx=5)
    input_year = ctk.CTkEntry(frame_año, placeholder_text="Año (Ej: 2025)", fg_color="#2C2F33")
    input_year.pack(pady=2, padx=2)

    frame_button = ctk.CTkFrame(ventana_principal, fg_color="#6A0DAD")
    frame_button.pack(pady=60, padx=5)
    button_continue = ctk.CTkButton(frame_button, text="Ejecutar",fg_color="#2C2F33", command=lambda: main(input_month, input_year))
    button_continue.pack(pady=2, padx=2)

    ventana_principal.bind("<Return>", lambda event: main(input_month, input_year))

    ventana_principal.mainloop()



