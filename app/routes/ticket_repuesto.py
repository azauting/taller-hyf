from flask import (
    Blueprint,
    request,
    redirect,
    url_for,
    flash,
    render_template,
)
from app import db
from app.models import TicketRepuesto, Cliente
from datetime import datetime

ticket_repuesto_bp = Blueprint("ticket_repuesto", __name__, template_folder="templates")


@ticket_repuesto_bp.route("/panel/ticket_repuesto/nuevo", methods=["GET"])
def ticket_repuesto_form():
    clientes = Cliente.query.all()
    return render_template(
        "ticket_repuesto/ticket_repuesto_form.html", clientes=clientes
    )


@ticket_repuesto_bp.route("/panel/ticket_repuesto/crear", methods=["POST"])
def ticket_repuesto_crear():
    try:
        cliente_id = request.form.get("cliente_id")
        tipo_repuesto = request.form.get("tipo_repuesto")  # ej: 'Disco'
        tamano = request.form.get("tamano")  # 'grande' o 'chico'
        cantidad = int(request.form.get("cantidad", 1))
        precio = int(request.form.get("precio", 0))
        observacion = request.form.get("observacion", "").strip()

        if not (cliente_id and tipo_repuesto and tamano and cantidad and precio):
            flash("Todos los campos son obligatorios.", "danger")
            return redirect(request.referrer)

        total = cantidad * precio

        ticket_reparacion = TicketRepuesto(
            cliente_id=cliente_id,
            tipo_repuesto=tipo_repuesto,
            tamano=tamano,
            cantidad=cantidad,
            precio=precio,
            total=total,
            observacion=observacion,
            estado_taller="En taller",
            estado_pago="Pendiente",
            fecha_creacion=datetime.now(),
        )

        db.session.add(ticket_reparacion)
        db.session.commit()

        flash("Ticket de repuesto creado exitosamente.", "success")
        return redirect(url_for("taller.tickets_en_taller"))

    except Exception as e:
        print(f"Error al crear el ticket de repuesto: {e}")
        flash("Ocurrió un error al crear el ticket de repuesto.", "danger")
        return redirect(request.referrer)


@ticket_repuesto_bp.route("/panel/ticket_repuesto/<int:ticket_id>", methods=["GET"])
def ticket_repuesto_ver(ticket_id):
    ticket = TicketRepuesto.query.get_or_404(ticket_id)
    return render_template(
        "ticket_repuesto/ticket_repuesto_detalle.html", ticket=ticket
    )


@ticket_repuesto_bp.route(
    "/panel/ticket_repuesto/<int:ticket_id>/editar", methods=["GET", "POST"]
)
def ticket_repuesto_editar(ticket_id):
    ticket = TicketRepuesto.query.get_or_404(ticket_id)

    if request.method == "POST":
        try:
            # Validar y procesar datos del formulario
            tipo_repuesto = request.form.get("tipo_repuesto", "").strip()
            tamano = request.form.get("tamano", "").strip()
            cantidad = int(request.form.get("cantidad", 0))
            precio = int(request.form.get("precio", 0))
            observacion = request.form.get("observacion", "").strip()
            estado_taller = request.form.get("estado_taller")
            estado_pago = request.form.get("estado_pago")

            if not tipo_repuesto or cantidad <= 0 or precio < 0:
                raise ValueError("Datos inválidos")

            # Actualizar campos
            ticket.tipo_repuesto = tipo_repuesto
            ticket.tamano = tamano
            ticket.cantidad = cantidad
            ticket.precio = precio
            ticket.total = precio * cantidad
            ticket.observacion = observacion
            ticket.estado_taller = estado_taller
            ticket.estado_pago = estado_pago

            # Actualizar fecha de pago si corresponde
            if estado_pago.lower() == "pagado" and not ticket.fecha_de_pago:
                ticket.fecha_de_pago = datetime.now()

            db.session.commit()
            flash("Ticket de repuesto actualizado correctamente", "success")
            return redirect(url_for("taller.tickets_en_taller"))

        except ValueError as ve:
            db.session.rollback()
            flash(f"Datos inválidos: {str(ve)}", "danger")
        except Exception as e:
            db.session.rollback()
            print(f"Error al actualizar ticket de repuesto: {str(e)}")
            flash("Error al actualizar el ticket de repuesto", "danger")

    # Para GET o si hay error en POST
    return render_template("ticket_repuesto/ticket_repuesto_editar.html", ticket=ticket)
