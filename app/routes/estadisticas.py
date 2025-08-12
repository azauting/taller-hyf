from flask import Blueprint, render_template, request
from datetime import datetime
from app.models import Inventario, TicketServicio, TicketRepuesto
from app import db
from sqlalchemy import func, extract

estadisticas_bp = Blueprint('estadisticas', __name__, template_folder='templates')

@estadisticas_bp.route('/panel/estadisticas')
def ver_estadisticas():
    # Datos KPIs originales
    valor_inventario = db.session.query(
        func.sum(Inventario.precio_venta * Inventario.stock)
    ).scalar() or 0

    tickets_servicio = db.session.query(
        func.coalesce(func.sum(TicketServicio.total), 0)
    ).filter(
        TicketServicio.estado_taller == "Entregado",
        TicketServicio.estado_pago == "Pagado"
    ).scalar()

    tickets_repuestos = db.session.query(
        func.coalesce(func.sum(TicketRepuesto.total), 0)
    ).filter(
        TicketRepuesto.estado_taller == "Entregado",
        TicketRepuesto.estado_pago == "Pagado"
    ).scalar()

    costo_inversion = db.session.query(
        func.sum(Inventario.precio_compra * Inventario.stock)
    ).scalar() or 0

    ingresos_totales = tickets_servicio + tickets_repuestos
    utilidad_global = ingresos_totales - costo_inversion

    # Parámetros mes y año (por GET)
    mes = request.args.get('mes', type=int)
    ano = request.args.get('ano', type=int)
    
    total_filtrado = None
    if mes and ano:
        total_servicios_mes = db.session.query(
            func.coalesce(func.sum(TicketServicio.total), 0)
        ).filter(
            TicketServicio.estado_taller == "Entregado",
            TicketServicio.estado_pago == "Pagado",
            extract('month', TicketServicio.fecha_creacion) == mes,
            extract('year', TicketServicio.fecha_creacion) == ano
        ).scalar()

        total_repuestos_mes = db.session.query(
            func.coalesce(func.sum(TicketRepuesto.total), 0)
        ).filter(
            TicketRepuesto.estado_taller == "Entregado",
            TicketRepuesto.estado_pago == "Pagado",
            extract('month', TicketRepuesto.fecha_creacion) == mes,
            extract('year', TicketRepuesto.fecha_creacion) == ano
        ).scalar()

        total_filtrado = total_servicios_mes + total_repuestos_mes

    current_year = datetime.now().year

    return render_template(
        'estadisticas/estadisticas.html',
        valor_inventario=valor_inventario,
        tickets_servicio=tickets_servicio,
        tickets_repuestos=tickets_repuestos,
        utilidad_global=utilidad_global,
        costo_inversion=costo_inversion,
        ingresos_totales=ingresos_totales,
        mes=mes,
        ano=ano,
        total_filtrado=total_filtrado,
        current_year=current_year
    )
