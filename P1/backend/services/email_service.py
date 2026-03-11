import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailService:

    def __init__(self, host, port, usuario, password):
        self.host = host
        self.port = port
        self.usuario = usuario
        self.password = password

    def enviar(self, destinatario, asunto, contenido):

        msg = MIMEMultipart()
        msg["Subject"] = asunto
        msg["From"] = self.usuario
        msg["To"] = destinatario

        msg.attach(MIMEText(contenido, "plain", "utf-8"))

        with smtplib.SMTP(self.host, self.port) as srv:
            srv.starttls()
            srv.login(self.usuario, self.password)
            srv.sendmail(self.usuario, destinatario, msg.as_string())

        return True