from app import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class Usuario(UserMixin, db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(120), unique=True, nullable=False)
    contrasena_hash = db.Column(db.String(128), nullable=False)
    rol = db.Column(
        db.String(20), nullable=False, default="default"
    )  # 'admin' para permisos

    def set_password(self, password):
        self.contrasena_hash = generate_password_hash(password, method="pbkdf2:sha256")

    def check_password(self, password):
        return check_password_hash(self.contrasena_hash, password)

    def guardar(self):
        db.session.add(self)
        db.session.commit()


class Inventario(db.Model):
    __tablename__ = "inventario"

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(100), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    precio_compra = db.Column(db.Integer, nullable=False)
    porcentaje = db.Column(db.Float, nullable=False)
    precio_venta = db.Column(db.Integer, nullable=False)
    fecha_actualizacion = db.Column(
        db.DateTime, default=datetime.now, onupdate=datetime.now
    )



class Cliente(db.Model):
    __tablename__ = "cliente"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    vehiculos = db.relationship("Vehiculo", backref="cliente", lazy=True)


class Vehiculo(db.Model):
    __tablename__ = "vehiculo"

    id = db.Column(db.Integer, primary_key=True)
    marca = db.Column(db.String(50), nullable=False)
    modelo = db.Column(db.String(50), nullable=False)
    patente = db.Column(db.String(10), unique=True, nullable=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.now)
    cliente_id = db.Column(db.Integer, db.ForeignKey("cliente.id"), nullable=False)
    tickets = db.relationship("TicketServicio", backref="vehiculo", lazy=True)



class TicketServicio(db.Model):
    __tablename__ = "ticket_servicio"

    id = db.Column(db.Integer, primary_key=True)
    motivo = db.Column(db.String(500), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.now)
    fecha_de_pago = db.Column(db.DateTime)
    estado_taller = db.Column(db.String(20), default="En taller") 
    estado_pago = db.Column(db.String(20), default="Pendiente")
    observacion = db.Column(db.Text)
    total = db.Column(db.Integer, nullable=False)
    vehiculo_id = db.Column(db.Integer, db.ForeignKey("vehiculo.id"), nullable=False)
    servicios = db.relationship("TicketServicioDetalle", backref="ticket", lazy=True)

    @property
    def calcular_total(self):
        return sum(detalle.subtotal for detalle in self.servicios)



class TicketServicioDetalle(db.Model):
    __tablename__ = "ticket_servicio_detalle"

    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(20), nullable=False)  # 'repuesto' o 'servicio'
    descripcion = db.Column(
        db.String(255), nullable=False
    )  # nombre de producto o servicio
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Integer, nullable=False)

    ticket_id = db.Column(db.Integer, db.ForeignKey("ticket_servicio.id"), nullable=False)

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario

class TicketRepuesto(db.Model):
    __tablename__ = 'ticket_repuesto'

    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    tipo_repuesto = db.Column(db.String(50), nullable=False)  
    tamano = db.Column(db.String(20), nullable=False)  #chico, grande
    cantidad = db.Column(db.Integer, nullable=False, default=1)
    precio = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Integer, nullable=False)
    observacion = db.Column(db.Text)
    estado_taller = db.Column(db.String(20), default="En taller") 
    fecha_creacion = db.Column(db.DateTime, default=datetime.now)
    fecha_de_pago = db.Column(db.DateTime)
    estado_pago = db.Column(db.String(20), default="Pendiente")
    cliente = db.relationship('Cliente', backref='tickets_repuestos')

    def calcular_total(self):
        self.total = self.precio * self.cantidad