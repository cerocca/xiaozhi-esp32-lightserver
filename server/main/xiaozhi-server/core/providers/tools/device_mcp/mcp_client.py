"""设备端MCP客户端定义"""

import asyncio
from concurrent.futures import Future
from core.utils.util import sanitize_tool_name
from config.logger import setup_logging

TAG = __name__
logger = setup_logging()
VOLUME_TOOL_NAME = "self.audio_speaker.set_volume"


class MCPClient:
    """设备端MCP客户端，用于管理MCP状态和工具"""

    def __init__(self):
        self.tools = {}  # original_name -> tool_data
        self.name_mapping = {}  # alias_name -> original_name
        self.ready = False
        self.call_results = {}  # To store Futures for tool call responses
        self.next_id = 1
        self.lock = asyncio.Lock()
        self._cached_available_tools = None  # Cache for get_available_tools

    def has_tool(self, name: str) -> bool:
        return name in self.tools or name in self.name_mapping

    def get_available_tools(self) -> list:
        # Check if the cache is valid
        if self._cached_available_tools is not None:
            cached_names = [
                tool.get("function", {}).get("name", "")
                for tool in self._cached_available_tools
            ]
            logger.bind(tag=TAG).debug(
                f"[tool_diag] device_mcp_cached_tools={cached_names}"
            )
            logger.bind(tag=TAG).info(
                f"[tool_diag] volume_tool_in_device_mcp_cache={VOLUME_TOOL_NAME in cached_names}"
            )
            return self._cached_available_tools

        # If cache is not valid, regenerate the list
        result = []
        for tool_name, tool_data in self.tools.items():
            function_def = {
                "name": tool_name,
                "description": tool_data["description"],
                "parameters": {
                    "type": tool_data["inputSchema"].get("type", "object"),
                    "properties": tool_data["inputSchema"].get("properties", {}),
                    "required": tool_data["inputSchema"].get("required", []),
                },
            }
            result.append({"type": "function", "function": function_def})

        tool_names = [tool.get("function", {}).get("name", "") for tool in result]
        logger.bind(tag=TAG).info(
            f"[tool_diag] device_mcp_available_tools={tool_names}"
        )
        logger.bind(tag=TAG).info(
            f"[tool_diag] volume_tool_in_device_mcp_available_tools={VOLUME_TOOL_NAME in tool_names}"
        )
        self._cached_available_tools = result  # Store the generated list in cache
        return result

    async def is_ready(self) -> bool:
        async with self.lock:
            return self.ready

    async def set_ready(self, status: bool):
        async with self.lock:
            self.ready = status

    async def add_tool(self, tool_data: dict):
        async with self.lock:
            original_name = tool_data["name"]
            sanitized_name = sanitize_tool_name(original_name)
            self.tools[original_name] = tool_data
            self.name_mapping[original_name] = original_name
            if sanitized_name != original_name:
                existing_original = self.name_mapping.get(sanitized_name)
                if existing_original and existing_original != original_name:
                    logger.bind(tag=TAG).warning(
                        f"[tool_diag] device_mcp_sanitized_alias_conflict alias={sanitized_name} "
                        f"existing={existing_original} new={original_name}"
                    )
                else:
                    self.name_mapping[sanitized_name] = original_name
            logger.bind(tag=TAG).info(
                f"[tool_diag] device_mcp_tool_registered raw={original_name} sanitized={sanitized_name}"
            )
            if original_name == VOLUME_TOOL_NAME:
                logger.bind(tag=TAG).info(
                    "[tool_diag] volume_tool_registered_in_device_mcp_client"
                )
            self._cached_available_tools = (
                None  # Invalidate the cache when a tool is added
            )

    async def get_next_id(self) -> int:
        async with self.lock:
            current_id = self.next_id
            self.next_id += 1
            return current_id

    async def register_call_result_future(self, id: int, future: Future):
        async with self.lock:
            self.call_results[id] = future

    async def resolve_call_result(self, id: int, result: any):
        async with self.lock:
            if id in self.call_results:
                future = self.call_results.pop(id)
                if not future.done():
                    future.set_result(result)

    async def reject_call_result(self, id: int, exception: Exception):
        async with self.lock:
            if id in self.call_results:
                future = self.call_results.pop(id)
                if not future.done():
                    future.set_exception(exception)

    async def cleanup_call_result(self, id: int):
        async with self.lock:
            if id in self.call_results:
                self.call_results.pop(id)
