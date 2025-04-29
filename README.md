pyinstaller --noconsole --onefile ^
 --icon=icono/icon.ico ^
 --hidden-import=mysql ^
 --hidden-import=mysql.connector ^
 --hidden-import=mysql.connector.plugins.mysql_native_password ^
 --add-data "rutas.json;." ^
 --add-data C:/Users/enzo.orozco/Desktop/Automatizacion-Esueldos-ADP-/.venv/Lib/site-packages/mysql/connector/locales;mysql/connector/locales" ^
 A-Esueldos.py


 pyinstaller --noconsole --onefile ^
--icon=icono/icon.ico ^
--collect-all mysql ^
--add-data "rutas.json;." ^
A-Esueldos.py
