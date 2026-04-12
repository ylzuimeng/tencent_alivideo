"""JSON Schema definitions for template validation

This package provides JSON schemas for validating template configuration fields.
"""

from .timeline_schemas import (
    TIMELINE_SCHEMA,
    OUTPUT_MEDIA_SCHEMA,
    TEXT_OVERLAY_SCHEMA,
    EDITING_PRODUCE_SCHEMA,
    SCHEMAS,
    get_schema
)

__all__ = [
    'TIMELINE_SCHEMA',
    'OUTPUT_MEDIA_SCHEMA',
    'TEXT_OVERLAY_SCHEMA',
    'EDITING_PRODUCE_SCHEMA',
    'SCHEMAS',
    'get_schema'
]
