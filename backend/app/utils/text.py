import json
import re
from typing import Any, TypeVar

from pydantic import BaseModel


T = TypeVar(
    "T",
    bound=BaseModel,
)


def message_to_text(
    message: Any,
) -> str:

    content = getattr(
        message,
        "content",
        message,
    )

    if isinstance(
        content,
        str,
    ):
        return content

    if isinstance(
        content,
        list,
    ):
        parts: list[str] = []

        for item in content:

            if isinstance(
                item,
                str,
            ):
                parts.append(
                    item
                )

            elif isinstance(
                item,
                dict,
            ):
                text = (
                    item.get("text")
                    or item.get(
                        "content"
                    )
                )

                if text:
                    parts.append(
                        str(text)
                    )

        return "\n".join(
            parts
        )

    return str(
        content or ""
    )


def parse_json_model(
    text: str,
    schema: type[T],
) -> T:

    cleaned = text.strip()

    cleaned = re.sub(
        r"^```(?:json)?\s*",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )

    cleaned = re.sub(
        r"\s*```$",
        "",
        cleaned,
    )

    try:
        return (
            schema
            .model_validate_json(
                cleaned
            )
        )

    except Exception:
        pass

    start = cleaned.find(
        "{"
    )

    end = cleaned.rfind(
        "}"
    )

    if (
        start == -1
        or end == -1
        or end <= start
    ):
        raise ValueError(
            "Model response did not "
            "contain a JSON object."
        )

    candidate = cleaned[
        start:end + 1
    ]

    try:
        payload = json.loads(
            candidate
        )

    except json.JSONDecodeError as exc:
        raise ValueError(
            "Could not parse "
            f"model JSON: {exc}"
        ) from exc

    return schema.model_validate(
        payload
    )