from pydantic import BaseModel

from backend.app.utils.text import (
    parse_json_model,
)


class Example(BaseModel):
    value: int


def test_parse_json_model_from_fence(
) -> None:

    parsed = parse_json_model(
        """
        ```json
        {"value": 7}
        ```
        """,

        Example,
    )

    assert (
        parsed.value
        == 7
    )