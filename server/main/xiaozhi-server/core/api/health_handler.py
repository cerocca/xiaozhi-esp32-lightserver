from aiohttp import web

from app.services.health_service import (
    check_asr,
    check_device,
    check_llm,
    check_tts,
)
from core.api.base_handler import BaseHandler


class HealthHandler(BaseHandler):
    def __init__(self, config: dict, ws_server=None):
        super().__init__(config)
        self.ws_server = ws_server

    async def handle_get(self, request):
        config = self.ws_server.config if self.ws_server else self.config
        response = web.json_response(
            {
                "llm": check_llm(config),
                "asr": check_asr(config),
                "tts": check_tts(config),
                "device": check_device(self.ws_server),
            }
        )
        self._add_cors_headers(response)
        return response

