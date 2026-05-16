from __future__ import annotations

from abc import ABC, abstractmethod

from app.modules.ai.schemas import AIGenerationRequest, AIGenerationResponse


class AIProvider(ABC):
    name: str

    @abstractmethod
    async def generate(self, request: AIGenerationRequest) -> AIGenerationResponse:
        raise NotImplementedError
