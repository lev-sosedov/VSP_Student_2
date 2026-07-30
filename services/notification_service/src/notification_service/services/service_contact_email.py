import asyncio
import smtplib
import ssl
from email.message import EmailMessage
from email.utils import formataddr

from notification_service.core.core_config import (
    settings
)
from notification_service.schemas.schemas_contact import (
    ContactMessageRequest
)


class ContactEmailService:
    async def send(
        self,
        contact_data: ContactMessageRequest,
        client_ip: str | None = None,
        user_agent: str | None = None
    ) -> None:
        await asyncio.to_thread(
            self._send_sync,
            contact_data,
            client_ip,
            user_agent
        )

    def _send_sync(
        self,
        contact_data: ContactMessageRequest,
        client_ip: str | None,
        user_agent: str | None
    ) -> None:
        smtp_user = settings.SMTP_USER.strip()
        smtp_password = settings.SMTP_PASSWORD.strip()

        receiver = (
            settings.CONTACT_RECEIVER_EMAIL.strip()
            or smtp_user
        )

        if not smtp_user:
            raise RuntimeError(
                "SMTP_USER не настроен"
            )

        if not smtp_password:
            raise RuntimeError(
                "SMTP_PASSWORD не настроен"
            )

        if not receiver:
            raise RuntimeError(
                "CONTACT_RECEIVER_EMAIL не настроен"
            )

        message = EmailMessage()

        message["Subject"] = (
            "Новая заявка с сайта ВШП Студент"
        )

        message["From"] = formataddr(
            (
                "ВШП Студент — форма сайта",
                smtp_user
            )
        )

        message["To"] = receiver
        message["Reply-To"] = contact_data.email

        message.set_content(
            "\n".join(
                [
                    "Новая заявка с публичного сайта",
                    "",
                    f"Имя: {contact_data.name}",
                    f"Телефон: {contact_data.phone}",
                    f"Email: {contact_data.email}",
                    f"Филиал: {contact_data.branch}",
                    "",
                    "Сообщение:",
                    contact_data.message,
                    "",
                    "Техническая информация:",
                    f"IP: {client_ip or 'не определён'}",
                    (
                        "User-Agent: "
                        f"{user_agent or 'не определён'}"
                    ),
                ]
            )
        )

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL(
            host=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            context=context,
            timeout=settings.SMTP_TIMEOUT_SECONDS
        ) as smtp:
            smtp.login(
                smtp_user,
                smtp_password
            )

            smtp.send_message(message)
