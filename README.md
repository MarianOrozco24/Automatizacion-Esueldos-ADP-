# 📊 Procesador de Novedades Mensuales

Este script en Python automatiza la lectura, transformación y exportación de datos desde un archivo Excel con novedades mensuales del personal. Ideal para preparar archivos listos para ser importados en sistemas como **E-sueldos** u otros de gestión de recursos humanos.

---

## ⚙️ ¿Qué hace el script?

- 🔄 Carga una configuración externa desde `config.json`.
- 📅 Construye dinámicamente el nombre del archivo a procesar usando mes y año.
- 📥 Lee y limpia el archivo Excel eliminando columnas innecesarias.
- 🧠 Detecta solo las celdas con valores (novedades reales).
- 🛠 Transforma cada novedad en un registro estructurado.
- 🔢 Ajusta tipos de datos y ordena los legajos.
- ✅ Verifica valores faltantes.
- 📤 Exporta los resultados a un nuevo archivo Excel listo para cargar.

---

## 📁 Estructura esperada del proyecto
tu_proyecto/ │ ├── config.json ├── Abril 2025.xlsx # (o el mes correspondiente) ├── tu_script.py └── Borrar.xlsx # (salida generada)


---

## 🧾 Formato del archivo de salida

Cada fila del archivo exportado contiene:

| Campo       | Descripción                           |
|-------------|----------------------------------------|
| Empresa     | Código de empresa fijo (ej: 1571)      |
| Legajo      | Número de legajo del empleado          |
| Periodo     | Año                                     |
| Mes         | Número de mes                          |
| Columna     | Tipo de novedad detectada              |
| MesAjuste   | Igual que Mes (puede ajustarse luego)  |
| Forzado     | 0 por defecto                          |
| Unidades    | Valor numérico de la novedad           |
| Importe     | 0 por defecto                          |

---

## 📦 Requisitos
Python 3.x

pandas

openpyxl


🛠 Configuración
El archivo config.json debe tener al menos la siguiente estructura:
{
  "ruta_inputs": "ruta/a/tu/carpeta/"
}

🧠 Notas adicionales
Este proyecto es ideal para automatizar tareas repetitivas del área de RRHH.

Se puede adaptar fácilmente para diferentes estructuras o sistemas de carga.


