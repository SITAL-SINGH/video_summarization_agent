from fastapi import (
    APIRouter,
    HTTPException,
)

from backend.app.schemas.response import (
    HistoryListItem,
    SummaryResponse,
)

from backend.app.services.history_service import (
    HistoryService,
)


router = APIRouter(
    prefix="/api/v1/history",

    tags=[
        "history"
    ],
)


history_service = (
    HistoryService()
)


@router.get(
    "",

    response_model=list[
        HistoryListItem
    ],
)
def list_history(
    limit: int = 20,
) -> list[
    HistoryListItem
]:

    return (
        history_service
        .list(
            limit
        )
    )


@router.get(
    "/{summary_id}",

    response_model=(
        SummaryResponse
    ),
)
def get_history_item(
    summary_id: int,
) -> SummaryResponse:

    result = (
        history_service
        .get(
            summary_id
        )
    )

    if result is None:
        raise HTTPException(
            status_code=404,

            detail=(
                "Summary not found."
            ),
        )

    return result