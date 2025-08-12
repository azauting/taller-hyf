from flask import Blueprint, jsonify, render_template, request, redirect, url_for, flash
from sqlalchemy import func, or_
from app import db
from app.models import Cliente, TicketServicio, Vehiculo, TicketRepuesto

cliente_bp = Blueprint("cliente", __name__, template_folder="templates")


@cliente_bp.route("/panel/cliente")
def ver_clientes():
    # Obtener parámetros
    page = request.args.get('page', 1, type=int)
    per_page = 10
    search_term = request.args.get('search', '') 

    # Construir consulta base
    query = Cliente.query.order_by(Cliente.nombre.asc())

    # Aplicar búsqueda si existe
    if search_term:
        search = f"%{search_term}%"
        query = query.filter(
            db.or_(
                Cliente.nombre.ilike(search),
                Cliente.apellido.ilike(search),
                Cliente.telefono.ilike(search),
            )
        )

    # Paginar resultados
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    # Calcular estadísticas
    total_clientes = Cliente.query.count()
    total_vehicles = db.session.query(Vehiculo).count()
    total_tickets = db.session.query(TicketServicio).join(Vehiculo).join(Cliente).count()

    return render_template(
        "cliente/clientes.html",
        cliente=pagination.items,
        pagination=pagination,
        counts={
            'total': total_clientes,
            'vehicles': total_vehicles,
            'tickets': total_tickets
        },
        search_term=search_term
    )

@cliente_bp.route("/panel/cliente/<int:id>")
def ver_cliente(id):
    cliente = Cliente.query.get_or_404(id)

    # Configuración de paginación
    page_servicios_pagados = request.args.get('page_servicios_pagados', 1, type=int)
    page_servicios_pendientes = request.args.get('page_servicios_pendientes', 1, type=int)
    page_repuestos_pagados = request.args.get('page_repuestos_pagados', 1, type=int)
    page_repuestos_pendientes = request.args.get('page_repuestos_pendientes', 1, type=int)
    per_page = 10  # Número de items por página

    # Tickets de Servicio (pagados y pendientes)
    tickets_servicio_pagados = (
        TicketServicio.query
        .join(Vehiculo)
        .filter(
            Vehiculo.cliente_id == cliente.id,
            TicketServicio.estado_pago == "Pagado"
        )
        .order_by(TicketServicio.fecha_creacion.desc())
        .paginate(page=page_servicios_pagados, per_page=per_page, error_out=False)
    )

    tickets_servicio_pendientes = (
        TicketServicio.query
        .join(Vehiculo)
        .filter(
            Vehiculo.cliente_id == cliente.id,
            TicketServicio.estado_pago == "Pendiente"
        )
        .order_by(TicketServicio.fecha_creacion.desc())
        .paginate(page=page_servicios_pendientes, per_page=per_page, error_out=False)
    )

    # Tickets de Repuesto (pagados y pendientes)
    tickets_repuesto_pagados = (
        TicketRepuesto.query
        .filter_by(
            cliente_id=cliente.id,
            estado_pago="Pagado"
        )
        .order_by(TicketRepuesto.fecha_creacion.desc())
        .paginate(page=page_repuestos_pagados, per_page=per_page, error_out=False)
    )

    tickets_repuesto_pendientes = (
        TicketRepuesto.query
        .filter_by(
            cliente_id=cliente.id,
            estado_pago="Pendiente"
        )
        .order_by(TicketRepuesto.fecha_creacion.desc())
        .paginate(page=page_repuestos_pendientes, per_page=per_page, error_out=False)
    )

    # Calcular deudas totales
    deuda_servicios = sum(ticket.total for ticket in tickets_servicio_pendientes.items)
    deuda_repuestos = sum(ticket.total for ticket in tickets_repuesto_pendientes.items)

    return render_template(
        "cliente/ver_cliente.html",
        cliente=cliente,
        tickets_servicio_pagados=tickets_servicio_pagados,
        tickets_servicio_pendientes=tickets_servicio_pendientes,
        tickets_repuesto_pagados=tickets_repuesto_pagados,
        tickets_repuesto_pendientes=tickets_repuesto_pendientes,
        deuda_servicios=deuda_servicios,
        deuda_repuestos=deuda_repuestos
    )


