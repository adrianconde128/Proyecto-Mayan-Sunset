Aquí tienes el texto en formato puro, incluyendo los caracteres de Markdown sin el formato aplicado:

```
# Notas de Integración y Pruebas Rápidas para LOGIN y MENU PRINCIPAL
---
## Estructura de Archivos 📂
Asegúrese de que los siguientes archivos estén en el **mismo directorio**:
* `main.py`
* `gui_login.py`
* `gui_menu.py`
* `logica.py`
* `datos.py`
* `mayan_sunset.db`
---
## Requisitos de la Base de Datos 🗃️
Se espera una tabla llamada **`Usuario`** con las siguientes columnas:
* `id`
* `usuario`
* `contraseña`
* `tipo_usuario`
Para que la validación funcione correctamente, los valores de `tipo_usuario` deben ser **`"administrador"`** o **`"empleado"`** en minúsculas. El código está diseñado para normalizar (convertir a minúsculas) cualquier entrada en mayúscula para una coincidencia estricta.
---
## Prueba Básica de Funcionalidad ✅
1.  Ejecute el programa principal desde la terminal: `python main.py`.
2.  En la pantalla de login, ingrese un **usuario** y una **contraseña** que ya existan en la tabla `Usuario`.
3.  Al validar correctamente, la ventana de login se cerrará y se abrirá la ventana del menú principal.
### Comportamiento del Menú 🚪
* El botón **"Gestión de Usuarios"** solo será visible si el `tipo_usuario` del usuario logueado es **`"administrador"`**.
* El botón de **"Reservaciones"** intentará importar el archivo `gui_hotel_mayan_sunset.py` y abrir su formulario. Hay comentarios `TODO` en el código para que pueda adaptar este punto de integración a su implementación específica.
```
