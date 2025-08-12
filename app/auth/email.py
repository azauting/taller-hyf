import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate
from flask import current_app

def enviar_correo(destinatario, asunto, cuerpo_html):
    remitente = current_app.config['MAIL_USERNAME']
    password = current_app.config['MAIL_PASSWORD']

    # Reemplazar espacio no separable para evitar error
    cuerpo_html = cuerpo_html.replace('\xa0', ' ')

    msg = MIMEMultipart('alternative')
    msg['Subject'] = asunto
    msg['From'] = remitente
    msg['To'] = destinatario

    parte_html = MIMEText(cuerpo_html, 'html', 'utf-8')
    msg.attach(parte_html)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as servidor:
            servidor.login(remitente, password)
            servidor.sendmail(remitente, destinatario, msg.as_string())
        print(f"[INFO] Correo enviado a {destinatario}")
    except Exception as e:
        print(f"[ERROR] No se pudo enviar el correo: {e}")