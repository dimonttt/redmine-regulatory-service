from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
from pathlib import Path
from datetime import datetime
import smtplib
from jinja2 import Environment, FileSystemLoader
from app.config import settings

logger = logging.getLogger(__name__)
TEMPLATES_DIR = Path(__file__).parent.parent / "templates"

def send_report_email(period_year: int, period_month: int, clients_data: list[dict]):
    if not settings.smtp_user or not settings.report_email:
        logger.warning("SMTP не настроен, письмо не отправлено")
        return False

    try:
        env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
        template = env.get_template("email_report.html")

        html_content = template.render(
            period_year=period_year,
            period_month=period_month,
            generated_at=datetime.now().strftime("%d.%m.%Y %H:%M"),
            clients=clients_data,
        )

        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Отчет по выработке за {period_year}-{period_month}"
        msg["From"] = settings.smtp_user
        msg["To"] = settings.report_email

        msg.attach(MIMEText(html_content, "html", "utf-8"))

        with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port) as server:
            server.login(settings.smtp_user,settings.smtp_password)
            server.send_message(msg)

        logger.info(f"Письмо отправлено на {settings.report_email}")
        return True
    except Exception as e:
        logger.error(f"Ошибки отправки почты: {e}")
        return False