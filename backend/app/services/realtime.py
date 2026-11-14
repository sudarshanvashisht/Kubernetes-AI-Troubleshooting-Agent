"""Realtime progress notification service (InsForge Socket.IO)."""

import aiohttp
if not hasattr(aiohttp, "ClientWSTimeout"):
    class ClientWSTimeout:
        def __init__(self, *, ws_receive=None, ws_close=10.0):
            self.ws_receive = ws_receive
            self.ws_close = ws_close
    aiohttp.ClientWSTimeout = ClientWSTimeout

import socketio
from loguru import logger

from app.core.config import settings


class RealtimeService:
    def __init__(self):
        self.sio = socketio.AsyncClient(logger=False, engineio_logger=False)
        self.url = settings.insforge_url
        self.token = settings.insforge_anon_key
        self._warned = False

    def _available(self) -> bool:
        if not self.url or not self.token:
            if not self._warned:
                logger.warning("InsForge realtime not configured; realtime progress disabled.")
                self._warned = True
            return False
        return True

    async def connect(self):
        if not self._available():
            return
        if not self.sio.connected:
            try:
                await self.sio.connect(self.url, auth={"token": self.token})
            except Exception as e:
                logger.warning("Failed to connect to InsForge realtime", exc_info=e)

    async def emit_progress(self, investigation_id, message, user_id=None):
        if not investigation_id or not self._available():
            return
        try:
            await self.connect()
            if not self.sio.connected:
                return
            channel = f"investigation:{user_id or 'anon'}:{investigation_id}"
            await self.sio.emit("realtime:subscribe", {"channel": channel})
            await self.sio.emit("realtime:publish", {"channel": channel, "event": "progress", "payload": {"message": message}})
        except Exception as e:
            logger.warning("Failed to emit realtime progress", exc_info=e)


realtime_service = RealtimeService()
