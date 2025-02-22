# generated by borea

# if you want to edit this file, add it to ignores in borea.config.json, glob syntax

# TODO: not implemented

from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING
from ....models.models import *

if TYPE_CHECKING:
    from ...trieve_api import TrieveApi


class RemoveChunkFromGroup:
    def __init__(self, parent: "TrieveApi"):
        self.parent = parent

    def remove_chunk_from_group(
        self,
        tr_dataset: str,
        group_id: str,
        chunk_id: Optional[str] = None,
    ) -> Any:
        """
        Route to remove a chunk from a group. Auth'ed user or api key must be an admin or owner of the dataset's organization to remove a chunk from a group.

        Args:
            tr_dataset: The dataset id or tracking_id to use for the request. We assume you intend to use an id if the value is a valid uuid.
            group_id: Id of the group you want to remove the chunk from.
            chunk_id: Id of the chunk you want to remove from the group

        Returns:
            Response data
        """
        path = f"/api/chunk_group/chunk/{group_id}"
        params = {}
        headers = {}
        if tr_dataset is not None:
            headers["TR-Dataset"] = tr_dataset
        if chunk_id is not None:
            params["chunk_id"] = chunk_id
        json_data = {
            "chunk_id": chunk_id if chunk_id is not None else None,
        }
        json_data = {k: v for k, v in json_data.items() if v is not None}

        response = self.parent._make_request(
            method="DELETE",
            path=path,
            params=params,
            headers=headers,
            json_data=json_data,
        )
        return response.json()
