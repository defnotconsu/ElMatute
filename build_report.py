from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                PageBreak, KeepTogether, Flowable, HRFlowable, Image as RLImage)
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

OUT = Path(__file__).resolve().parent / "informe_eva3_ropa_interior.pdf"
INK = colors.HexColor("#29242A")
PLUM = colors.HexColor("#713E55")
ROSE = colors.HexColor("#F5EDF1")
MUTED = colors.HexColor("#625B60")
GREEN = colors.HexColor("#27664F")
AMBER = colors.HexColor("#8A5B15")

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="CoverTitle", parent=styles["Title"], fontName="Helvetica-Bold",
    fontSize=28, leading=33, textColor=PLUM, alignment=TA_LEFT, spaceAfter=9))
styles.add(ParagraphStyle(name="Sub", parent=styles["Normal"], fontSize=13, leading=18,
    textColor=MUTED, spaceAfter=7))
styles.add(ParagraphStyle(name="H1x", parent=styles["Heading1"], fontName="Helvetica-Bold",
    fontSize=19, leading=23, textColor=PLUM, spaceBefore=4, spaceAfter=11, keepWithNext=True))
styles.add(ParagraphStyle(name="H2x", parent=styles["Heading2"], fontName="Helvetica-Bold",
    fontSize=12.5, leading=16, textColor=PLUM, spaceBefore=9, spaceAfter=5, keepWithNext=True))
styles.add(ParagraphStyle(name="Bodyx", parent=styles["BodyText"], fontName="Helvetica",
    fontSize=9.2, leading=13.5, textColor=INK, spaceAfter=6))
styles.add(ParagraphStyle(name="Smallx", parent=styles["BodyText"], fontName="Helvetica",
    fontSize=7.5, leading=10, textColor=MUTED, spaceAfter=3))
styles.add(ParagraphStyle(name="Cellx", parent=styles["BodyText"], fontName="Helvetica",
    fontSize=7.8, leading=10.2, textColor=INK))
styles.add(ParagraphStyle(name="CellHeadx", parent=styles["BodyText"], fontName="Helvetica-Bold",
    fontSize=7.8, leading=10, textColor=colors.white))
styles.add(ParagraphStyle(name="Quote", parent=styles["BodyText"], fontName="Helvetica-Oblique",
    fontSize=10, leading=14, textColor=PLUM, leftIndent=10, rightIndent=8, spaceAfter=7))

def P(text, style="Bodyx"):
    return Paragraph(text, styles[style])

