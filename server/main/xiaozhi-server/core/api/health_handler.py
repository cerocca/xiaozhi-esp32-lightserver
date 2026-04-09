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
        llm_details = check_llm(config)
        asr_details = check_asr(config)
        tts_details = check_tts(config)
        device_details = check_device(self.ws_server)
        response = web.json_response(
            {
                "llm": llm_details["status"],
                "asr": asr_details["status"],
                "tts": tts_details["status"],
                "device": device_details["status"],
                "details": {
                    "llm": llm_details,
                    "asr": asr_details,
                    "tts": tts_details,
                    "device": device_details,
                },
            }
        )
        self._add_cors_headers(response)
        return response
