from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class LoginForm(FlaskForm):
    correo = StringField("Correo", validators=[DataRequired(), Email()])
    contrasena = PasswordField("Contraseña", validators=[DataRequired()])
    submit = SubmitField("Iniciar sesión")

class RecuperarContrasenaForm(FlaskForm):
    correo = StringField("Correo electrónico", validators=[DataRequired(), Email()])
    submit = SubmitField("Enviar enlace de recuperación")

class RestablecerContrasenaForm(FlaskForm):
    contrasena = PasswordField("Nueva contraseña", validators=[DataRequired(), Length(min=6)])
    confirmar = PasswordField("Confirmar contraseña", validators=[
        DataRequired(), EqualTo('contrasena', message="Las contraseñas no coinciden")
    ])
    submit = SubmitField("Restablecer contraseña")