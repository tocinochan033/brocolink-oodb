import argparse
from pathlib import Path

from durus.connection import Connection
from durus.file_storage import FileStorage

from .repository import obtener_raiz


def ejecutar(database_path):
    database_path = Path(database_path)
    database_path.parent.mkdir(parents=True, exist_ok=True)
    storage = FileStorage(str(database_path))
    connection = Connection(storage)
    try:
        root = obtener_raiz(connection)
        producto = root.alta_articulo("Producto", "Teclado", "450.00", "Teclado USB")
        servicio = root.alta_articulo("Servicio", "Instalacion", "800.00")
        venta = root.alta_venta(7, "person", porcentaje_impuesto=16)
        root.alta_detalle(venta.id, producto.id, 2)
        root.alta_detalle(venta.id, servicio.id, 1)
        connection.commit()

        print(f"Venta confirmada #{venta.id}: subtotal={venta.subtotal}, total={venta.total}")
        for detalle in root.resumen_venta(venta.id):
            print(
                f"- {detalle['cantidad']} {detalle['unidad']} de {detalle['articulo']} "
                f"({detalle['tipo']}): {detalle['subtotal']}"
            )

        venta_abortada = root.alta_venta(8, "company", porcentaje_impuesto=0)
        connection.abort()
        root = obtener_raiz(connection)
        print(f"Venta #{venta_abortada.id} revertida; ventas persistidas: {len(root.listar_ventas())}")
    finally:
        storage.close()


def main():
    parser = argparse.ArgumentParser(description="Demostracion OODB de Swifty con Durus")
    parser.add_argument(
        "--database",
        default="swifty-demo.durus",
        help="ruta del archivo Durus (por defecto: swifty-demo.durus)",
    )
    arguments = parser.parse_args()
    ejecutar(arguments.database)


if __name__ == "__main__":
    main()