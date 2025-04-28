import pandas as pd, openpyxl
import customtkinter as ctk
import datetime, os, dotenv, json
import mysql.connector.connection
from config import Config
from tkinter import messagebox

dotenv.load_dotenv()
# Configuracion ruta json
with open("rutas.json", "r") as archivo:
    rutas = json.load(archivo)
    
def escribir_registro(texto):
    with open("registro.txt", "a",encoding="utf-8") as registro:
        rutas = registro.write(f"{texto}\n")
escribir_registro("\n\n")

def escribir_errores (funcion, texto):
    with open("reporte_de_errores.txt", "a", encoding="utf-8") as registro:
        error = registro.write(f"[{funcion}] {texto}")

def obtener_hora_actual ():
    now = datetime.datetime.now() 
    return now


class ProcesamientoDeInformacion:
    def __init__(self, file_name):
        self.df = pd.read_excel(f"{rutas['input']}Novedades {file_name}") # Consumimos el documento generado en el script anterior
        self.df = self.df[[Config.columnas_a_filtrar]]

        self.host = os.getenv('DB_HOST')
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASS")

        self.resultado_novedades = []
        self.errores_novedades = []

    def extraccion_dataset (self, database, tabla, query, columnas):
        cnx = conexion_db(self.host, self.user, self.password, database) # Conexion con base de datos
        resultado = extraccion_de_datos(cnx, query, tabla) # Extraccion de resultado
        self.df_payroll = pd.DataFrame(resultado, columns=columnas) # Conversion del dataset en dataframe

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
            self.df_payroll.to_excel(f"{rutas['Output']}procesado database.xlsx", index=False)
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
            
        if len(self.errores_novedades) > 0:
            escribir_errores("procesamiento_novedades", f"Ocurrio un error en los siguientes asesores\n{self.errores_novedades}")
        else:
            now = obtener_hora_actual()
            escribir_registro(f"[{now}] ✅ Se codifico correctamente el dataset extraido de novedades")
        
        self.df_novedades = pd.DataFrame(self.resultado_novedades)
        if len(self.df_novedades) > 0:
            self.df_novedades['Legajo'] = self.df_novedades['Legajo'].astype(int)
            self.df_novedades['Cantidad'] = self.df_novedades['Cantidad'].astype(int)


    def exportacion_reporte(self):
        try:    
            df_final = pd.concat([self.df_payroll, self.df_novedades],axis=0)
            df_final = df_final.groupby(by=['Empresa', 'Legajo','Periodo', 'Mes', 'Concepto', 'Tipo', 'Forzado'])['Cantidad'].sum().reset_index()

            file_name = file_name.replace(".xlsx", "")
            df_final.to_excel(f"{rutas['Output']}E-Sueldos {file_name}.xlsx", index= False)
            escribir_registro(f"> Se obtuvieron {len(self.df_novedades)} filas de novedades")
            escribir_registro(f"> Se obtuvieron {len(self.df_borrar)} filas de payroll")
            escribir_registro(f"> Se exportaron {len(df_final)} filas")
            escribir_registro(" - El proceso finalizo exitosamente - ")
        except Exception as error_exportacion:
            escribir_registro("Ocurrio un error a la hora de exportar el registo")
            escribir_errores("exportacion_reporte", f"{error_exportacion}")

    

def conexion_db(host, user, password, database):
    try:
        cnx = mysql.connector.connect(host= host, user=user, password=password, database=database)
        print("Conexion exitosa a base de datos")
        now = datetime.now()
        escribir_registro(f"[{now}] ✅ Conexion exitosa a base de datos")
        return cnx
    except Exception as conection_error:
        print(f"Se produjo un error al intentar conectarse a base de datos: \n{conection_error}")
        now = datetime.now()
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
        now = datetime.now()
        escribir_registro(f"[{now}] ✅ Se extrajo correctamente la informacion a base de datos")
        print("Se extrajo la informacion correctamente de base de datos")
        return resultado
    except Exception as extract_error:
        now = datetime.now()
        print(f"Se produjo un error al extraer la informacion de base de datos {extract_error}\n {query}")
        escribir_registro(f"[{now}]❌ Ocurrio un error al extraer los datos de la tabla {tabla}")



if __name__ == '__main__':
    procesador = ProcesamientoDeInformacion("March 2025.xlsx") # Cambiar
    procesador.extraccion_dataset("db_omnia", "payroll", )