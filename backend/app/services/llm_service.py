import json
from typing import (
    Literal,
    TypeVar,
)

from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
)

from langchain_openrouter import (
    ChatOpenRouter,
)

from pydantic import BaseModel

from backend.app.core.config import (
    settings,
)

from backend.app.services.model_catalog import (
    ModelCatalogService,
)

from backend.app.utils.text import (
    message_to_text,
    parse_json_model,
)


T = TypeVar(
    "T",
    bound=BaseModel,
)

Role = Literal[
    "video",
    "reasoning",
    "summary",
]


class LLMService:

    def __init__(
        self,
        catalog: (
            ModelCatalogService
            | None
        ) = None,
    ) -> None:

        self.catalog = (
            catalog
            or ModelCatalogService()
        )

    def models_for(
        self,
        role: Role,
    ) -> list[str]:

        if role == "video":
            return (
                settings
                .video_model_list
            )

        if role == "reasoning":
            return (
                settings
                .reasoning_model_list
            )

        return (
            settings
            .summary_model_list
        )

    def chat_model(
        self,
        model_id: str,
        temperature: (
            float | None
        ) = None,
    ) -> ChatOpenRouter:

        return ChatOpenRouter(
            model=model_id,

            api_key=(
                settings
                .require_openrouter_key()
            ),

            temperature=(
                settings
                .model_temperature
                if temperature is None
                else temperature
            ),

            max_retries=(
                settings
                .model_max_retries
            ),
        )

    def invoke_text_model(
        self,
        model_id: str,
        messages: list[
            BaseMessage
        ],
    ) -> str:

        response = (
            self.chat_model(
                model_id
            )
            .invoke(
                messages
            )
        )

        return (
            message_to_text(
                response
            )
            .strip()
        )

    def invoke_text(
        self,
        role: Role,
        messages: list[
            BaseMessage
        ],
    ) -> tuple[
        str,
        str,
    ]:

        errors: list[str] = []

        for model_id in (
            self.models_for(
                role
            )
        ):

            try:
                return (
                    self.invoke_text_model(
                        model_id,
                        messages,
                    ),
                    model_id,
                )

            except Exception as exc:

                errors.append(
                    f"{model_id}: {exc}"
                )

        raise RuntimeError(
            f"All {role} models failed. "
            + " | ".join(
                errors
            )
        )

    def invoke_structured_model(
        self,
        model_id: str,
        messages: list[
            BaseMessage
        ],
        schema: type[T],
    ) -> T:

        caps = self.catalog.get(
            model_id
        )

        if (
            caps
            .supports_native_structured_output
        ):

            try:
                structured = (
                    self.chat_model(
                        model_id
                    )
                    .with_structured_output(
                        schema,
                        method="json_schema",
                        strict=True,
                    )
                )

                result = (
                    structured.invoke(
                        messages
                    )
                )

                if isinstance(
                    result,
                    schema,
                ):
                    return result

                return (
                    schema
                    .model_validate(
                        result
                    )
                )

            except Exception:
                pass

        schema_json = json.dumps(
            schema.model_json_schema(),
            ensure_ascii=False,
        )

        portable_messages = (
            list(messages)
            + [
                HumanMessage(
                    content=(
                        "Return ONLY one valid "
                        "JSON object matching "
                        "this JSON Schema. "
                        "No markdown fences and "
                        "no commentary.\n\n"
                        "JSON Schema:\n"
                        f"{schema_json}"
                    )
                )
            ]
        )

        text = (
            self.invoke_text_model(
                model_id,
                portable_messages,
            )
        )

        return parse_json_model(
            text,
            schema,
        )

    def invoke_structured(
        self,
        role: Role,
        messages: list[
            BaseMessage
        ],
        schema: type[T],
    ) -> tuple[
        T,
        str,
    ]:

        errors: list[str] = []

        for model_id in (
            self.models_for(
                role
            )
        ):

            try:
                return (
                    self.invoke_structured_model(
                        model_id,
                        messages,
                        schema,
                    ),
                    model_id,
                )

            except Exception as exc:

                errors.append(
                    f"{model_id}: {exc}"
                )

        raise RuntimeError(
            f"All {role} models failed. "
            + " | ".join(
                errors
            )
        )