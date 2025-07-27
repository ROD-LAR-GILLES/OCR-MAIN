"""
Dependencias de la API.
"""

from .container import (
    get_system_config,
    get_document_processor,
    get_markdown_generator,
    SystemConfigDep,
    DocumentProcessorDep,
    MarkdownGeneratorDep,
    DefaultSystemConfig,
    MockDocumentProcessor,
    MockMarkdownGenerator
)

__all__ = [
    "get_system_config",
    "get_document_processor", 
    "get_markdown_generator",
    "SystemConfigDep",
    "DocumentProcessorDep",
    "MarkdownGeneratorDep",
    "DefaultSystemConfig",
    "MockDocumentProcessor",
    "MockMarkdownGenerator"
]