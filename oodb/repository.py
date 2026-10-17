from durus.persistent import Persistent
from durus.persistent_dict import PersistentDict

from .models import Articulo, DetalleVenta, Producto, Servicio, Venta


class SwiftyRoot(Persistent):
    def __init__(self):
        self._articulos = PersistentDict()
        self._ventas = PersistentDict()
        self._siguiente_articulo_id = 1
        self._siguiente_venta_id = 1
        self._siguiente_detalle_id = 1

    def alta_articulo(self, tipo, nombre, precio, descripcion=""):
        clases = {"Producto": Producto, "Servicio": Servicio}
        if tipo not in clases:
            raise ValueError("tipo debe ser 'Producto' o 'Servicio'")
        articulo = clases[tipo](nombre, precio, descripcion)
        articulo._asignar_id(self._siguiente_articulo_id)
        self._articulos[articulo.id] = articulo
        self._siguiente_articulo_id += 1
        return articulo

    def consultar_articulo(self, articulo_id):
        try:
            return self._articulos[int(articulo_id)]
        except (KeyError, TypeError, ValueError) as error:
            raise KeyError(f"No existe el articulo {articulo_id}") from error

    def listar_articulos(self):
        return tuple(sorted(self._articulos.values(), key=lambda articulo: articulo.id))

    def modificar_articulo(self, articulo_id, **cambios):
        articulo = self.consultar_articulo(articulo_id)
        permitidos = {"nombre", "precio", "descripcion"}
        if not cambios or cambios.keys() - permitidos:
            raise ValueError("Solo se permiten cambios de nombre, precio o descripcion")

        clase = Producto if articulo.tipo == "Producto" else Servicio
        candidato = clase(
            cambios.get("nombre", articulo.nombre),
            cambios.get("precio", articulo.precio),
            cambios.get("descripcion", articulo.descripcion),
        )
        articulo.establecer_nombre(candidato.nombre)
        articulo.establecer_precio(candidato.precio)
        articulo.establecer_descripcion(candidato.descripcion)
        return articulo

    def baja_articulo(self, articulo_id):
        articulo = self.consultar_articulo(articulo_id)
        if any(
            detalle.articulo is articulo
            for venta in self._ventas.values()
            for detalle in venta.detalles
        ):
            raise ValueError("No se puede borrar un articulo usado en ventas")
        del self._articulos[articulo.id]
        return articulo

    def alta_venta(self, cliente_id, tipo_cliente="person", fecha_venta=None, porcentaje_impuesto=0):
        venta = Venta(cliente_id, tipo_cliente, fecha_venta, porcentaje_impuesto)
        venta._asignar_id(self._siguiente_venta_id)
        self._ventas[venta.id] = venta
        self._siguiente_venta_id += 1
        return venta

    def consultar_venta(self, venta_id):
        try:
            return self._ventas[int(venta_id)]
        except (KeyError, TypeError, ValueError) as error:
            raise KeyError(f"No existe la venta {venta_id}") from error

    def listar_ventas(self):
        return tuple(sorted(self._ventas.values(), key=lambda venta: venta.id))

    def modificar_venta(self, venta_id, *, cliente_id=None, tipo_cliente=None, fecha_venta=None,
                        porcentaje_impuesto=None):
        venta = self.consultar_venta(venta_id)
        if cliente_id is not None or tipo_cliente is not None:
            venta.establecer_cliente(
                venta.cliente_id if cliente_id is None else cliente_id,
                venta.tipo_cliente if tipo_cliente is None else tipo_cliente,
            )
        if fecha_venta is not None:
            venta.establecer_fecha(fecha_venta)
        if porcentaje_impuesto is not None:
            venta.establecer_porcentaje_impuesto(porcentaje_impuesto)
        return venta

    def alta_detalle(self, venta_id, articulo_id, cantidad, precio_unitario=None):
        venta = self.consultar_venta(venta_id)
        articulo = self.consultar_articulo(articulo_id)
        detalle = DetalleVenta(
            articulo,
            cantidad,
            precio_unitario,
            venta.porcentaje_impuesto,
        )
        detalle._asignar_id(self._siguiente_detalle_id)
        venta.agregar_detalle(detalle)
        self._siguiente_detalle_id += 1
        return detalle

    def consultar_detalle(self, venta_id, detalle_id):
        venta = self.consultar_venta(venta_id)
        for detalle in venta.detalles:
            if detalle.id == int(detalle_id):
                return detalle
        raise KeyError(f"No existe el detalle {detalle_id} en la venta {venta_id}")

    def modificar_detalle(self, venta_id, detalle_id, *, cantidad=None, precio_unitario=None):
        detalle = self.consultar_detalle(venta_id, detalle_id)
        candidato = DetalleVenta(
            detalle.articulo,
            detalle.cantidad if cantidad is None else cantidad,
            detalle.precio_unitario if precio_unitario is None else precio_unitario,
            detalle.tasa_impuesto,
        )
        detalle.establecer_cantidad(candidato.cantidad)
        detalle.establecer_precio_unitario(candidato.precio_unitario)
        return detalle

    def baja_detalle(self, venta_id, detalle_id):
        return self.consultar_venta(venta_id).quitar_detalle(int(detalle_id))

    def baja_venta(self, venta_id):
        venta = self.consultar_venta(venta_id)
        while venta.detalles:
            venta.quitar_detalle(venta.detalles[-1].id)
        del self._ventas[venta.id]
        return venta

    def ventas_de_cliente(self, cliente_id, tipo_cliente="person"):
        # SQL equivalente: SELECT * FROM sales WHERE client_id = ? AND client_type = ?;
        cliente_id = int(cliente_id)
        return tuple(
            venta
            for venta in self._ventas.values()
            if venta.cliente_id == cliente_id and venta.tipo_cliente == tipo_cliente
        )

    def ventas_con_articulo(self, articulo_id):
        # SQL equivalente: SELECT DISTINCT s.* FROM sales s JOIN sale_details d ON d.sale_id = s.id WHERE d.product_id = ?;
        articulo = self.consultar_articulo(articulo_id)
        return tuple(
            venta
            for venta in self._ventas.values()
            if any(detalle.articulo is articulo for detalle in venta.detalles)
        )

    def resumen_venta(self, venta_id):
        # SQL equivalente: SELECT d.*, p.name, p.type FROM sale_details d JOIN products p ON p.id = d.product_id WHERE d.sale_id = ?;
        venta = self.consultar_venta(venta_id)
        return tuple(detalle.resumen() for detalle in venta.detalles)


def obtener_raiz(connection):
    database_root = connection.get_root()
    root = database_root.get("swifty")
    if root is None:
        root = SwiftyRoot()
        database_root["swifty"] = root
    elif not isinstance(root, SwiftyRoot):
        raise TypeError("La clave 'swifty' de la raiz contiene un objeto incompatible")
    return root