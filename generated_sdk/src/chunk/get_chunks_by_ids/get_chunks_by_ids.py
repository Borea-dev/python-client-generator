# generated by borea

# if you want to edit this file, add it to ignores in borea.config.json, glob syntax

# TODO: not implemented

from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING
from ....models.models import *

if TYPE_CHECKING:
    from ...trieve_api import TrieveApi


class GetChunksByIds:
    def __init__(self, parent: "TrieveApi"):
        self.parent = parent

    def get_chunks_by_ids(
        self,
        tr_dataset: str,
        ids: List[str],
        x_api_version: Optional[APIVersion] = None,
    ) -> Any:
        """
        Get multiple chunks by multiple ids.

        Args:
            tr_dataset: The dataset id or tracking_id to use for the request. We assume you intend to use an id if the value is a valid uuid.
            ids: No description provided
            x_api_version: The API version to use for this request. Defaults to V2 for orgs created after July 12, 2024 and V1 otherwise.

        Returns:
            Response data
        """
        path = f"/api/chunks"
        params = {}
        headers = {}
        if tr_dataset is not None:
            headers["TR-Dataset"] = tr_dataset
        if x_api_version is not None:
            headers["X-API-Version"] = x_api_version
        json_data = {
            "ids": ids if ids is not None else None,
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
