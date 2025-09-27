# Notas de Integración y Pruebas Rápidas

---

## Estructura de Archivos

Asegúrese de que los siguientes archivos estén en el **mismo directorio**:

- `main.py`
- `gui_login.py`
- `gui_menu.py`
- `logica.py`
- `datos.py`
- `mayan_sunset.db`

---

## Requisitos de la Base de Datos

Se espera una tabla llamada **`Usuario`** con las siguientes columnas:

- `id`
- `usuario`
- `contraseña`
- `tipo_usuario`

Para que la validación funcione correctamente, los valores de `tipo_usuario` deben ser **`"administrador"`** o **`"empleado"`** en minúsculas.  
El código está diseñado para normalizar (convertir a minúsculas) cualquier entrada en mayúscula para una coincidencia estricta.

---

## Prueba Básica de Funcionalidad

1. Ejecute el programa principal desde la terminal:  
   ```bash
   python main.py
