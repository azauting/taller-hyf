from flask import Blueprint, render_template, request, jsonify
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

@estadisticas_bp.route('/panel/estadisticas/datos-grafico')
def datos_grafico():
    # Obtener datos para el gráfico de los últimos 12 meses
    end_date = datetime.now()
    start_date = datetime(end_date.year - 1, end_date.month, end_date.day)
    
    # Consulta para servicios
    servicios_data = db.session.query(
        extract('month', TicketServicio.fecha_creacion).label('mes'),
        extract('year', TicketServicio.fecha_creacion).label('ano'),
        func.coalesce(func.sum(TicketServicio.total), 0).label('total')
    ).filter(
        TicketServicio.estado_taller == "Entregado",
        TicketServicio.estado_pago == "Pagado",
        TicketServicio.fecha_creacion >= start_date
    ).group_by(
        extract('year', TicketServicio.fecha_creacion),
        extract('month', TicketServicio.fecha_creacion)
    ).all()
    
    # Consulta para repuestos
    repuestos_data = db.session.query(
        extract('month', TicketRepuesto.fecha_creacion).label('mes'),
        extract('year', TicketRepuesto.fecha_creacion).label('ano'),
        func.coalesce(func.sum(TicketRepuesto.total), 0).label('total')
    ).filter(
        TicketRepuesto.estado_taller == "Entregado",
        TicketRepuesto.estado_pago == "Pagado",
        TicketRepuesto.fecha_creacion >= start_date
    ).group_by(
        extract('year', TicketRepuesto.fecha_creacion),
        extract('month', TicketRepuesto.fecha_creacion)
    ).all()
    
    # Combinar datos
    meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 
             'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    
    # Crear estructura para 12 meses
    datos_grafico = {
        'labels': [],
        'servicios': [0] * 12,
        'repuestos': [0] * 12,
        'total': [0] * 12
    }
    
    current_month = end_date.month
    for i in range(12):
        month_index = (current_month - 1 - i) % 12
        year = end_date.year if (current_month - i) > 0 else end_date.year - 1
        datos_grafico['labels'].insert(0, f"{meses[month_index]} {year}")
        
    # Llenar datos de servicios
    for dato in servicios_data:
        month_index = dato.mes - 1
        year_diff = end_date.year - dato.ano
        if year_diff == 0:
            pos = (current_month - 1) - (current_month - dato.mes)
        elif year_diff == 1:
            pos = (current_month - 1) + (12 - (current_month - dato.mes))
        else:
            continue
            
        if 0 <= pos < 12:
            datos_grafico['servicios'][pos] = float(dato.total)
            datos_grafico['total'][pos] += float(dato.total)
    
    # Llenar datos de repuestos
    for dato in repuestos_data:
        month_index = dato.mes - 1
        year_diff = end_date.year - dato.ano
        if year_diff == 0:
            pos = (current_month - 1) - (current_month - dato.mes)
        elif year_diff == 1:
            pos = (current_month - 1) + (12 - (current_month - dato.mes))
        else:
            continue
            
        if 0 <= pos < 12:
            datos_grafico['repuestos'][pos] = float(dato.total)
            datos_grafico['total'][pos] += float(dato.total)
    
    return jsonify(datos_grafico)