"""JSON Schema definitions for template validation

This module defines JSON schemas for validating template configuration fields.
All schemas follow the JSON Schema draft 7 specification.
"""

from typing import Dict, Any


# Timeline JSON Schema
# Validates the structure of ICE Timeline JSON used in advanced templates
TIMELINE_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "required": ["VideoTracks"],
    "properties": {
        "VideoTracks": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "required": ["VideoTrackClips"],
                "properties": {
                    "VideoTrackClips": {
                        "type": "array",
                        "minItems": 1,
                        "items": {
                            "type": "object",
                            "required": ["MediaURL"],
                            "properties": {
                                "MediaURL": {
                                    "type": "string",
                                    "pattern": "^(https?://|\\$[a-zA-Z_]+)"  # HTTP URL or placeholder
                                },
                                "Duration": {
                                    "type": "number",
                                    "minimum": 0
                                },
                                "MainTrack": {
                                    "type": "boolean"
                                },
                                "Effects": {
                                    "type": "array"
                                },
                                "TimelineIn": {
                                    "type": "number",
                                    "minimum": 0
                                },
                                "TimelineOut": {
                                    "type": "number",
                                    "minimum": 0
                                }
                            }
                        }
                    }
                }
            }
        },
        "SubtitleTracks": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["SubtitleTrackClips"],
                "properties": {
                    "SubtitleTrackClips": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["Type"],
                            "properties": {
                                "Type": {
                                    "type": "string",
                                    "enum": ["Text", "Subtitle"]
                                },
                                "SubType": {
                                    "type": "string",
                                    "enum": ["srt", "ass"]
                                },
                                "Content": {"type": "string"},
                                "Text": {"type": "string"},  # Legacy field for compatibility
                                "FileURL": {"type": "string", "format": "uri"},
                                "X": {"type": "number"},
                                "Y": {"type": "number"},
                                "FontSize": {"type": "integer", "minimum": 8, "maximum": 5000},
                                "FontColor": {"type": "string"},
                                "FontColorOpacity": {"type": "number", "minimum": 0, "maximum": 1},
                                "FontFace": {
                                    "type": "object",
                                    "properties": {
                                        "Bold": {"type": "boolean"},
                                        "Italic": {"type": "boolean"},
                                        "Underline": {"type": "boolean"}
                                    }
                                },
                                "Spacing": {"type": "integer"},
                                "LineSpacing": {"type": "integer"},
                                "Angle": {"type": "number"},
                                "BorderStyle": {"type": "integer", "enum": [1, 3]},
                                "Outline": {"type": "integer", "minimum": 0},
                                "OutlineColour": {"type": "string"},
                                "Alignment": {
                                    "type": "string",
                                    "enum": ["TopLeft", "TopCenter", "TopRight",
                                           "CenterLeft", "CenterCenter", "CenterRight",
                                           "BottomLeft", "BottomCenter", "BottomRight"]
                                },
                                "TimelineIn": {"type": "number", "minimum": 0},
                                "TimelineOut": {"type": "number", "minimum": 0},
                                "ClipId": {"type": "string"},
                                "ReferenceClipId": {"type": "string"}
                            }
                        }
                    }
                }
            }
        },
        "AudioTracks": {
            "type": "array"
        }
    }
}


# Output Media Config Schema
# Validates video output configuration (resolution, format, etc.)
OUTPUT_MEDIA_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "Width": {
            "type": "integer",
            "minimum": 240,
            "maximum": 3840,
            "description": "Video width in pixels"
        },
        "Height": {
            "type": "integer",
            "minimum": 240,
            "maximum": 2160,
            "description": "Video height in pixels"
        },
        "Bitrate": {
            "type": "integer",
            "minimum": 100,
            "maximum": 50000,
            "description": "Video bitrate in kbps"
        },
        "Fps": {
            "type": "number",
            "minimum": 1,
            "maximum": 120,
            "description": "Frames per second"
        },
        "Format": {
            "type": "string",
            "enum": ["mp4", "mov", "flv", "mkv"],
            "description": "Output format"
        }
    }
}


# Text Overlay Config Schema
# Validates text overlay configuration array
TEXT_OVERLAY_SCHEMA: Dict[str, Any] = {
    "type": "array",
    "items": {
        "type": "object",
        "required": ["text", "x", "y"],
        "properties": {
            "text": {
                "type": "string",
                "minLength": 1,
                "maxLength": 500,
                "description": "Text content to display"
            },
            "x": {
                "type": "number",
                "description": "X coordinate (percentage or pixels)"
            },
            "y": {
                "type": "number",
                "description": "Y coordinate (percentage or pixels)"
            },
            "font_size": {
                "type": "integer",
                "minimum": 8,
                "maximum": 200,
                "description": "Font size in pixels"
            },
            "font_color": {
                "type": "string",
                "pattern": "^#[0-9A-Fa-f]{6}$",
                "description": "Font color in hex format"
            },
            "duration": {
                "type": "number",
                "minimum": 0,
                "description": "Display duration in seconds"
            },
            "timeline_in": {
                "type": "number",
                "minimum": 0,
                "description": "Start time in seconds"
            },
            "timeline_out": {
                "type": "number",
                "minimum": 0,
                "description": "End time in seconds"
            },
            "alignment": {
                "type": "string",
                "enum": ["left", "center", "right", "top-left", "top-center", "top-right", "bottom-left", "bottom-center", "bottom-right"],
                "description": "Text alignment"
            }
        }
    }
}


# Editing Produce Config Schema
# Validates production configuration (thumbnail,封面, etc.)
EDITING_PRODUCE_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "CoverUrl": {
            "type": "string",
            "pattern": "^https?://",
            "description": "Cover image URL"
        },
        "CoverMode": {
            "type": "string",
            "enum": ["crop", "pad", "blur"],
            "description": "Cover image mode"
        },
        "Title": {
            "type": "string",
            "maxLength": 200,
            "description": "Video title"
        },
        "Description": {
            "type": "string",
            "maxLength": 1000,
            "description": "Video description"
        },
        "Tags": {
            "type": "array",
            "items": {
                "type": "string",
                "maxLength": 50
            },
            "maxItems": 20,
            "description": "Video tags"
        }
    }
}


# Schema registry for easy access
SCHEMAS: Dict[str, Dict[str, Any]] = {
    'timeline': TIMELINE_SCHEMA,
    'output_media': OUTPUT_MEDIA_SCHEMA,
    'text_overlay': TEXT_OVERLAY_SCHEMA,
    'editing_produce': EDITING_PRODUCE_SCHEMA,
}


def get_schema(schema_type: str) -> Dict[str, Any]:
    """
    Get schema by type

    Args:
        schema_type: Type of schema ('timeline', 'output_media', 'text_overlay', 'editing_produce')

    Returns:
        Schema dictionary

    Raises:
        ValueError: If schema type is unknown
    """
    schema = SCHEMAS.get(schema_type)
    if not schema:
        raise ValueError(f"Unknown schema type: {schema_type}. Available types: {list(SCHEMAS.keys())}")
    return schema
