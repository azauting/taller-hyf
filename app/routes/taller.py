from flask import (
    Blueprint,
    request,
    redirect,
    url_for,
    flash,
    render_template,
    make_response,
)
from sqlalchemy import func
from app import db
from app.models import TicketServicio, Cliente, Vehiculo, TicketRepuesto
from sqlalchemy.orm import joinedload
from datetime import datetime

taller_bp = Blueprint("taller", __name__, template_folder="templates")


@taller_bp.route("/panel/taller")
def tickets_en_taller():
    # Tickets de vehículos
    tickets_vehiculo = (
        TicketServicio.query.filter(TicketServicio.estado_taller == "En taller")
        .options(joinedload(TicketServicio.vehiculo).joinedload(Vehiculo.cliente))
        .all()
    )

    # Tickets de repuestos
    tickets_repuesto = (
        TicketRepuesto.query.filter(TicketRepuesto.estado_taller == "En taller")
        .options(joinedload(TicketRepuesto.cliente))
        .all()
    )

    return render_template(
        "tickets/en_taller.html",
        tickets_vehiculo=tickets_vehiculo,
        tickets_repuesto=tickets_repuesto,
    )


@taller_bp.route("/panel/tickets-servicios", methods=["GET"])
def tabla_vehiculos():
    estado_taller_filtro = request.args.get("estado_taller", "")
    estado_pago_filtro = request.args.get("estado_pago", "")
    search_termino = request.args.get("buscar", "")
    fecha = request.args.get("fecha", "")
    page = request.args.get("page", 1, type=int)
    per_page = 10  # número de registros por página

    # Crear la consulta base para tickets
    query = db.session.query(TicketServicio).join(Vehiculo).join(Cliente)

    # Filtros de estado de taller
    if estado_taller_filtro:
        query = query.filter(TicketServicio.estado_taller == estado_taller_filtro)
    # Filtros de estado de pago
    if estado_pago_filtro:
        query = query.filter(TicketServicio.estado_pago == estado_pago_filtro)

    # Búsqueda por patente, marca del vehículo, o nombre del cliente
    if search_termino:
        search_filter = f"%{search_termino}%"
        query = query.filter(
            db.or_(
                Vehiculo.patente.ilike(search_filter),
                Vehiculo.marca.ilike(search_filter),
                Vehiculo.modelo.ilike(search_filter),
                Cliente.nombre.ilike(search_filter),
                Cliente.apellido.ilike(search_filter),
                func.concat(Cliente.nombre, ' ', Cliente.apellido).ilike(search_filter),
            )
        )

    # Filtro por fecha exacta (en formato DD-MM-YYYY)
    if fecha:
        try:
            # Convertir la fecha ingresada a formato datetime
            search_date = datetime.strptime(fecha, "%d-%m-%Y")

            # Comparar solo la fecha (sin la hora)
            query = query.filter(
                db.func.date(TicketServicio.fecha_creacion) == search_date.date()
            )

        except ValueError:
            # Si el formato de fecha no es válido, mostramos un mensaje de error
            flash('Formato de fecha incorrecto. Usa el formato "DD-MM-YYYY".', "error")
            return redirect(url_for("ticket.mostrar_tickets_vehiculos_todos"))

    # Ordenar por la fecha de creación, más recientes primero
    query = query.order_by(TicketServicio.fecha_creacion.desc())

    # Aplicar paginación
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    tickets = pagination.items
    total_pages = pagination.pages

    # Contar los tickets por estado taller
    counts_taller = {
        "En taller": db.session.query(TicketServicio).filter_by(estado_taller="En taller").count(),
        "Terminado": db.session.query(TicketServicio).filter_by(estado_taller="Terminado").count(),
        "Entregado": db.session.query(TicketServicio).filter_by(estado_taller="Entregado").count(),
        "Cancelado": db.session.query(TicketServicio).filter_by(estado_taller="Cancelado").count(),
    }

    # Contar los tickets por estado de pago
    counts_pago = {
        "Pendiente": db.session.query(TicketServicio).filter_by(estado_pago="Pendiente").count(),
        "Pagado": db.session.query(TicketServicio).filter_by(estado_pago="Pagado").count(),
    }


    return render_template(
        "ticket_servicio/tabla_vehiculos.html",
        tickets=tickets,
        estado_taller_filtro=estado_taller_filtro,
        estado_pago_filtro = estado_pago_filtro,
        search_termino=search_termino,
        fecha=fecha,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        total_items=pagination.total,
        counts_taller=counts_taller,
        counts_pago=counts_pago,
    )


