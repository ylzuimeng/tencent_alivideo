"""Structured JSON validation service

This module provides JSON schema validation for template configuration fields.
Uses jsonschema library for validation with caching for performance.
"""

import json
import logging
from typing import Tuple, Dict, Any
from functools import lru_cache

logger = logging.getLogger(__name__)


class JSONValidator:
    """JSON schema validator with caching

    Validates JSON strings against predefined schemas and provides
    detailed error messages for debugging.
    """

    def __init__(self):
        """Initialize validator and load schemas"""
        self._schemas = {}
        self._load_schemas()

    def _load_schemas(self):
        """Load schema definitions from schemas package"""
        try:
            from schemas.timeline_schemas import SCHEMAS
            self._schemas = SCHEMAS.copy()
            logger.info(f"Loaded {len(self._schemas)} JSON schemas")
        except ImportError as e:
            logger.error(f"Failed to import schemas: {e}")
            raise

    @lru_cache(maxsize=128)
    def validate_json(
        self,
        json_str: str,
        schema_type: str
    ) -> Tuple[bool, str]:
        """
        Validate JSON string against schema

        Args:
            json_str: JSON string to validate
            schema_type: Type of schema ('timeline', 'output_media', 'text_overlay', 'editing_produce')

        Returns:
            Tuple of (is_valid, error_message)
            - is_valid: True if validation passes, False otherwise
            - error_message: Empty string if valid, error details if invalid
        """
        try:
            # Parse JSON
            data = json.loads(json_str)

            # Get schema
            schema = self._schemas.get(schema_type)
            if not schema:
                return False, f"Unknown schema type: {schema_type}. Available: {list(self._schemas.keys())}"

            # Validate against schema
            from jsonschema import validate, ValidationError
            validate(instance=data, schema=schema)

            return True, ""

        except json.JSONDecodeError as e:
            error_msg = f"JSON格式错误: {str(e)}"
            logger.debug(f"JSON decode error for {schema_type}: {error_msg}")
            return False, error_msg

        except ImportError:
            # jsonschema not installed, provide basic validation only
            logger.warning("jsonschema library not installed, skipping schema validation")
            return True, ""

        except ValidationError as e:
            # Format validation error for better readability
            error_path = ' -> '.join(str(p) for p in e.path) if e.path else 'root'
            error_msg = f"Schema验证失败: {e.message} (位置: {error_path})"
            logger.debug(f"Validation error for {schema_type}: {error_msg}")
            return False, error_msg

        except Exception as e:
            error_msg = f"验证异常: {str(e)}"
            logger.error(f"Unexpected validation error for {schema_type}: {error_msg}")
            return False, error_msg

    def validate_and_return_data(
        self,
        json_str: str,
        schema_type: str
    ) -> Tuple[bool, str, Any]:
        """
        Validate JSON and return parsed data if valid

        Args:
            json_str: JSON string to validate
            schema_type: Type of schema

        Returns:
            Tuple of (is_valid, error_message, parsed_data)
            - parsed_data: Python object if valid, None if invalid
        """
        is_valid, error_msg = self.validate_json(json_str, schema_type)

        if not is_valid:
            return False, error_msg, None

        try:
            data = json.loads(json_str)
            return True, "", data
        except json.JSONDecodeError as e:
            return False, f"JSON解析错误: {str(e)}", None

    def clear_cache(self):
        """Clear validation cache

        Call this if schemas are updated at runtime
        """
        self.validate_json.cache_clear()
        logger.debug("Validation cache cleared")

    def get_available_schemas(self) -> list[str]:
        """Get list of available schema types"""
        return list(self._schemas.keys())


# Global validator instance for convenient access
_json_validator_instance = None


def get_json_validator() -> JSONValidator:
    """
    Get global JSON validator instance (singleton pattern)

    Returns:
        JSONValidator instance
    """
    global _json_validator_instance
    if _json_validator_instance is None:
        _json_validator_instance = JSONValidator()
    return _json_validator_instance


# Convenience functions for quick validation
def validate_timeline_json(json_str: str) -> Tuple[bool, str]:
    """Validate timeline JSON"""
    validator = get_json_validator()
    return validator.validate_json(json_str, 'timeline')


def validate_output_media_config(json_str: str) -> Tuple[bool, str]:
    """Validate output media config JSON"""
    validator = get_json_validator()
    return validator.validate_json(json_str, 'output_media')


def validate_text_overlay_config(json_str: str) -> Tuple[bool, str]:
    """Validate text overlay config JSON"""
    validator = get_json_validator()
    return validator.validate_json(json_str, 'text_overlay')


def validate_editing_produce_config(json_str: str) -> Tuple[bool, str]:
    """Validate editing produce config JSON"""
    validator = get_json_validator()
    return validator.validate_json(json_str, 'editing_produce')
