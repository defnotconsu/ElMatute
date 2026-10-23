# El Matute - EVA3

Prototipo académico para el emprendimiento de ropa interior El Matute: alta de prendas por modelo y talla, consulta de inventario y registro de ventas con descuento de stock transaccional.

## Requisitos y ejecución

Python 3.11 o superior recomendado. En PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:FLASK_SECRET_KEY = (py -c "import secrets; print(secrets.token_urlsafe(48))")
$env:ADMIN_USER = "admin"
$env:ADMIN_PASSWORD_HASH = (py -c "from werkzeug.security import generate_password_hash; print(generate_password_hash(input('Contraseña: ')))")
py app.py
```

Abrir `http://127.0.0.1:5000/login` e ingresar con el usuario y la clave usados al generar el hash. La base de datos de demostración se crea como `elmatute.db` en esta carpeta. No usar datos personales reales en esta demostración.

## Pruebas

```powershell
python -m unittest discover -s tests -v
```

Las pruebas cubren autenticación, CSRF, creación de producto, venta válida, rechazo por falta de stock, consultas parametrizadas ante una entrada similar a SQL y cabeceras de seguridad.

## Controles incorporados

- Contraseña almacenada como hash de Werkzeug; el hash y la clave de sesión se entregan mediante variables de entorno.
- Sesión con cookies HttpOnly y SameSite=Lax; activar `COOKIE_SECURE=1` detrás de HTTPS.
- Token CSRF en cada operación POST.
- Consultas SQL parametrizadas, validación de cantidades y transacción para descontar el stock.
- Escape HTML automático de Jinja y cabeceras CSP, X-Frame-Options y nosniff.
- `debug=False`, errores de base de datos genéricos para el usuario y detalle en log del servidor.

## Límites del prototipo

El usuario administrador es único; no hay roles granulares, recuperación de clave, registro de auditoría de cambios, integración de pagos ni datos de clientes. SQLite sirve para la demostración de un solo local, no para operación concurrente en varias sucursales. Para producción: gestión formal de secretos, HTTPS, base de datos administrada, copias de seguridad probadas, monitoreo, control de acceso por rol y revisión de seguridad independiente.

## Estructura

- `app.py`: aplicación Flask.
- `templates/`, `static/`: interfaz.
- `tests/`: pruebas automatizadas.
- `uml/`: fuentes PlantUML de los tres diagramas.
- `informe_eva3_ropa_interior.pdf`: informe para revisión y ajuste del equipo.
