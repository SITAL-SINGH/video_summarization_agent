from fastapi import (
    APIRouter,
)

from backend.app.core.config import (
    settings,
)

from backend.app.services.model_catalog import (
    ModelCatalogService,
)


router = APIRouter(
    prefix="/api/v1",

    tags=[
        "models"
    ],
)


catalog = (
    ModelCatalogService()
)


@router.get(
    "/models/configured"
)
def configured_models(
) -> dict:

    roles = {
        "video":
            settings
            .video_model_list,

        "reasoning":
            settings
            .reasoning_model_list,

        "summary":
            settings
            .summary_model_list,
    }

    result: dict[
        str,
        list[dict],
    ] = {}

    for (
        role,
        model_ids,
    ) in roles.items():

        result[role] = []

        for model_id in model_ids:

            try:
                caps = (
                    catalog.get(
                        model_id
                    )
                )

                result[
                    role
                ].append(
                    {
                        "id":
                            model_id,

                        "input_modalities":
                            sorted(
                                caps
                                .input_modalities
                            ),

                        "output_modalities":
                            sorted(
                                caps
                                .output_modalities
                            ),

                        "structured_output":
                            caps
                            .supports_native_structured_output,

                        "context_length":
                            caps
                            .context_length,
                    }
                )

            except Exception as exc:

                result[
                    role
                ].append(
                    {
                        "id":
                            model_id,

                        "error":
                            str(exc),
                    }
                )

    return result