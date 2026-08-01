from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from common.security.dependencies import get_current_principal
from common.security.principal import CurrentPrincipal
from communication_service.db.db_session import get_session
from communication_service.repositories.repository_chat_member import ChatMemberRepository


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
    return principal
