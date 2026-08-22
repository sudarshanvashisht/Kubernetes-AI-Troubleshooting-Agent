"""Realtime progress notification service for InsForge Realtime."""

import aiohttp
# Monkeypatch ClientWSTimeout which is missing in this environment's aiohttp version
if not hasattr(aiohttp, "ClientWSTimeout"):
    class ClientWSTimeout:
        def __init__(self, *, ws_receive=None, ws_close=10.0):
            self.ws_receive = ws_receive
            self.ws_close = ws_close
    aiohttp.ClientWSTimeout = ClientWSTimeout

import socketio
from loguru import logger


class RealtimeService:
    """Service to emit real-time investigation progress over Socket.IO to InsForge."""

    def __init__(self):
        self.sio = socketio.AsyncClient(logger=False, engineio_logger=False)
        self.url = "https://h7d3q8mn.us-east.insforge.app"
        self.token = "anon_c955b75459fc1cb6eda4cddaa2725ff7b89c36b9aeabc447b57067e3afcd88c8"

    async def connect(self):
        """Connect to InsForge Realtime Socket.IO if not already connected."""
        if not self.sio.connected:
            await self.sio.connect(self.url, auth={"token": self.token})

    async def emit_progress(self, investigation_id: str | None, message: str):
        """Emit progress update to the investigation's realtime channel."""
        if not investigation_id:
            return

        try:
            await self.connect()
            channel = f"investigation:{investigation_id}"

            # Subscribe first (required by InsForge Realtime before publishing)
            await self.sio.emit("realtime:subscribe", {"channel": channel})

            # Publish event
            await self.sio.emit(
                "realtime:publish",
                {
                    "channel": channel,
                    "event": "progress",
                    "payload": {"message": message},
                },
            )
            logger.info(f"Emitted progress to {channel}: {message}")
        except Exception as e:
            logger.error(f"Failed to emit realtime progress: {e}")


realtime_service = RealtimeService()