# ruta para el form del ticket
@cliente_bp.route("/cliente/ajax-crear", methods=["POST"])
def crear_cliente_ajax():
    nombre = request.form["nombre"]
    apellido = request.form["apellido"]
    telefono = request.form["telefono"]

    if not nombre or not apellido or not telefono:
        flash("Todos los campos son obligatorios.", "danger")
        return redirect(url_for("ticket.nuevo_ticket"))

    # Verificar si el teléfono ya está registrado
    existente = Cliente.query.filter_by(telefono=telefono).first()
    if existente:
        flash("Este teléfono ya está registrado.", "danger")
        return redirect(url_for("ticket.nuevo_ticket"))

    cliente = Cliente(nombre=nombre, apellido=apellido, telefono=telefono)
    db.session.add(cliente)
    db.session.commit()
    flash("Cliente registrado correctamente.", "success")
    return {
        "id": cliente.id,
        "nombre": cliente.nombre,
        "apellido": cliente.apellido,
        "telefono": cliente.telefono,
    }


# Registrar un nuevo cliente
@cliente_bp.route("/panel/cliente/nuevo", methods=["GET", "POST"])
def nuevo_cliente():
    if request.method == "POST":
        form = request.form
        nombre = form.get("nombre", "").strip()
        apellido = form.get("apellido", "").strip()
        telefono = form.get("telefono", "").strip()

        # Validación básica
        if not nombre or not apellido or not telefono:
            flash("Todos los campos son obligatorios.", "danger")
            return render_template("cliente/nuevo_cliente.html")

        # Verificar si el teléfono ya está registrado
        existente = Cliente.query.filter_by(telefono=telefono).first()
        if existente:
            flash("Este teléfono ya está registrado.", "danger")
            return render_template("cliente/nuevo_cliente.html")

        # Crear nuevo cliente
        nuevo = Cliente(
            nombre=nombre, apellido=apellido, telefono=telefono
        )
        db.session.add(nuevo)
        db.session.commit()

        flash("Cliente registrado correctamente.", "success")
        return redirect(url_for("cliente.ver_clientes"))

    return render_template("cliente/nuevo_cliente.html")


# ruta para editar cliente
@cliente_bp.route("/panel/cliente/editar/<int:id>", methods=["GET", "POST"])
def editar_cliente(id):
    cliente = Cliente.query.get_or_404(id)

    if request.method == "POST":
        form = request.form
        nombre = form.get("nombre", "").strip()
        apellido = form.get("apellido", "").strip()
        telefono = form.get("telefono", "").strip()

        if not nombre or not apellido or not telefono:
            flash("Nombre, apellido y teléfono son obligatorios.", "danger")
            return render_template("cliente/editar_cliente.html", cliente=cliente)


        telefono_existente = Cliente.query.filter(
            Cliente.telefono == telefono, Cliente.id != id
        ).first()
        if telefono_existente:
            flash("El teléfono ya está registrado por otro cliente.", "danger")
            return render_template("cliente/editar_cliente.html", cliente=cliente)

        cliente.nombre = nombre
        cliente.apellido = apellido
        cliente.telefono = telefono

        db.session.commit()
        flash("Cliente actualizado correctamente.", "success")
        return redirect(url_for("clientes.ver_clientes"))

    return render_template("cliente/editar_cliente.html", cliente=cliente)


# Eliminar cliente
@cliente_bp.route("/panel/cliente/eliminar/<int:id>", methods=["POST"])
def eliminar_cliente(id):
    item = Cliente.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash("Cliente eliminado correctamente.", "success")
    return redirect(url_for("cliente.ver_clientes"))


@cliente_bp.route('/panel/cliente/buscar')
def buscar_clientes():
    query = request.args.get('q', '').strip()
    
    if len(query) < 2:
        return jsonify([])
    
    clientes = Cliente.query.filter(
        or_(
            Cliente.nombre.ilike(f'%{query}%'),
            Cliente.apellido.ilike(f'%{query}%'),
            Cliente.telefono.ilike(f'%{query}%'),
            func.concat(Cliente.nombre, ' ', Cliente.apellido).ilike(f'%{query}%'),
        )
    ).limit(10).all()
    
    resultados = [{
        'id': c.id,
        'nombre': c.nombre,
        'apellido': c.apellido,
        'telefono': c.telefono
    } for c in clientes]
    
    return jsonify(resultados)