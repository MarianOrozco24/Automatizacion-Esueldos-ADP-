class Config:
    # Deinimos las columnas que nos vamos a dejar del excel resultado del script anterior
    columnas_a_filtrar = ["Legajo", "Basico", "Vacaciones", "Feriado", "D. Mudanza", "D. Estudio", "D. Suspension", "D. Tramite","Hs Extras", "Dep. Judicial", "Prepaga", "Enlazados", "Ant. de Sueldos", "Adic. Ventas"]

    # Configuraciones del procesamiento de reportes
    
    codigo_empresa = 1521 # Codigo de la empresa
    tipo_pago = "M" # Mensual

    def query_payroll (month, year):
        query= f"""
        SELECT 
        legajo, 
        fecha, 
        codigo, 
        descripcion,
        horas_programadas, 
        horas_trabajadas
        FROM payroll  WHERE MONTH(fecha) = {month} AND YEAR(fecha) = {year}"""
        
        return query

    columnas_payroll = ["legajo", "fecha", "codigo", "descripcion", 
                        "horas_programadas", "horas_trabajadas"] # Columnas payroll
    codificado = {
    "LM": 409,  # LICENCIA POR MATERNIDAD
    "LFF": 56,  # FALLECIMIENTO
    "MTM": 55,  # MATRIMONIO
    "CE": 62,  # ESTUDIO
    "ART" : 65, # ENFERMEDAD
    "LMED": 65,  # ENFERMEDAD
    "LESP" : 65, # Enfermedad
    "CM" : 65, # Enfermedad
    "LPS" : 65, # Enfermedad - Licencia psiquiatrica
    "Prepaga" : 654,
    "Basico" : 1,
    "Vacaciones" : 17,
    "Feriado" : 8,
    "D. Mudanza" : 54,
    "D. Estudio" : 62,
    "D. Suspension" : 50,
    "D. Tramite" : 51,
    "Enlazados" : 675 
    }


