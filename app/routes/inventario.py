from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import Inventario

inventario_bp = Blueprint("inventario", __name__, template_folder="templates")


# Función auxiliar para validar datos del formulario
def validar_inventario_formulario(form):
    nombre_form = form.get("nombre", "").strip()
    codigo_form = form.get("codigo", "").strip()
    stock_form = form.get("stock", "").strip()
    precio_compra_form = form.get("precio_compra", "").strip()
    porcentaje_form = form.get("porcentaje", "").strip()

    if not nombre_form or not codigo_form or not stock_form or not precio_compra_form or not porcentaje_form:
        raise ValueError("Todos los campos son obligatorios.")

    try:
        stock = int(stock_form)
        if stock < 0:
            raise ValueError("Stock negativo")
    except ValueError:
        raise ValueError("El stock debe ser un número entero positivo.")

    try:
        precio_compra = float(precio_compra_form)
        if precio_compra < 0:
            raise ValueError("Precio_compra negativo")
    except ValueError:
        raise ValueError("El precio_compra debe ser un número positivo.")

    try:
        porcentaje = float(porcentaje_form)
        if porcentaje < 0:
            raise ValueError("Porcentaje negativo")
    except ValueError:
        raise ValueError("El porcentaje debe ser un número positivo.")

    nombre = nombre_form
    codigo = codigo_form
    return (
        nombre,
        codigo,
        stock,
        precio_compra,
        porcentaje
    )


@inventario_bp.route("/panel/inventario")
def ver_inventario():
    search = request.args.get("search", "", type=str).strip()
    stock_filter = request.args.get("stock_filter", "", type=str).strip()
    page = request.args.get("page", 1, type=int)
    per_page = 10  # cantidad de productos por página

    query = Inventario.query

    # Aplicar filtro de búsqueda
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            db.or_(
                Inventario.codigo.ilike(search_filter),
                Inventario.nombre.ilike(search_filter),
            )
        )

    # Aplicar filtro de stock
    if stock_filter == "low":
        query = query.filter(Inventario.stock < 10)
    elif stock_filter == "normal":
        query = query.filter(Inventario.stock >= 10)

    # Ordenar por nombre
    query = query.order_by(Inventario.nombre)

    # Aplicar paginación
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    items = pagination.items
    total_pages = pagination.pages
    total_items = pagination.total

    # Calcular estadísticas de stock
    stock_bajo_count = Inventario.query.filter(Inventario.stock < 10).count()
    sin_stock_count = Inventario.query.filter(Inventario.stock == 0).count()

    return render_template(
        "inventario/inventario.html",
        items=items,  # Cambiado de 'productos' a 'items' para coincidir con la plantilla
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        total_items=total_items,
        stock_bajo=stock_bajo_count,
        sin_stock=sin_stock_count,
        search_termino=search,  
        estado_filtro=stock_filter
    )

@inventario_bp.route("/inventario/nuevo_producto", methods=["GET", "POST"])
def nuevo_producto():
    if request.method == "POST":
        form = request.form
        try:
            nombre, codigo, stock, precio_compra, porcentaje = validar_inventario_formulario(form)

            precio_compra_iva = precio_compra * 1.19
            precio_venta = precio_compra_iva * (1 + porcentaje / 100)

            nuevo_item = Inventario(
                nombre=nombre,
                codigo=codigo,
                stock=stock,
                precio_compra=precio_compra,
                porcentaje=porcentaje,
                precio_venta=precio_venta
            )

            db.session.add(nuevo_item)
            db.session.commit()

            flash("Producto agregado correctamente.", "success")
            return redirect(url_for("inventario.ver_inventario"))

        except ValueError as e:
            flash(str(e), "danger")
        except Exception as e:
            flash("Error inesperado al agregar el producto.", "danger")

    return render_template("inventario/nuevo_producto.html")



@inventario_bp.route("/inventario/editar_producto/<int:id>", methods=["GET", "POST"])
def editar_producto(id):
    producto = Inventario.query.get_or_404(id)

    if request.method == "POST":
        form = request.form
        try:
            nombre, codigo, stock, precio_compra, porcentaje = validar_inventario_formulario(form)
            
            # Asegurarse de que porcentaje es un número
            try:
                porcentaje = float(porcentaje)
                if porcentaje < 0:
                    raise ValueError("Porcentaje negativo")
            except ValueError:
                raise ValueError("El porcentaje debe ser un número positivo.")

            # Calcular nuevo precio_venta
            precio_compra_iva = precio_compra * 1.19
            precio_venta = precio_compra_iva * (1 + porcentaje / 100)

            producto.nombre = nombre
            producto.codigo = codigo
            producto.stock = stock
            producto.precio_compra = precio_compra
            producto.porcentaje = porcentaje
            producto.precio_venta = precio_venta  # Actualizar precio_venta

            db.session.commit()

            flash("Producto actualizado con éxito.", "success")
            return redirect(url_for("inventario.ver_inventario"))

        except ValueError as e:
            flash(str(e), "danger")

    return render_template("inventario/editar_producto.html", producto=producto)


# Eliminar Inventario
@inventario_bp.route("/inventario/eliminar_producto/<int:id>", methods=["POST"])
def eliminar_producto(id):
    try:
        item = Inventario.query.get_or_404(id)
        db.session.delete(item)
        db.session.commit()
        flash("Inventario eliminado.", "success")
    except Exception:
        flash("No se pudo eliminar el producto.", "danger")
    return redirect(url_for("inventario.ver_inventario"))


# Inventarios bajo stock (< 10 unidades)
@inventario_bp.route("/inventario/bajo_stock")
def bajo_stock():
    items = (
        Inventario.query.filter(Inventario.stock < 10).order_by(Inventario.nombre).all()
    )
    return render_template("inventario/pedidos_stock.html", items=items)


@inventario_bp.route("/inventario/actualizar_stock_producto/<int:id>", methods=["POST"])
def actualizar_stock(id):
    item = Inventario.query.get_or_404(id)

    try:
        cantidad_str = request.form.get("cantidad", "").strip()

        cantidad = int(cantidad_str)
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser un número entero positivo.")

        item.stock += cantidad  # Sumamos al stock actual
        db.session.commit()

        flash(f"Stock de '{item.nombre}' actualizado: +{cantidad}.", "success")

    except (ValueError, TypeError):
        flash("La cantidad debe ser un número entero positivo.", "danger")
    except Exception:
        flash("Error al actualizar el stock.", "danger")

    return redirect(url_for("inventario.bajo_stock"))
