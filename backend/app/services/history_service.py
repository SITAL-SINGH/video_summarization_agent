from backend.app.db.database import (
    connect,
)

from backend.app.schemas.response import (
    HistoryListItem,
    SummaryResponse,
)


class HistoryService:

    def save(
        self,
        response: SummaryResponse,
    ) -> int:

        with connect() as conn:

            cursor = conn.execute(
                """
                INSERT INTO summaries (
                    source_type,
                    source_name,
                    title,
                    response_json,
                    generated_at
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    response.source_type,

                    response.source_name,

                    response.analysis.title,

                    response
                    .model_dump_json(),

                    response
                    .generated_at
                    .isoformat(),
                ),
            )

            row_id = int(
                cursor.lastrowid
            )

            response.id = row_id

            conn.execute(
                """
                UPDATE summaries
                SET response_json = ?
                WHERE id = ?
                """,
                (
                    response
                    .model_dump_json(),

                    row_id,
                ),
            )

            conn.commit()

            return row_id

    def list(
        self,
        limit: int = 20,
    ) -> list[
        HistoryListItem
    ]:

        limit = max(
            1,
            min(
                limit,
                100,
            ),
        )

        with connect() as conn:

            rows = conn.execute(
                """
                SELECT
                    id,
                    source_type,
                    source_name,
                    title,
                    generated_at
                FROM summaries
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        return [
            HistoryListItem(
                **dict(row)
            )

            for row
            in rows
        ]

    def get(
        self,
        summary_id: int,
    ) -> (
        SummaryResponse
        | None
    ):

        with connect() as conn:

            row = conn.execute(
                """
                SELECT response_json
                FROM summaries
                WHERE id = ?
                """,
                (summary_id,),
            ).fetchone()

        if row is None:
            return None

        return (
            SummaryResponse
            .model_validate_json(
                row[
                    "response_json"
                ]
            )
        )