def tbl(rows, widths, header=True, font=7.8):
    wrapped=[]
    for ri,row in enumerate(rows):
        wrapped.append([P(str(x), "CellHeadx" if header and ri==0 else "Cellx") for x in row])
    t=Table(wrapped, colWidths=widths, repeatRows=1 if header else 0, hAlign="LEFT")
    cmds=[("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(0,0),(-1,-1),6),
          ("RIGHTPADDING",(0,0),(-1,-1),6),("TOPPADDING",(0,0),(-1,-1),5),
          ("BOTTOMPADDING",(0,0),(-1,-1),5),("GRID",(0,0),(-1,-1),0.35,colors.HexColor("#D9CCD2"))]
    if header:
        cmds += [("BACKGROUND",(0,0),(-1,0),PLUM),("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,ROSE])]
    else:
        cmds += [("BACKGROUND",(0,0),(-1,-1),ROSE)]
    t.setStyle(TableStyle(cmds))
    return t

def evidence_image(filename, width):
    img=RLImage(str(Path(__file__).resolve().parent / "evidencias" / filename), width=width)
    img.drawHeight=width * img.imageHeight / img.imageWidth
    return img

class Diagram(Flowable):
    def __init__(self, kind, width=468, height=205):
        super().__init__(); self.kind=kind; self.width=width; self.height=height
    def box(self,x,y,w,h,title,lines=(),fill=ROSE,stroke=PLUM):
        c=self.canv; c.setFillColor(fill); c.setStrokeColor(stroke); c.setLineWidth(0.8)
        c.roundRect(x,y,w,h,5,fill=1,stroke=1); c.setFillColor(PLUM)
        c.setFont("Helvetica-Bold",8); c.drawCentredString(x+w/2,y+h-13,title)
        c.setFillColor(INK); c.setFont("Helvetica",7)
        for i,line in enumerate(lines): c.drawCentredString(x+w/2,y+h-25-i*10,line)
    def arrow(self,x1,y1,x2,y2,label=""):
        c=self.canv; c.setStrokeColor(MUTED); c.setFillColor(MUTED); c.setLineWidth(.8)
        c.line(x1,y1,x2,y2)
        if abs(y2-y1)<1:
            d=1 if x2>x1 else -1
            c.line(x2,y2,x2-5*d,y2+3); c.line(x2,y2,x2-5*d,y2-3)
        else:
            d=1 if y2>y1 else -1
            c.line(x2,y2,x2-3,y2-5*d); c.line(x2,y2,x2+3,y2-5*d)
        if label:
            c.setFont("Helvetica",6.7); c.setFillColor(INK); c.drawCentredString((x1+x2)/2,(y1+y2)/2+4,label)
    def draw(self):
        c=self.canv; w=self.width; h=self.height
        if self.kind=="architecture":
            c.setDash(3,2); c.setStrokeColor(colors.HexColor("#B99CAA")); c.roundRect(149,24,301,156,8,fill=0,stroke=1); c.setDash()
            c.setFont("Helvetica-Bold",8); c.setFillColor(PLUM); c.drawCentredString(299,167,"Google Cloud - despliegue recomendado")
            self.box(5,76,126,58,"Personal de tienda",["Navegador y HTTPS","Inicio de sesión"],fill=colors.white)
            self.box(172,76,117,58,"Cloud Run (PaaS)",["Aplicación Flask","Secretos y logs"],fill=colors.white)
            self.box(330,76,112,58,"Cloud SQL",["PostgreSQL","Backups cifrados"],fill=colors.white)
            self.arrow(131,105,172,105,"HTTPS")
            self.arrow(289,105,330,105,"TLS privado")
            self.box(172,27,117,30,"SaaS",["Workspace y repositorio"],fill=ROSE)
            self.arrow(230,57,230,76,"gestión")
            c.setFont("Helvetica-Oblique",7); c.setFillColor(MUTED); c.drawString(5,10,"IaaS (Compute Engine) es alternativa si se necesita controlar el sistema operativo; exige más administración.")
        elif self.kind=="usecase":
            c.setStrokeColor(PLUM); c.roundRect(92,14,363,174,6,fill=0,stroke=1)
            c.setFont("Helvetica-Bold",8); c.setFillColor(PLUM); c.drawCentredString(273,176,"El Matute")
            c.setFillColor(INK); c.setStrokeColor(INK)
            c.circle(34,125,7,fill=0,stroke=1); c.line(34,118,34,94); c.line(34,110,23,102); c.line(34,110,45,102); c.line(34,94,25,81); c.line(34,94,43,81)
            c.setFont("Helvetica",7); c.drawCentredString(34,70,"Vendedor/a")
            cases=[("Iniciar sesión",145), ("Registrar producto",116), ("Consultar inventario",87), ("Registrar venta",58), ("Consultar ventas",29)]
            for title,y in cases:
                c.ellipse(136,y,270,y+22,fill=0,stroke=1); c.setFillColor(INK); c.drawCentredString(203,y+8,title)
                c.setStrokeColor(MUTED)
                if title == "Consultar ventas":
                    c.line(46,103,70,72); c.line(70,72,86,40); c.line(86,40,136,40)
                else:
                    c.line(46,103,136,y+11)
            c.ellipse(315,58,440,84,fill=0,stroke=1); c.setFillColor(INK); c.drawCentredString(377,67,"Validar stock")
            c.setStrokeColor(MUTED); c.setDash(3,2); c.line(270,69,315,69); c.setDash()
            c.setFillColor(INK); c.setFont("Helvetica",6.5); c.drawCentredString(293,74,"<<include>>")
        elif self.kind=="classes":
            self.box(8,54,126,111,"Producto",["id: int","nombre: str","talla: str","precio: CLP","stock: int"],fill=colors.white)
            self.box(170,54,126,111,"Venta",["id: int","cantidad: int","precio_unitario: CLP","total: CLP","fecha: datetime"],fill=colors.white)
            self.box(334,54,126,111,"Usuario / sesión",["usuario configurado","hash fuera de DB","sesión firmada","token CSRF"],fill=colors.white)
            self.arrow(134,110,170,110,"1 - 0..*")
            c.setFont("Helvetica",7); c.setFillColor(MUTED); c.drawCentredString(396,35,"no se persiste en SQLite")
            self.box(170,8,126,30,"Servicio de ventas",["validar y descontar stock"],fill=ROSE)
            self.arrow(233,54,233,38,"")
        elif self.kind=="sequence":
            xs=[44,151,268,390]; labels=["Vendedor/a","Interfaz Flask","Servicio venta","SQLite"]
            for x,label in zip(xs,labels):
                self.box(x-42,164,84,28,label,(),fill=colors.white)
                c.setStrokeColor(colors.HexColor("#B9AFB4")); c.setDash(2,2); c.line(x,8,x,164); c.setDash()
            steps=[(44,151,143,"POST venta + CSRF"),(151,151,119,"sesión y CSRF OK"),
                   (151,268,95,"producto, cantidad"),(268,390,71,"BEGIN; UPDATE stock"),
                   (390,268,47,"stock suficiente"),(268,390,26,"INSERT venta / COMMIT")]
            for x1,x2,y,label in steps: self.arrow(x1,y,x2,y,label)
            c.setFont("Helvetica-Oblique",6.7); c.setFillColor(AMBER); c.drawRightString(454,9,"Si falla stock: rollback y rechazo")

def footer(c, doc):
    c.saveState(); width,height=letter
    c.setStrokeColor(colors.HexColor("#E6DCE1")); c.line(20*mm,16*mm,width-20*mm,16*mm)
    c.setFont("Helvetica",7); c.setFillColor(MUTED)
    c.drawString(20*mm,10*mm,"Ingeniería de Software | EVA3 | El Matute")
    c.drawRightString(width-20*mm,10*mm,f"{doc.page}")
    c.restoreState()

story=[]
story += [Spacer(1,27*mm), P("Ingeniería de Software · Evaluación 3","Sub"),
          P("Sistema de ventas e inventario<br/>para El Matute","CoverTitle"),
          P("Propuesta tecnológica, análisis ético y legal, UML, prototipo seguro y pruebas","Sub"),
          Spacer(1,11*mm), HRFlowable(width="100%", thickness=1, color=PLUM), Spacer(1,8*mm),
          P("Caso de estudio: El Matute, emprendimiento de ropa interior. El prototipo aborda el control de existencias por producto y talla, el registro de ventas y la actualización del stock.","Bodyx"),
          Spacer(1,13*mm), tbl([["Equipo","Dos integrantes (roles identificados en sección 4)"],["Fecha","20 de octubre de 2026"],["Evaluación","EVA3 - 40% de la asignatura"]],[45*mm,115*mm],header=False),
          Spacer(1,12*mm), P("Informe académico basado en el alcance funcional demostrado y en los antecedentes del caso El Matute.","Smallx"), PageBreak()]

story += [P("Resumen ejecutivo","H1x"),
 P("El Matute necesita reemplazar planillas y registros manuales por un sistema pequeño y confiable que mantenga al día el stock por prenda y talla, registre ventas y permita recuperar el estado del inventario después de errores. El prototipo usa Flask y SQLite para demostrar el flujo crítico en un solo local. Para crecer, se propone desplegar la aplicación en una plataforma administrada y migrar la base a PostgreSQL administrado."),
 P("La venta descuenta existencias dentro de una transacción: si el producto no existe o no hay stock suficiente, la operación se rechaza sin crear una venta parcial. La solución evita recopilar datos personales de clientes en esta etapa; los registros de venta contienen producto, talla, cantidad, precio y fecha. El historial ofrece trazabilidad básica, pero no es un registro inmutable ni una auditoría protegida contra cambios directos en la base de datos. La versión de entrega incorpora inicio de sesión, token CSRF, consultas parametrizadas, límites de entrada y cabeceras de seguridad."),
 P("1. Contexto y alcance","H1x"),
 P("El caso se basa en el emprendimiento de ropa interior El Matute y en la aplicación Flask disponible para la evaluación. Por el tipo de catálogo, una misma prenda puede variar por modelo y talla; confirmar esa disponibilidad al vender y conservar un registro claro de cada movimiento son necesidades centrales del caso. El prototipo demuestra esas funciones en una operación de una sucursal."),
 P("Problema y objetivos","H2x"),
 tbl([["Necesidad operacional","Respuesta del prototipo","Criterio de aceptación"],
["Confirmar disponibilidad por modelo y talla para evitar sobreventa.","Catálogo con producto, talla, precio y stock; selector muestra disponibilidad.","El inventario refleja el nuevo stock tras una venta válida."],
["Evitar errores al calcular cobros y reconstruir movimientos.","Calcular el total y guardar cantidad, precio unitario, total y fecha.","El total coincide con precio × cantidad y la venta aparece en el historial."],
["Restringir cambios y reducir solicitudes no autorizadas.","Exigir sesión, token CSRF y validación de entradas.","Peticiones sin sesión o CSRF se rechazan."]],[48*mm,58*mm,54*mm]),
 P("Alcance funcional","H2x"),
 P("Incluye acceso de administrador, alta de producto, consulta de inventario, registro de venta, validación de stock y vista de las últimas diez ventas. No incluye pago electrónico, facturación tributaria, devoluciones, clientes, varias sucursales ni sincronización con un POS externo. Es un prototipo académico; no debe tratarse como sistema productivo certificado."), PageBreak()]

story += [P("2. Propuesta tecnológica e infraestructura cloud","H1x"),
 P("El diseño mantiene una aplicación web simple para el equipo de tienda. El navegador se comunica por HTTPS con Flask. La aplicación administra las reglas de venta; una base relacional conserva productos y movimientos. Para el prototipo, SQLite reduce complejidad y facilita probar el descuento de stock en una sucursal. En una operación desplegada con varios usuarios, PostgreSQL administrado mejora la concurrencia, el respaldo y la operación."),
 P("Arquitectura propuesta","H2x"), Diagram("architecture",height=200),
 tbl([["Modelo","Uso propuesto en El Matute","Ventaja y límite"],
 ["Cloud Computing","Uso de recursos de cómputo, red y almacenamiento bajo demanda; la arquitectura separa aplicación, base y respaldos.","Reduce inversión inicial y permite ajustar capacidad; requiere conectividad, gestión de accesos y control de costos."],
 ["SaaS","Google Workspace para correo y documentos; repositorio GitHub/GitLab como servicio de colaboración.","No hay que instalar ni mantener esos productos; revisar ubicación de datos, permisos y condiciones del proveedor."],
 ["PaaS","Cloud Run para publicar el servicio Flask sin administrar servidores; Cloud SQL para PostgreSQL administrado.","El proveedor mantiene plataforma y parches del servicio; la PYME sigue responsable de código, permisos y datos."],
 ["IaaS","Compute Engine como alternativa si se necesita controlar el sistema operativo o instalar componentes propios.","Mayor flexibilidad, pero la tienda tendría que mantener sistema operativo, firewall, parches y recuperación."]],[25*mm,74*mm,61*mm]),
 P("Justificación y operación","H2x"),
 P("Para un emprendimiento pequeño de ropa interior, la prioridad es controlar las existencias por modelo y talla, evitar diferencias de stock y recuperar respaldos sin personal dedicado a servidores. Por eso, la ruta recomendada es PaaS y base administrada; IaaS queda como alternativa condicionada por una necesidad técnica concreta. Cloud SQL ofrece administración del motor relacional y opciones de cifrado y respaldo, sujetas a configuración del servicio. Antes de contratar se compararán costo mensual total, región disponible, exportación y restauración de datos, soporte, SLA, límites de uso y dependencia del proveedor."),
 P("Operación y continuidad: definir con la dueña el tiempo máximo tolerable sin servicio y pérdida de datos; programar respaldos diarios y probar restauración trimestral. Si falla Internet, anotar ventas con folio y conciliarlas al restablecer conexión. Proteger con HTTPS, secretos fuera del código, red privada, MFA y alertas de presupuesto."), PageBreak()]

story += [P("3. Confiabilidad, ética y marco legal","H1x"),
 P("La confiabilidad protege la continuidad de caja y la confianza de quienes administran el inventario. Una caída durante una venta puede duplicar un cobro, dejar el stock desactualizado o retrasar la atención. Una pérdida de datos puede impedir reponer prendas o explicar diferencias. El diseño usa una actualización condicional de stock y registra la venta dentro de una transacción, evitando confirmar operaciones incompletas."),
 P("Principios éticos aplicados","H2x"),
 P("El equipo limita el acceso a personas autorizadas, minimiza los datos recogidos, explica a la PYME qué se almacena, protege la información y prueba solo el sistema propio o con autorización. El código de ética de ACM orienta a priorizar el bien público, respetar privacidad y diseñar seguridad usable. Los resultados de pruebas deben comunicarse con honestidad; una suite aprobada no equivale a una auditoría de seguridad completa."),
 P("Marco chileno relevante a la fecha del informe","H2x"),
 tbl([["Norma","Aplicación al caso"],
 ["Ley 19.628 sobre protección de la vida privada (vigente hasta 30-11-2026).","Si se incorporan datos personales de clientes o trabajadores, definir finalidad y base aplicable, restringir accesos, proteger registros y responder solicitudes conforme al texto vigente."],
 ["Ley 21.719, publicada en 2024; modificaciones con vigencia desde 01-12-2026.","Reforma el régimen de datos personales y crea una autoridad de protección de datos. Diseñar desde ahora con minimización, finalidad, seguridad y atención de derechos para facilitar la transición."],
 ["Ley 21.459 sobre delitos informáticos (texto vigente consultado al 01-04-2025).","El acceso no autorizado, ataques a integridad, interceptación y otras conductas descritas en la ley son un riesgo jurídico. Las pruebas deben limitarse al prototipo y a entornos autorizados."]],[53*mm,107*mm]),
 P("En el prototipo no se solicitan ni almacenan nombres, RUT, teléfonos, correos ni medios de pago de clientes. La PYME debe validar el tratamiento de datos y sus obligaciones con asesoría competente antes de operar con datos reales. Este apartado identifica normas aplicables al caso, pero no sustituye una evaluación jurídica."), PageBreak()]

story += [P("4. Modelado UML y trabajo en equipo","H1x"),
 P("Los diagramas describen al vendedor como actor principal y el flujo crítico como una venta que valida sesión y CSRF, intenta descontar stock y guarda el movimiento solo cuando existe disponibilidad."),
 P("Diagrama de casos de uso","H2x"), Diagram("usecase",height=203),
 P("El caso de uso «Registrar venta» incluye «Validar stock». El actor consulta catálogo y ventas, registra productos y termina la sesión. La autorización ocurre antes de ejecutar acciones de cambio."),
 P("Diagrama de clases","H2x"), Diagram("classes",height=192),
 P("Una venta referencia un producto; el servicio de ventas coordina la operación transaccional. El usuario se configura fuera de SQLite y su sesión autoriza el acceso; por eso no aparece como una tabla persistente."), PageBreak(),
 P("4. Modelado UML y trabajo en equipo (continuación)","H1x"),
 P("Secuencia de venta","H2x"), Diagram("sequence",height=207),
 P("La operación comienza con la sesión y el token CSRF válidos. SQLite inicia una transacción, actualiza el stock solo cuando alcanza para toda la cantidad y guarda el precio aplicado. Si no se cumple la condición, se rechaza la operación y no se registra una venta parcial."),
 P("Roles y método de colaboración","H2x"),
 tbl([["Rol de trabajo","Responsabilidades incluidas en el plan"],
 ["Integrante 1 - Lead Developer / Backend y seguridad","Lógica de ventas y stock, esquema relacional, autenticación, controles OWASP y revisión técnica."],
 ["Integrante 2 - Scrum Master / Frontend, QA y cumplimiento","Coordinación del backlog, interfaz, ejecución de pruebas y documentación ética, legal e ISO."],
 ["Trabajo conjunto","Validación de criterios, revisión de cambios y consolidación de la entrega."]],[55*mm,105*mm]),
 P("La extensión organiza el trabajo en cuatro ciclos: preparación y arquitectura; prototipado y seguridad; testing y refactorización; auditoría y cierre. Este informe describe ese cronograma como plan de trabajo y atribuye como implementado solo lo demostrado por el prototipo y las pruebas adjuntas."), PageBreak()]

story += [P("5. Prototipo, seguridad OWASP y alcance legal","H1x"),
 P("El prototipo funcional se implementa con Flask y SQLite. Permite registrar prendas de ropa interior por nombre o modelo, talla, precio y stock; consultar el stock disponible al iniciar una venta; calcular el total; y revisar las diez ventas más recientes. El navegador recibe mensajes claros y las plantillas escapan el contenido dinámico."),
 P("Controles de seguridad incorporados","H2x"),
 tbl([["Riesgo / referencia OWASP Top 10:2025","Control presente","Prueba o evidencia"],
 ["A01 Control de acceso roto; A07 Fallas de autenticación","Inicio de sesión con hash de contraseña; rutas protegidas; cookie HttpOnly y SameSite.","Acceso sin sesión redirige a login; prueba de acceso."],
 ["A02 Configuración insegura; A04 Fallas criptográficas","debug=False; secreto de sesión y hash fuera del código; cabeceras CSP, nosniff y frame-ancestors.","Revisión de configuración y prueba de cabeceras."],
 ["A05 Inyección","Consultas parametrizadas y escape HTML automático de Jinja.","Entrada con sintaxis similar a SQL permanece como texto y no elimina la tabla."],
 ["CSRF / diseño inseguro","Token CSRF obligatorio en todas las operaciones POST.","POST sin token recibe HTTP 400."],
 ["Condición de carrera / integridad de datos","Descuento condicionado a stock suficiente dentro de transacción inmediata.","Prueba de venta válida y prueba de venta mayor al stock disponible."]],[45*mm,72*mm,43*mm]),
 P("El OWASP Top 10:2025 sirve para priorizar riesgos, mientras que OWASP ASVS ofrece requisitos verificables para controles técnicos. El prototipo aplica controles seleccionados; no afirma cubrir todos los riesgos del Top 10 ni obtener conformidad ASVS."),
 P("Corrección Antes / Después","H2x"),
 tbl([["Antes - aplicación inicial","Después - versión EVA3"],
 ["Clave fija para sesión en código y modo de depuración activo.","Secreto de sesión desde variable de entorno con valor aleatorio de respaldo para ejecución local; `debug=False`. En producción se debe configurar secreto persistente y rotarlo."],
 ["Formulario POST sin autenticación ni token CSRF.","Formulario exige sesión y token sincronizado; el servidor compara el token en tiempo constante y rechaza su ausencia."],
 ["El registro de venta descontaba stock de forma condicional; no había evidencia automatizada para flujo de venta.","Se conserva el descuento condicional y se prueba con escenarios de venta válida y stock insuficiente; se ejecuta como transacción." ]],[80*mm,80*mm]),
 P("Se conservó el uso de consultas parametrizadas que ya existía. La mejora se concentra en sesiones, CSRF, configuración segura y evidencia repetible de integridad de inventario."), PageBreak()]

login_img=evidence_image("login_ropa_interior.jpg",72*mm)
stock_img=evidence_image("inventario_ropa_interior.jpg",72*mm)
sale_img=evidence_image("venta_ropa_interior.jpg",112*mm)
story += [P("Evidencia visual del prototipo","H1x"),
 P("Las capturas se tomaron desde el navegador en la versión local del prototipo el 20-10-2026. El producto y la venta son datos ficticios de demostración; no corresponden a registros reales de El Matute."),
 Table([[login_img,stock_img],[P("Inicio de sesión.","Smallx"),P("Inventario tras registrar venta: stock 3.","Smallx")]], colWidths=[79*mm,79*mm], hAlign="CENTER", style=TableStyle([("ALIGN",(0,0),(-1,-1),"CENTER"),("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(0,0),(-1,-1),2),("RIGHTPADDING",(0,0),(-1,-1),2),("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3)])),
 Spacer(1,5*mm), P("Registro de venta","H2x"),
 Table([[sale_img],[P("Venta demo número 1: dos calzones de algodón a $9.990 cada uno, total $19.980; stock actualizado de 5 a 3.","Smallx")]], colWidths=[160*mm], hAlign="CENTER", style=TableStyle([("ALIGN",(0,0),(-1,-1),"CENTER"),("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(0,0),(-1,-1),2),("RIGHTPADDING",(0,0),(-1,-1),2),("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3)])),
 PageBreak()]

story += [P("6. Testing, ISO 27000 y refactorización","H1x"),
 P("El plan combina pruebas de integración y seguridad sobre una base temporal. Los resultados que siguen se obtuvieron ejecutando `python -m unittest discover -s tests -v` desde la carpeta eva3_entrega el 20-10-2026. La suite no prueba carga, disponibilidad, recuperación de respaldos, gestión de secretos en cloud, escaneo de dependencias ni penetración externa."),
 P("Matriz y resultado de pruebas","H2x"),
 tbl([["ID / tipo","Procedimiento y resultado esperado","Resultado ejecutado"],
 ["T01 - acceso","Abrir inventario sin sesión; se espera redirección a login.","APROBADA"],
 ["T02 - integración","Crear un calzón de algodón talla M a $9.990, stock 5; vender 2; stock 3 y total = 19.980 CLP.","APROBADA"],
 ["T03 - integridad","Intentar vender 6 unidades con stock 5; no cambia stock ni crea venta.","APROBADA"],
 ["T04 - CSRF","Enviar alta de producto sin token; se espera HTTP 400.","APROBADA"],
 ["T05 - inyección","Usar texto con sintaxis similar a SQL en el nombre; se guarda como texto y tabla sigue disponible.","APROBADA"],
 ["T06 - configuración","Comprobar CSP, X-Frame-Options y X-Content-Type-Options en respuesta.","APROBADA"]],[28*mm,105*mm,27*mm]),
 P("Resultado: 6 de 6 pruebas automatizadas aprobadas. Los casos están en `tests/test_app.py`; la salida de esta ejecución se adjunta como `evidencias/pruebas_ropa_interior.txt`."),
 P("Análisis según ISO/IEC 27001 y 27002","H2x"),
 tbl([["Hallazgo / activo","Riesgo inicial","Control alineado","Acción / estado"],
 ["Acceso a ventas e inventario","Alto: terceros podrían alterar existencias.","Control de acceso, autenticación y gestión de privilegios; ISO/IEC 27002 5.15, 5.17, 5.18 y 8.5.","Sesión requerida y hash de clave implementados; pendiente separar roles y revisar privilegios."],
 ["Sesión web y formularios","Medio-alto: CSRF y configuración débil.","Desarrollo seguro y codificación segura; 8.25, 8.28 y 8.29.","Token CSRF, cookies seguras y cabeceras añadidos; activar cookie Secure en HTTPS."],
 ["Base de inventario","Alto: error de venta o pérdida de stock.","Respaldo 8.13, registro 8.15 y gestión de vulnerabilidades 8.8.","Transacción y log del servidor; diseñar backups cloud y prueba de restauración."],
 ["Dependencias y servicio cloud","Medio: vulnerabilidad o indisponibilidad de proveedor.","Gestión de servicios cloud 5.23 y gestión de vulnerabilidades 8.8.","Inventariar versiones, aplicar parches, revisar SLA y probar salida/migración."]],[33*mm,37*mm,54*mm,36*mm]),
 P("ISO/IEC 27001 define requisitos para un sistema de gestión de seguridad de la información; ISO/IEC 27002 ofrece controles de referencia. Esta matriz usa controles como guía de mejora y no declara certificación ni cumplimiento formal."),
 PageBreak()]

story += [P("Referencias","H1x"),
 P("Normas y estándares consultados","H2x"),
 P("[1] Biblioteca del Congreso Nacional de Chile. Ley 19.628, texto vigente al 30 de noviembre de 2026. <link href='https://www.bcn.cl/leychile/navegar?idNorma=141599&amp;idVersion=2023-05-09' color='#713E55'>Texto oficial</link>.","Smallx"),
 P("[2] Biblioteca del Congreso Nacional de Chile. Ley 21.719, modifica la Ley 19.628; vigencia de las modificaciones desde 1 de diciembre de 2026. <link href='https://www.bcn.cl/leychile/navegar?idNorma=1209272' color='#713E55'>Texto oficial</link>.","Smallx"),
 P("[3] Biblioteca del Congreso Nacional de Chile. Ley 21.459 sobre delitos informáticos, versión vigente consultada al 1 de abril de 2025. <link href='https://www.bcn.cl/leychile/navegar?idNorma=1177743&amp;idVersion=2025-04-01' color='#713E55'>Texto oficial</link>.","Smallx"),
 P("[4] ACM. Code of Ethics and Professional Conduct, secciones sobre bien público, privacidad, acceso autorizado y seguridad. <link href='https://www.acm.org/binaries/content/assets/about/acm-code-of-ethics-booklet.pdf' color='#713E55'>Código</link>.","Smallx"),
 P("[5] OWASP Foundation. OWASP Top 10:2025. <link href='https://top10.owasp.org/2025/' color='#713E55'>Proyecto oficial</link>; OWASP ASVS 5.0.0. <link href='https://owasp.org/projects/asvs' color='#713E55'>Proyecto oficial</link>.","Smallx"),
 P("[6] ISO. ISO/IEC 27001:2022, Information security management systems. <link href='https://www.iso.org/standard/27001' color='#713E55'>Página oficial</link>; ISO/IEC 27002:2022, controles de seguridad. <link href='https://www.iso.org/standard/75652.html' color='#713E55'>Página oficial</link>.","Smallx"),
 P("[7] Google Cloud. Cloud SQL, servicio de base de datos relacional administrado. <link href='https://cloud.google.com/sql' color='#713E55'>Documentación del proveedor</link>; Cloud Run. <link href='https://cloud.google.com/run/docs/overview/what-is-cloud-run' color='#713E55'>Documentación del proveedor</link>.","Smallx"),
 Spacer(1,7*mm), P("Evolución recomendada para El Matute","H2x"),
 tbl([["Prioridad futura","Motivo y alcance sugerido"],
["Validar catálogo y reglas de venta","Confirmar modelos, tallas, cambios y devoluciones con la dueña antes de ampliar el sistema."],
["Despliegue y continuidad","Configurar HTTPS, base administrada, respaldos y pruebas de restauración antes de usar datos reales."],
["Clientes y medios de pago (fuera del prototipo)","Incorporarlos solo si el negocio lo necesita; definir minimización de datos y usar una pasarela externa sin almacenar datos de tarjeta."],
["Auditoría de movimientos (fuera del prototipo)","Si se requiere historial resistente a modificaciones, diseñar permisos, bitácora y respaldos separados; el historial actual no es inmutable."]],[52*mm,108*mm]),
 Spacer(1,6*mm), P("Las capturas y resultados de pruebas incluidos corresponden al prototipo académico. Los módulos señalados como evolución no están implementados ni se presentan como capacidades actuales.","Smallx"),
 Spacer(1,4*mm), P("Fuentes revisadas el 20 de octubre de 2026.","Smallx")]

doc=SimpleDocTemplate(str(OUT), pagesize=letter, rightMargin=22*mm,leftMargin=22*mm,
    topMargin=19*mm,bottomMargin=22*mm,title="Sistema de ventas e inventario para El Matute - EVA3",
    author="Equipo El Matute")
doc.build(story,onFirstPage=footer,onLaterPages=footer)
print(OUT)
