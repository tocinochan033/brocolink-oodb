import tempfile
import unittest
from pathlib import Path

from durus.connection import Connection
from durus.file_storage import FileStorage
from durus.persistent import Persistent

from apicore.oodb.models import Articulo, DetalleVenta, Producto, Servicio, Venta
from apicore.oodb.repository import obtener_raiz


class SwiftyOodbTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.storage = FileStorage(str(Path(self.temp_dir.name) / "swifty.durus"))
        self.connection = Connection(self.storage)
        self.root = obtener_raiz(self.connection)

    def tearDown(self):
        self.connection.abort()
        self.storage.close()
        self.temp_dir.cleanup()

    def test_persistent_hierarchy_and_polymorphic_graph(self):
        product = self.root.alta_articulo("Producto", "Teclado", "450.00")
        service = self.root.alta_articulo("Servicio", "Instalacion", "800.00")
        sale = self.root.alta_venta(7, "person", "2026-10-16", 16)
        self.root.alta_detalle(sale.id, product.id, 2)
        self.root.alta_detalle(sale.id, service.id, 1)

        self.assertTrue(issubclass(Articulo, Persistent))
        self.assertTrue(issubclass(Venta, Persistent))
        self.assertTrue(issubclass(DetalleVenta, Persistent))
        self.assertTrue(issubclass(Producto, Articulo))
        self.assertTrue(issubclass(Servicio, Articulo))
        self.assertEqual(sale.total, 1972)
        self.assertEqual(
            [line["unidad"] for line in self.root.resumen_venta(sale.id)],
            ["pieza", "servicio"],
        )
        self.assertIs(sale.detalles[0].articulo, product)

    def test_commit_and_abort(self):
        product = self.root.alta_articulo("Producto", "Mouse", "250.00")
        committed_sale = self.root.alta_venta(3, "person", porcentaje_impuesto=0)
        self.root.alta_detalle(committed_sale.id, product.id, 1)
        self.connection.commit()

        aborted_sale = self.root.alta_venta(4, "company", porcentaje_impuesto=0)
        self.connection.abort()
        self.root = obtener_raiz(self.connection)

        self.assertEqual(len(self.root.listar_ventas()), 1)
        self.assertEqual(self.root.consultar_venta(committed_sale.id).total, 250)
        with self.assertRaises(KeyError):
            self.root.consultar_venta(aborted_sale.id)

    def test_crud_navigation_and_cascade(self):
        product = self.root.alta_articulo("Producto", "Monitor", "3000.00")
        service = self.root.alta_articulo("Servicio", "Soporte", "500.00")
        sale = self.root.alta_venta(9, "company", porcentaje_impuesto=0)
        detail = self.root.alta_detalle(sale.id, product.id, 1)
        self.root.alta_detalle(sale.id, service.id, 2)

        self.assertEqual(self.root.ventas_de_cliente(9, "company"), (sale,))
        self.assertEqual(self.root.ventas_con_articulo(product.id), (sale,))
        self.root.modificar_articulo(product.id, nombre="Monitor HD", precio="3200.00")
        self.root.modificar_venta(sale.id, fecha_venta="2026-10-15")
        self.root.modificar_detalle(sale.id, detail.id, cantidad=2)
        self.assertEqual(detail.subtotal, 6000)
        self.assertEqual(sale.fecha_venta.isoformat(), "2026-10-15")

        with self.assertRaises(ValueError):
            self.root.baja_articulo(product.id)
        removed_sale = self.root.baja_venta(sale.id)
        self.assertEqual(removed_sale.detalles, ())
        with self.assertRaises(KeyError):
            self.root.consultar_venta(sale.id)
        self.root.baja_articulo(product.id)
        self.assertEqual(self.root.listar_articulos(), (service,))

    def test_validation_rejects_invalid_business_values(self):
        with self.assertRaises(ValueError):
            self.root.alta_articulo("Producto", "", "10.00")
        with self.assertRaises(ValueError):
            self.root.alta_venta(1, "other")
        with self.assertRaises(ValueError):
            self.root.alta_venta(1, "person", porcentaje_impuesto=101)


if __name__ == "__main__":
    unittest.main()