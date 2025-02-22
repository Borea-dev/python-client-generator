# generated by borea

# if you want to edit this file, add it to ignores in borea.config.json, glob syntax

# TODO: not implemented

from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING
from ....models.models import *

if TYPE_CHECKING:
    from ...trieve_api import TrieveApi


class CreateEtlJob:
    def __init__(self, parent: "TrieveApi"):
        self.parent = parent

    def create_etl_job(
        self,
        tr_dataset: str,
        prompt: str,
        include_images: Optional[bool] = None,
        model: Optional[str] = None,
        tag_enum: Optional[List[str]] = None,
    ) -> Any:
        """
        This endpoint is used to create a new ETL job for a dataset.

        Args:
            tr_dataset: The dataset id to use for the request
            prompt: No description provided
            include_images: No description provided
            model: No description provided
            tag_enum: No description provided

        Returns:
            Response data
        """
        path = f"/api/etl/create_job"
        params = {}
        headers = {}
        if tr_dataset is not None:
            headers["TR-Dataset"] = tr_dataset
        json_data = {
            "include_images": include_images if include_images is not None else None,
            "model": model if model is not None else None,
            "prompt": prompt if prompt is not None else None,
            "tag_enum": tag_enum if tag_enum is not None else None,
        }
        json_data = {k: v for k, v in json_data.items() if v is not None}

        response = self.parent._make_request(
            method="POST",
            path=path,
            params=params,
            headers=headers,
            json_data=json_data,
        )
        return response.json()
