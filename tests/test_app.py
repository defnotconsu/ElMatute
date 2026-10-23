import os
import re
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from werkzeug.security import generate_password_hash

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import app


class AppSecurityTests(unittest.TestCase):
    def setUp(self):
        self.db_path = str(Path(__file__).resolve().parent / "test.db")
        Path(self.db_path).unlink(missing_ok=True)
        self.env = patch.dict(os.environ, {
            "ADMIN_USER": "admin",
            "ADMIN_PASSWORD_HASH": generate_password_hash("Clave-de-prueba-2026!"),
        })
        self.env.start()
        app.app.config.update(TESTING=True, DATABASE=self.db_path, SECRET_KEY="test-secret")
        app.inicializar_db()
        self.client = app.app.test_client()

    def tearDown(self):
        self.env.stop()
        Path(self.db_path).unlink(missing_ok=True)

    def csrf(self, page="/login"):
        response = self.client.get(page)
        match = re.search(rb'name="_csrf_token" value="([^"]+)"', response.data)
        self.assertIsNotNone(match)
        return match.group(1).decode()

    def login(self):
        token = self.csrf()
        response = self.client.post("/login", data={
            "_csrf_token": token, "usuario": "admin", "clave": "Clave-de-prueba-2026!"
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        return response

    def add_product(self, nombre="Calzón de algodón"):
        return self.client.post("/productos", data={
            "_csrf_token": self.csrf("/"), "nombre": nombre, "talla": "M",
            "precio": "9990", "stock": "5"
        }, follow_redirects=True)

    def test_authentication_is_required(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.headers["Location"])

    def test_login_and_sale_update_inventory_atomically(self):
        self.login()
        self.add_product()
        token = self.csrf("/")
        response = self.client.post("/ventas", data={
            "_csrf_token": token, "producto_id": "1", "cantidad": "2"
        }, follow_redirects=True)
        self.assertIn("Venta registrada", response.get_data(as_text=True))
        with app.conectar_db() as db:
            self.assertEqual(db.execute("SELECT stock FROM productos WHERE id=1").fetchone()[0], 3)
            self.assertEqual(db.execute("SELECT total FROM ventas").fetchone()[0], 19980)

    def test_sale_rejects_insufficient_stock_without_partial_record(self):
        self.login()
        self.add_product()
        self.client.post("/ventas", data={
            "_csrf_token": self.csrf("/"), "producto_id": "1", "cantidad": "6"
        })
        with app.conectar_db() as db:
            self.assertEqual(db.execute("SELECT stock FROM productos WHERE id=1").fetchone()[0], 5)
            self.assertEqual(db.execute("SELECT COUNT(*) FROM ventas").fetchone()[0], 0)

    def test_csrf_token_is_required_for_state_changes(self):
        self.login()
        response = self.client.post("/productos", data={
            "nombre": "Calzón", "talla": "M", "precio": "1000", "stock": "2"
        })
        self.assertEqual(response.status_code, 400)

    def test_sql_like_input_is_stored_as_data(self):
        self.login()
        payload = "x'); DROP TABLE productos;--"
        self.add_product(payload)
        with app.conectar_db() as db:
            self.assertEqual(db.execute("SELECT nombre FROM productos").fetchone()[0], payload)
            self.assertIsNotNone(db.execute("SELECT name FROM sqlite_master WHERE name='productos'").fetchone())

    def test_security_headers_are_present(self):
        self.login()
        response = self.client.get("/")
        self.assertEqual(response.headers["X-Frame-Options"], "DENY")
        self.assertIn("default-src 'self'", response.headers["Content-Security-Policy"])
        self.assertEqual(response.headers["X-Content-Type-Options"], "nosniff")

    def test_zero_quantity_is_rejected(self):
        self.login()
        self.add_product()
        response = self.client.post("/ventas", data={
            "_csrf_token": self.csrf("/"),
            "producto_id": "1",
            "cantidad": "0"
        }, follow_redirects=True)
        self.assertIn(
            "El producto y la cantidad deben ser válidos.",
            response.get_data(as_text=True)
        )
        with app.conectar_db() as db:
            self.assertEqual(
                db.execute("SELECT stock FROM productos WHERE id=1").fetchone()[0],
                5
            )
            self.assertEqual(db.execute("SELECT COUNT(*) FROM ventas").fetchone()[0], 0)

