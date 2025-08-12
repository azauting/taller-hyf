from flask import (
    Blueprint,
    jsonify,
    request,
    redirect,
    url_for,
    flash,
    render_template,
    make_response,
)
from app import db
from app.models import TicketServicio, TicketServicioDetalle, Cliente, Vehiculo
from datetime import datetime
from sqlalchemy.orm import joinedload
from datetime import datetime

ticket_servicio_bp = Blueprint("ticket_servicio", __name__, template_folder="templates")


# Grupo de rutas relacionadas con formularios de tickets
@ticket_servicio_bp.route("/panel/ticket_servicio/nuevo", methods=["GET"])
def ticket_servicio_form():
    clientes = Cliente.query.all()
    return render_template(
        "ticket_servicio/ticket_servicio_form.html", clientes=clientes
    )

# Endpoint para API/AJAX
@ticket_servicio_bp.route("/panel/ticket_servicio/vehiculos-cliente/<int:cliente_id>", methods=["GET"])
def obtener_vehiculos_cliente(cliente_id):
    vehiculos = Vehiculo.query.filter_by(cliente_id=cliente_id).all()
    return jsonify(
        [
            {"id": v.id, "marca": v.marca, "modelo": v.modelo, "patente": v.patente}
            for v in vehiculos
        ]
    )


# crear ticket servicio
@ticket_servicio_bp.route("/panel/ticket_servicio/crear", methods=["POST"])
def ticket_servicio_crear():
    try:
        # Obtener datos del cliente
        cliente_id = request.form.get("cliente_id")
        nombre = request.form.get("nombre_cliente")
        apellido = request.form.get("apellido_cliente")
        telefono = request.form.get("telefono_cliente")

        if not cliente_id:
            # Crear nuevo cliente
            if not (nombre and apellido and telefono):
                flash("Debe completar los datos del cliente.", "danger")
                return redirect(request.referrer)
            cliente = Cliente(
                nombre=nombre.strip(),
                apellido=apellido.strip(),
                telefono=telefono.strip(),
            )
            db.session.add(cliente)
            db.session.flush()
        else:
            cliente = Cliente.query.get(cliente_id)
            if not cliente:
                flash("Cliente no encontrado.", "danger")
                return redirect(request.referrer)

        # Vehículo existente o nuevo
        vehiculo_id = request.form.get("vehiculo_id")

        if vehiculo_id:
            vehiculo = Vehiculo.query.get(vehiculo_id)
            if not vehiculo:
                flash("Vehículo no encontrado.", "danger")
                return redirect(request.referrer)
        else:
            marca = request.form.get("marca")
            modelo = request.form.get("modelo")
            patente = request.form.get("patente")

            if not (marca and modelo and patente):
                flash("Debe completar todos los datos del vehículo.", "danger")
                return redirect(request.referrer)

            vehiculo = Vehiculo.query.filter_by(
                patente=patente.strip(), cliente_id=cliente.id
            ).first()

            if not vehiculo:
                vehiculo = Vehiculo(
                    marca=marca.strip(),
                    modelo=modelo.strip(),
                    patente=patente.strip(),
                    cliente_id=cliente.id,
                )
                db.session.add(vehiculo)
                db.session.flush()

        # Crear ticket
        motivo = request.form.get("motivo")
        observacion = request.form.get("observacion", "")

        if not motivo:
            flash("Debe especificar el motivo del ingreso.", "danger")
            return redirect(request.referrer)

        # Primero creamos el ticket sin total para obtener el ID
        ticket = TicketServicio(
            vehiculo_id=vehiculo.id,
            motivo=motivo.strip(),
            observacion=observacion.strip(),
            estado_taller="En taller",
            estado_pago="Pendiente",
            fecha_creacion=datetime.now(),
            total=0,  # Inicializamos con 0
        )
        db.session.add(ticket)
        db.session.flush()

        # Variables para calcular el total
        total_ticket = 0

        # Crear detalles de servicios y calcular subtotales
        tipos = request.form.getlist("tipo[]")
        descripciones = request.form.getlist("descripcion[]")
        cantidades = request.form.getlist("cantidad[]")
        precios = request.form.getlist("precio_unitario[]")

        for tipo, desc, cant, precio in zip(tipos, descripciones, cantidades, precios):
            if not desc.strip():
                continue
            try:
                cantidad = int(cant)
                precio_unitario = int(precio)
                subtotal = cantidad * precio_unitario
                total_ticket += subtotal
            except ValueError:
                flash("Cantidad o precio inválido en un servicio.", "warning")
                continue

            detalle = TicketServicioDetalle(
                tipo=tipo,
                descripcion=desc.strip(),
                cantidad=cantidad,
                precio_unitario=precio_unitario,
                ticket_id=ticket.id,
            )
            db.session.add(detalle)

        # Actualizar el total del ticket
        ticket.total = total_ticket

        db.session.commit()
        flash("Ticket creado exitosamente.", "success")
        return redirect(url_for("taller.tickets_en_taller"))

    except Exception as e:
        db.session.rollback()
        import traceback

        print(f"Error al crear el ticket: {e}")
        print(traceback.format_exc())
        flash("Ocurrió un error inesperado al crear el ticket.", "danger")
        return redirect(
            request.referrer or url_for("ticket_servicio.ticket_servicio_form")
        )


