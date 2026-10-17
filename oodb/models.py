from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from durus.persistent import Persistent
from durus.persistent_list import PersistentList


_CENT = Decimal("0.01")


def _amount(value, field_name):
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as error:
        raise ValueError(f"{field_name} debe ser un valor numerico") from error
    if not amount.is_finite() or amount < 0:
        raise ValueError(f"{field_name} debe ser un valor no negativo")
    return amount.quantize(_CENT, rounding=ROUND_HALF_UP)


def _positive_integer(value, field_name):
    if isinstance(value, bool):
        raise ValueError(f"{field_name} debe ser un entero positivo")
    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as error:
        raise ValueError(f"{field_name} debe ser un entero positivo") from error
    if not number.is_finite() or number != number.to_integral_value() or number <= 0:
        raise ValueError(f"{field_name} debe ser un entero positivo")
    return int(number)


def _percentage(value, field_name):
    percentage = _amount(value, field_name)
    if percentage > Decimal("100.00"):
        raise ValueError(f"{field_name} no puede exceder 100")
    return percentage


class Articulo(Persistent):
    def __init__(self, nombre, precio, descripcion=""):
        self._id = None
        self._nombre = self._validate_text(nombre, "nombre", 100)
        self._descripcion = self._validate_text(descripcion, "descripcion", 1000, allow_empty=True)
        self._precio = _amount(precio, "precio")

    @staticmethod
    def _validate_text(value, field_name, max_length, allow_empty=False):
        if not isinstance(value, str):
            raise ValueError(f"{field_name} debe ser texto")
        text = value.strip()
        if (not text and not allow_empty) or len(text) > max_length:
            raise ValueError(f"{field_name} debe contener entre 1 y {max_length} caracteres")
        return text

    @property
    def id(self):
        return self._id

    @property
    def nombre(self):
        return self._nombre

    @property
    def descripcion(self):
        return self._descripcion

    @property
    def precio(self):
        return self._precio

    @property
    def tipo(self):
        raise NotImplementedError

    def establecer_nombre(self, nombre):
        self._nombre = self._validate_text(nombre, "nombre", 100)

    def establecer_descripcion(self, descripcion):
        self._descripcion = self._validate_text(descripcion, "descripcion", 1000, allow_empty=True)

    def establecer_precio(self, precio):
        self._precio = _amount(precio, "precio")

    def unidad_comercial(self):
        raise NotImplementedError

    def _asignar_id(self, articulo_id):
        if self._id is not None:
            raise ValueError("El articulo ya tiene un identificador")
        self._id = _positive_integer(articulo_id, "id")


class Producto(Articulo):
    @property
    def tipo(self):
        return "Producto"

    def unidad_comercial(self):
        return "pieza"


class Servicio(Articulo):
    @property
    def tipo(self):
        return "Servicio"

    def unidad_comercial(self):
        return "servicio"


class DetalleVenta(Persistent):
    def __init__(self, articulo, cantidad, precio_unitario=None, tasa_impuesto=0):
        if not isinstance(articulo, Articulo):
            raise ValueError("El detalle debe referenciar un articulo persistente")
        self._id = None
        self._articulo = articulo
        self._cantidad = _positive_integer(cantidad, "cantidad")
        self._precio_unitario = _amount(
            articulo.precio if precio_unitario is None else precio_unitario,
            "precio_unitario",
        )
        self._tasa_impuesto = _percentage(tasa_impuesto, "tasa_impuesto")

    @property
    def id(self):
        return self._id

    @property
    def articulo(self):
        return self._articulo

    @property
    def cantidad(self):
        return self._cantidad

    @property
    def precio_unitario(self):
        return self._precio_unitario

    @property
    def tasa_impuesto(self):
        return self._tasa_impuesto

    @property
    def subtotal(self):
        return (self._precio_unitario * self._cantidad).quantize(_CENT, rounding=ROUND_HALF_UP)

    @property
    def impuesto(self):
        return (self.subtotal * self._tasa_impuesto / Decimal("100")).quantize(
            _CENT, rounding=ROUND_HALF_UP
        )

    def establecer_cantidad(self, cantidad):
        self._cantidad = _positive_integer(cantidad, "cantidad")

    def establecer_precio_unitario(self, precio_unitario):
        self._precio_unitario = _amount(precio_unitario, "precio_unitario")

    def _establecer_tasa_impuesto(self, tasa_impuesto):
        self._tasa_impuesto = _percentage(tasa_impuesto, "tasa_impuesto")

    def resumen(self):
        return {
            "articulo": self._articulo.nombre,
            "tipo": self._articulo.tipo,
            "unidad": self._articulo.unidad_comercial(),
            "cantidad": self._cantidad,
            "precio_unitario": self._precio_unitario,
            "subtotal": self.subtotal,
            "impuesto": self.impuesto,
        }

    def _asignar_id(self, detalle_id):
        if self._id is not None:
            raise ValueError("El detalle ya tiene un identificador")
        self._id = _positive_integer(detalle_id, "id")


