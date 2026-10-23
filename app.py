"""Prototipo académico El Matute: ventas e inventario con controles básicos."""
from __future__ import annotations

import hmac
import os
import secrets
import sqlite3
from contextlib import contextmanager
from functools import wraps
from pathlib import Path

from flask import Flask, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash


BASE_DIR = Path(__file__).resolve().parent
app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32),
    DATABASE=os.environ.get("ELMATUTE_DATABASE", str(BASE_DIR / "elmatute.db")),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE", "0") == "1",
    MAX_CONTENT_LENGTH=16 * 1024,
)


@contextmanager
def conectar_db():
    db = sqlite3.connect(app.config["DATABASE"], timeout=5)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def inicializar_db():
    Path(app.config["DATABASE"]).parent.mkdir(parents=True, exist_ok=True)
    with conectar_db() as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL CHECK(length(nombre) BETWEEN 1 AND 100),
                talla TEXT NOT NULL CHECK(length(talla) BETWEEN 1 AND 20),
                precio INTEGER NOT NULL CHECK(precio > 0),
                stock INTEGER NOT NULL CHECK(stock >= 0)
            );
            CREATE TABLE IF NOT EXISTS ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                producto_id INTEGER NOT NULL,
                cantidad INTEGER NOT NULL CHECK(cantidad > 0),
                precio_unitario INTEGER NOT NULL CHECK(precio_unitario > 0),
                total INTEGER NOT NULL CHECK(total > 0),
                fecha TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(producto_id) REFERENCES productos(id)
            );
        """)


def csrf_valido():
    recibido = request.form.get("_csrf_token", "")
    guardado = session.get("_csrf_token", "")
    return bool(recibido and guardado and hmac.compare_digest(recibido, guardado))


@app.before_request
def controles_de_sesion():
    if "_csrf_token" not in session:
        session["_csrf_token"] = secrets.token_urlsafe(32)

    endpoint = request.endpoint or ""
    if endpoint not in {"login", "static"} and not session.get("usuario"):
        return redirect(url_for("login"))

    if request.method == "POST" and not csrf_valido():
        return "Solicitud rechazada: token CSRF ausente o inválido.", 400
    return None


@app.after_request
def cabeceras_seguridad(response):
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("Content-Security-Policy", "default-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'")
    response.headers.setdefault("Cache-Control", "no-store")
    return response


def requiere_sesion(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("usuario"):
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario_configurado = os.environ.get("ADMIN_USER", "admin")
        hash_configurado = os.environ.get("ADMIN_PASSWORD_HASH", "")
        usuario = request.form.get("usuario", "")
        clave = request.form.get("clave", "")
        if (hash_configurado and hmac.compare_digest(usuario, usuario_configurado)
                and check_password_hash(hash_configurado, clave)):
            session.clear()
            session["usuario"] = usuario
            session["_csrf_token"] = secrets.token_urlsafe(32)
            return redirect(url_for("inicio"))
        flash("Credenciales incorrectas o administrador sin configurar.")
    return render_template("login.html", csrf_token=session["_csrf_token"])


@app.post("/logout")
@requiere_sesion
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/")
@requiere_sesion
def inicio():
    with conectar_db() as db:
        productos = db.execute("SELECT * FROM productos ORDER BY nombre").fetchall()
        ventas = db.execute("""
            SELECT ventas.*, productos.nombre, productos.talla
            FROM ventas JOIN productos ON productos.id = ventas.producto_id
            ORDER BY ventas.id DESC LIMIT 10
        """).fetchall()
    return render_template("index.html", productos=productos, ventas=ventas,
                           csrf_token=session["_csrf_token"])


@app.post("/productos")
@requiere_sesion
def agregar_producto():
    nombre = request.form.get("nombre", "").strip()
    talla = request.form.get("talla", "").strip()
    try:
        precio = int(request.form.get("precio", ""))
        stock = int(request.form.get("stock", ""))
    except (ValueError, TypeError):
        flash("El precio y el stock deben ser números enteros.")
        return redirect(url_for("inicio"))

    if not nombre or len(nombre) > 100 or not talla or len(talla) > 20:
        flash("Nombre y talla son obligatorios y deben respetar el largo máximo.")
    elif precio <= 0 or stock < 0:
        flash("El precio debe ser mayor que cero y el stock no puede ser negativo.")
    else:
        with conectar_db() as db:
            db.execute("INSERT INTO productos(nombre,talla,precio,stock) VALUES(?,?,?,?)",
                       (nombre, talla, precio, stock))
        flash("Producto registrado correctamente.")
    return redirect(url_for("inicio"))


@app.post("/ventas")
@requiere_sesion
def registrar_venta():
    try:
        producto_id = int(request.form.get("producto_id", ""))
        cantidad = int(request.form.get("cantidad", ""))
    except (ValueError, TypeError):
        flash("Selecciona un producto e ingresa una cantidad válida.")
        return redirect(url_for("inicio"))
    if producto_id <= 0 or cantidad <= 0:
        flash("El producto y la cantidad deben ser válidos.")
        return redirect(url_for("inicio"))

    try:
        with conectar_db() as db:
            db.execute("BEGIN IMMEDIATE")
            resultado = db.execute(
                "UPDATE productos SET stock=stock-? WHERE id=? AND stock>=?",
                (cantidad, producto_id, cantidad),
            )
            if resultado.rowcount != 1:
                flash("Venta rechazada: producto inexistente o stock insuficiente.")
                return redirect(url_for("inicio"))
            producto = db.execute("SELECT precio FROM productos WHERE id=?", (producto_id,)).fetchone()
            total = producto["precio"] * cantidad
            db.execute("INSERT INTO ventas(producto_id,cantidad,precio_unitario,total) VALUES(?,?,?,?)",
                       (producto_id, cantidad, producto["precio"], total))
        flash(f"Venta registrada. Total: ${total:,}".replace(",", "."))
    except sqlite3.Error:
        app.logger.exception("Fallo de base de datos al registrar venta")
        flash("No se pudo registrar la venta. No se confirmó la operación.")
    return redirect(url_for("inicio"))


if __name__ == "__main__":
    inicializar_db()
    app.run(debug=False, host="127.0.0.1", port=int(os.environ.get("PORT", "5000")))
