from itsdangerous import URLSafeTimedSerializer
from flask import current_app

def generar_token_correo(correo):
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return s.dumps(correo, salt='recuperar-contrasena')

def verificar_token_correo(token, max_age=1800):  # 30 minutos
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        correo = s.loads(token, salt='recuperar-contrasena', max_age=max_age)
    except Exception as e:
        print(f"[ERROR] Token inválido o expirado: {e}")
        return None
    return correo
