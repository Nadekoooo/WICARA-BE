from __future__ import annotations


class AIError(Exception):
    """Base exception for AI wrapper failures."""


class AIConfigurationError(AIError):
    """Raised when required AI configuration is missing or invalid."""


class AIInputError(AIError, ValueError):
    """Raised when an AI request payload is invalid."""


class AIProviderError(AIError):
    """Raised when a provider request fails or returns an unusable response."""


class AIProviderNotFoundError(AIError, LookupError):
    """Raised when a requested provider has not been registered."""