# Ver ticket de servicio (solo lectura)
@ticket_servicio_bp.route("/panel/ticket_servicio/<int:ticket_id>", methods=["GET"])
def ticket_servicio_ver(ticket_id):
    ticket = TicketServicio.query.get_or_404(ticket_id)
    total_ticket = sum(detalle.subtotal for detalle in ticket.servicios)

    return render_template(
        "ticket_servicio/ticket_servicio_detalle.html",  # Nueva plantilla para solo visualización
        ticket=ticket,
        total_ticket=total_ticket,
    )


# Editar ticket de servicio
@ticket_servicio_bp.route("/panel/ticket_servicio/<int:ticket_id>/editar", methods=["GET", "POST"])
def ticket_servicio_editar(ticket_id):
    ticket = TicketServicio.query.get_or_404(ticket_id)

    if request.method == "POST":
        try:
            # Actualizar campos del ticket principal
            ticket.estado_taller = request.form.get(
                "estado_taller", ticket.estado_taller
            )
            ticket.estado_pago = request.form.get("estado_pago", ticket.estado_pago)
            ticket.motivo = request.form.get("motivo", ticket.motivo)
            ticket.observacion = request.form.get("observacion", ticket.observacion)

            if ticket.estado_pago.lower() == "pagado" and not ticket.fecha_de_pago:
                ticket.fecha_de_pago = datetime.now()

            # === Servicios existentes ===
            ids_en_form = {
                key.split("_")[1]
                for key in request.form.keys()
                if key.startswith("descripcion_")
            }

            for detalle in ticket.servicios:
                detalle_id = str(detalle.id)
                if detalle_id not in ids_en_form:
                    continue

                detalle.descripcion = request.form.get(
                    f"descripcion_{detalle_id}", ""
                ).strip()
                if cant := request.form.get(f"cantidad_{detalle_id}"):
                    detalle.cantidad = int(cant)
                if precio := request.form.get(f"precio_unitario_{detalle_id}"):
                    detalle.precio_unitario = int(precio)
                detalle.tipo = request.form.get(f"tipo_{detalle_id}", detalle.tipo)

            # === Eliminar servicios removidos ===
            servicios_a_eliminar = [
                d for d in ticket.servicios if str(d.id) not in ids_en_form
            ]
            for eliminar in servicios_a_eliminar:
                db.session.delete(eliminar)

            # === Agregar nuevos servicios ===
            nuevas_descr = request.form.getlist("descripcion_nuevo[]")
            nuevas_cant = request.form.getlist("cantidad_nuevo[]")
            nuevos_prec = request.form.getlist("precio_nuevo[]")
            nuevos_tipos = request.form.getlist("tipo_nuevo[]")

            for desc, cant, prec, tipo in zip(
                nuevas_descr, nuevas_cant, nuevos_prec, nuevos_tipos
            ):
                if desc and cant and prec:
                    nuevo = TicketServicioDetalle(
                        descripcion=desc.strip(),
                        cantidad=int(cant),
                        precio_unitario=int(prec),
                        tipo=tipo or "servicio",
                        ticket_id=ticket.id,
                    )
                    db.session.add(nuevo)

            # Actualizar total
            ticket.total = sum(detalle.subtotal for detalle in ticket.servicios)

            db.session.commit()
            flash("Ticket actualizado correctamente", "success")
            return redirect(url_for("taller.tickets_en_taller"))

        except Exception as e:
            db.session.rollback()
            print(f"Error al actualizar ticket: {str(e)}")
            flash("Error al actualizar el ticket", "danger")

    # Para GET o si hay error en POST
    total_ticket = sum(detalle.subtotal for detalle in ticket.servicios)
    return render_template(
        "ticket_servicio/ticket_servicio_editar.html",  # Plantilla de edición
        ticket=ticket,
        total_ticket=total_ticket,
    )
