from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required

from app.auth import auth_bp
from app.auth.forms import LoginForm, RecuperarContrasenaForm, RestablecerContrasenaForm
from app.models import Usuario
from app.auth.tokens import generar_token_correo, verificar_token_correo
from app.auth.email import enviar_correo

# ruta principal
# 1. verificar si esta logeado
# 2. si no esta logeado, la ruta sirve para el formulario del login
# 3. si esta logeado o se logea, lo redirije al dashboard
@auth_bp.route('/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('taller.tickets_en_taller'))

    form = LoginForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            usuario = Usuario.query.filter_by(correo=form.correo.data).first()
            if usuario and usuario.check_password(form.contrasena.data):
                login_user(usuario)
                flash("Sesión iniciada correctamente", "success")
                print("[INFO] Sesión iniciada correctamente")
                return redirect(url_for('taller.tickets_en_taller'))
            
            flash("Correo o contraseña incorrectos", "danger")
            print("[WARNING] Intento fallido")

    return render_template('auth/login.html', form=form)

#ruta de logout
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada", "info")
    return redirect(url_for('auth.login'))

# ruta para recuperar contrasena
@auth_bp.route('/recuperar_contrasena', methods=['GET', 'POST'])
def recuperar_contrasena():
    form = RecuperarContrasenaForm()

    if form.validate_on_submit():
        correo = form.correo.data
        usuario = Usuario.query.filter_by(correo=correo).first()

        if usuario:
            token = generar_token_correo(correo)
            enlace = url_for('auth.restablecer_contrasena', token=token, _external=True)

            cuerpo_html = f"""
            <p>Hola,</p>
            <p>Haz clic en el siguiente enlace para restablecer tu contraseña:</p>
            <p><a href="{enlace}">{enlace}</a></p>
            <p>Este enlace caduca en 30 minutos.</p>
            """

            enviar_correo(correo, 'Recuperación de contraseña - HYF frenos', cuerpo_html)

            flash('Se ha enviado un enlace de recuperación a tu correo.', 'info')
        else:
            flash('No se encontró una cuenta con ese correo.', 'danger')
    
    

    return render_template('auth/recuperar_contrasena.html', form=form)

# ruta para restablecer contrasena con el token
@auth_bp.route('/restablecer_contrasena/<token>', methods=['GET', 'POST'])
def restablecer_contrasena(token):
    correo = verificar_token_correo(token)
    if not correo:
        flash("El enlace no es válido o ha expirado", "danger")
        return redirect(url_for('auth.login'))

    form = RestablecerContrasenaForm()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(correo=correo).first()
        if usuario:
            usuario.set_password(form.contrasena.data)
            usuario.guardar()  # o db.session.commit() si no tienes método guardar()
            flash("Tu contraseña ha sido restablecida correctamente", "success")
            return redirect(url_for('auth.login'))

        flash("Usuario no encontrado", "danger")
        return redirect(url_for('auth.recuperar_contrasena'))

    return render_template('auth/restablecer_contrasena.html', form=form)