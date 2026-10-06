import time
from dataclasses import dataclass
from typing import Any

import requests

from backend.app.core.config import (
    settings,
)


@dataclass(
    frozen=True,
)
class ModelCapabilities:
    model_id: str

    input_modalities: frozenset[
        str
    ]

    output_modalities: frozenset[
        str
    ]

    supported_parameters: frozenset[
        str
    ]

    context_length: (
        int | None
    ) = None

    @property
    def supports_native_structured_output(
        self,
    ) -> bool:

        return bool(
            {
                "response_format",
                "structured_outputs",
            }
            & self.supported_parameters
        )


class ModelCatalogService:

    def __init__(
        self,
        ttl_seconds: int = 900,
    ) -> None:

        self.ttl_seconds = (
            ttl_seconds
        )

        self._loaded_at = 0.0

        self._models: dict[
            str,
            dict[str, Any],
        ] = {}

    def _load(
        self,
    ) -> None:

        if (
            self._models
            and (
                time.monotonic()
                - self._loaded_at
            )
            < self.ttl_seconds
        ):
            return

        headers = {
            "Authorization":
                "Bearer "
                + settings
                .require_openrouter_key()
        }

        response = requests.get(
            (
                "https://openrouter.ai/"
                "api/v1/models"
            ),
            headers=headers,
            timeout=20,
        )

        response.raise_for_status()

        data = (
            response
            .json()
            .get(
                "data",
                [],
            )
        )

        self._models = {
            item.get("id", ""):
                item

            for item in data

            if item.get("id")
        }

        self._loaded_at = (
            time.monotonic()
        )

    def get(
        self,
        model_id: str,
    ) -> ModelCapabilities:

        self._load()

        item = self._models.get(
            model_id
        )

        if item is None:

            return ModelCapabilities(
                model_id=model_id,

                input_modalities=(
                    frozenset(
                        {"text"}
                    )
                ),

                output_modalities=(
                    frozenset(
                        {"text"}
                    )
                ),

                supported_parameters=(
                    frozenset()
                ),

                context_length=None,
            )

        architecture = (
            item.get(
                "architecture"
            )
            or {}
        )

        supported = (
            item.get(
                "supported_parameters"
            )
            or []
        )

        if isinstance(
            supported,
            dict,
        ):
            supported = list(
                supported.keys()
            )

        return ModelCapabilities(
            model_id=model_id,

            input_modalities=frozenset(
                architecture.get(
                    "input_modalities"
                )
                or ["text"]
            ),

            output_modalities=frozenset(
                architecture.get(
                    "output_modalities"
                )
                or ["text"]
            ),

            supported_parameters=frozenset(
                str(x)
                for x
                in supported
            ),

            context_length=item.get(
                "context_length"
            ),
        )