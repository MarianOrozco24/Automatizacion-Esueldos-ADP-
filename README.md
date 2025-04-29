pyinstaller --noconsole --onefile ^
 --icon=icono/icon.ico ^
 --hidden-import=mysql ^
 --hidden-import=mysql.connector ^
 --hidden-import=mysql.connector.plugins.mysql_native_password ^
 --add-data "rutas.json;." ^
 --add-data "C:/Users/Usuario/Desktop/Codigos Planificacion Estrategica/Automatizacion-Adm-Personal/esueldos/.venv/Lib/site-packages/mysql/connector/locales;mysql/connector/locales" ^
 A-Esueldos.py