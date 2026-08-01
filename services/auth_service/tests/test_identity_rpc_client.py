import asyncio
import os
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

os.environ.setdefault("RABBITMQ_USERNAME", "test")
os.environ.setdefault("RABBITMQ_PASSWORD", "test")

from auth_service.messaging import messaging_rpc_client as client_module


@pytest.mark.asyncio
async def test_concurrent_start_opens_only_one_connection(monkeypatch):
    callback_queue = SimpleNamespace(consume=AsyncMock(), name="callback")
    channel = SimpleNamespace(
        is_closed=False,
        declare_queue=AsyncMock(return_value=callback_queue),
        close=AsyncMock(),
    )
    connection = SimpleNamespace(
        is_closed=False,
        channel=AsyncMock(return_value=channel),
        close=AsyncMock(),
    )
    connect = AsyncMock(return_value=connection)
    monkeypatch.setattr(client_module.aio_pika, "connect_robust", connect)

    client = client_module.UserIdentityRpcClient()
    await asyncio.gather(client.start(), client.start())

    connect.assert_awaited_once()
    channel.declare_queue.assert_awaited_once_with(exclusive=True, auto_delete=True)
    callback_queue.consume.assert_awaited_once_with(client._on_response, no_ack=True)


@pytest.mark.asyncio
async def test_stop_closes_channel_and_connection_and_cancels_pending():
    channel = SimpleNamespace(is_closed=False, close=AsyncMock())
    connection = SimpleNamespace(is_closed=False, close=AsyncMock())
    client = client_module.UserIdentityRpcClient()
    client.channel = channel
    client.connection = connection
    pending = asyncio.get_running_loop().create_future()
    client.pending["request"] = pending

    await client.stop()

    assert pending.cancelled()
    channel.close.assert_awaited_once()
    connection.close.assert_awaited_once()
    assert client.channel is None and client.connection is None


@pytest.mark.asyncio
async def test_call_times_out_and_removes_pending_request(monkeypatch):
    exchange = SimpleNamespace(publish=AsyncMock())
    client = client_module.UserIdentityRpcClient()
    client.start = AsyncMock()
    client.channel = SimpleNamespace(default_exchange=exchange)
    client.callback_queue = SimpleNamespace(name="callback")
    monkeypatch.setattr(client_module.rabbitmq_settings, "rpc_timeout_seconds", 0.001)

    with pytest.raises(asyncio.TimeoutError):
        await client.resolve_by_auth_id(7)

    assert client.pending == {}
    published = exchange.publish.await_args
    assert published.kwargs["routing_key"] == client_module.rabbitmq_settings.user_rpc_queue
    assert published.args[0].correlation_id
    assert published.args[0].reply_to == "callback"


@pytest.mark.asyncio
async def test_invalid_json_response_fails_pending_call_without_details():
    client = client_module.UserIdentityRpcClient()
    future = asyncio.get_running_loop().create_future()
    client.pending["request"] = future
    message = SimpleNamespace(correlation_id="request", body=b"not-json")

    await client._on_response(message)

    with pytest.raises(RuntimeError, match="Invalid RPC response"):
        await future
    assert client.pending == {}