@taller_bp.route("/panel/tickets-repuestos", methods=["GET"])
def tabla_repuestos():
    estado_taller_filtro = request.args.get("estado_taller", "")
    estado_pago_filtro = request.args.get("estado_pago", "")
    search_termino = request.args.get("buscar", "")
    fecha = request.args.get("fecha", "")
    page = request.args.get("page", 1, type=int)
    per_page = 10  # número de registros por página

    # Consulta base que une TicketRepuesto con Cliente
    query = db.session.query(TicketRepuesto, Cliente).join(Cliente)

    # Filtros de estado de taller
    if estado_taller_filtro:
        query = query.filter(TicketRepuesto.estado_taller == estado_taller_filtro)
    # Filtros de estado de pago
    if estado_pago_filtro:
        query = query.filter(TicketRepuesto.estado_pago == estado_pago_filtro)

    # Búsqueda por tipo de repuesto o nombre del cliente
    if search_termino:
        search_filter = f"%{search_termino}%"
        query = query.filter(
            db.or_(
                TicketRepuesto.tipo_repuesto.ilike(search_filter),
                Cliente.nombre.ilike(search_filter),
                Cliente.apellido.ilike(search_filter),
                Cliente.telefono.ilike(search_filter),
                func.concat(Cliente.nombre, ' ', Cliente.apellido).ilike(search_filter),
            )
        )

    # Filtro por fecha exacta (en formato DD-MM-YYYY)
    if fecha:
        try:
            # Convertir la fecha ingresada a formato datetime
            search_date = datetime.strptime(fecha, "%d-%m-%Y")
            # Comparar solo la fecha (sin la hora)
            query = query.filter(
                db.func.date(TicketRepuesto.fecha_creacion) == search_date.date()
            )
        except ValueError:
            # Si el formato de fecha no es válido
            flash('Formato de fecha incorrecto. Usa el formato "DD-MM-YYYY".', "error")
            return redirect(url_for("ticket.mostrar_tickets_repuestos_todos"))

    # Ordenar por la fecha de creación, más recientes primero
    query = query.order_by(TicketRepuesto.fecha_creacion.desc())

    # Aplicar paginación - Necesitamos adaptar para la consulta con join
    # Primero obtenemos el total de items
    total_items = query.count()

    # Aplicamos límite y offset manualmente
    tickets_repuesto = query.offset((page - 1) * per_page).limit(per_page).all()
    total_pages = (
        total_items + per_page - 1
    ) // per_page  # Cálculo del total de páginas

    # Contar los tickets por estado taller
    counts_taller = {
        "En taller": db.session.query(TicketRepuesto).filter_by(estado_taller="En taller").count(),
        "Terminado": db.session.query(TicketRepuesto).filter_by(estado_taller="Terminado").count(),
        "Entregado": db.session.query(TicketRepuesto).filter_by(estado_taller="Entregado").count(),
        "Anulado": db.session.query(TicketRepuesto).filter_by(estado_taller="Anulado").count(),
        "Cancelado": db.session.query(TicketRepuesto).filter_by(estado_taller="Cancelado").count(),
    }

    # Contar los tickets por estado de pago
    counts_pago = {
        "Pendiente": db.session.query(TicketRepuesto).filter_by(estado_pago="Pendiente").count(),
        "Pagado": db.session.query(TicketRepuesto).filter_by(estado_pago="Pagado").count(),
    }

    return render_template(
        "ticket_repuesto/tabla_repuestos.html",
        ticketsRepuesto=tickets_repuesto,
        estado_taller_filtro=estado_taller_filtro,
        estado_pago_filtro=estado_pago_filtro,
        search_termino=search_termino,
        fecha=fecha,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        total_items=total_items,
        counts_taller=counts_taller,
        counts_pago=counts_pago,
    )
