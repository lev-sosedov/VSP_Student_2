from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from common.security.dependencies import get_current_principal
from common.security.principal import CurrentPrincipal
from communication_service.db.db_session import get_session
from communication_service.repositories.repository_chat_member import ChatMemberRepository
from communication_service.models.model_chat import Chat
from communication_service.messaging.messaging_rpc_client import communication_rpc_client


async def require_chat_member(
    request: Request,
    principal: CurrentPrincipal = Depends(get_current_principal),
    session: AsyncSession = Depends(get_session),
) -> CurrentPrincipal:
    raw_chat_id = request.path_params.get("chat_id") or request.query_params.get("chat_id")
    try:
        chat_id = int(raw_chat_id)
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Chat membership required") from exc
    member = await ChatMemberRepository(session).get_member(chat_id, principal.user_id)
    if member is None or not member.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Chat membership required")
    chat = await session.get(Chat, chat_id)
    if chat is None or not chat.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
    if chat.group_id is not None:
        try:
            response = await communication_rpc_client.call_academic(
                method="academic.authorization.membership",
                payload={"user_id": principal.user_id, "group_id": chat.group_id, "role": "student"},
                timeout=2.0,
            )
            if not isinstance(response, dict) or response.get("success") is not True or response.get("exists") is not True or response.get("is_active") is not True:
                raise ValueError("inactive academic membership")
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Academic group authorization unavailable") from exc
    return principal
