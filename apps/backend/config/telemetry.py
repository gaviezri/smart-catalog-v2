"""OpenTelemetry SDK initialisation.

Current exporter: console.
Swap via env var ``OTEL_EXPORTER`` (``console`` | ``otlp``).
"""
from __future__ import annotations

import os

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter


def init_telemetry() -> None:
    """Bootstrap the OTel tracer provider."""
    resource: Resource = Resource.create({"service.name": "smart-catalog-backend"})
    provider: TracerProvider = TracerProvider(resource=resource)

    exporter_type: str = os.getenv("OTEL_EXPORTER", "console")

    if exporter_type == "otlp":
        # Lazy import so we don't require the package when using console only.
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (  # type: ignore[import-untyped]
            OTLPSpanExporter,
        )

        provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
    else:
        provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

    trace.set_tracer_provider(provider)