class Venta(Persistent):
    def __init__(self, cliente_id, tipo_cliente="person", fecha_venta=None, porcentaje_impuesto=0):
        self._id = None
        self._cliente_id = _positive_integer(cliente_id, "cliente_id")
        self._tipo_cliente = self._validate_client_type(tipo_cliente)
        self._fecha_venta = self._validate_date(fecha_venta)
        self._porcentaje_impuesto = _percentage(porcentaje_impuesto, "porcentaje_impuesto")
        self._detalles = PersistentList()

    @staticmethod
    def _validate_client_type(tipo_cliente):
        if tipo_cliente not in ("person", "company"):
            raise ValueError("tipo_cliente debe ser 'person' o 'company'")
        return tipo_cliente

    @staticmethod
    def _validate_date(fecha_venta):
        if fecha_venta is None:
            return date.today()
        if isinstance(fecha_venta, date):
            return fecha_venta
        if isinstance(fecha_venta, str):
            try:
                return date.fromisoformat(fecha_venta)
            except ValueError as error:
                raise ValueError("fecha_venta debe tener formato YYYY-MM-DD") from error
        raise ValueError("fecha_venta debe ser una fecha o texto YYYY-MM-DD")

    @property
    def id(self):
        return self._id

    @property
    def cliente_id(self):
        return self._cliente_id

    @property
    def tipo_cliente(self):
        return self._tipo_cliente

    @property
    def fecha_venta(self):
        return self._fecha_venta

    @property
    def porcentaje_impuesto(self):
        return self._porcentaje_impuesto

    @property
    def detalles(self):
        return tuple(self._detalles)

    @property
    def subtotal(self):
        return sum((detalle.subtotal for detalle in self._detalles), Decimal("0.00"))

    @property
    def impuesto(self):
        return sum((detalle.impuesto for detalle in self._detalles), Decimal("0.00"))

    @property
    def total(self):
        return self.subtotal + self.impuesto

    def establecer_cliente(self, cliente_id, tipo_cliente):
        self._cliente_id = _positive_integer(cliente_id, "cliente_id")
        self._tipo_cliente = self._validate_client_type(tipo_cliente)

    def establecer_fecha(self, fecha_venta):
        self._fecha_venta = self._validate_date(fecha_venta)

    def establecer_porcentaje_impuesto(self, porcentaje_impuesto):
        percentage = _percentage(porcentaje_impuesto, "porcentaje_impuesto")
        for detalle in self._detalles:
            detalle._establecer_tasa_impuesto(percentage)
        self._porcentaje_impuesto = percentage

    def agregar_detalle(self, detalle):
        if not isinstance(detalle, DetalleVenta):
            raise ValueError("Se requiere un DetalleVenta")
        if detalle.tasa_impuesto != self._porcentaje_impuesto:
            raise ValueError("La tasa del detalle debe coincidir con la tasa de la venta")
        self._detalles.append(detalle)

    def quitar_detalle(self, detalle_id):
        for index, detalle in enumerate(self._detalles):
            if detalle.id == detalle_id:
                del self._detalles[index]
                return detalle
        raise KeyError(f"No existe el detalle {detalle_id}")

    def _asignar_id(self, venta_id):
        if self._id is not None:
            raise ValueError("La venta ya tiene un identificador")
        self._id = _positive_integer(venta_id, "id")