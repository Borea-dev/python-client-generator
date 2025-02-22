# generated by borea

# if you want to edit this file, add it to ignores in borea.config.json, glob syntax

# TODO: not implemented

from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING
from ....models.models import *

if TYPE_CHECKING:
    from ...trieve_api import TrieveApi


class DeleteFileHandler:
    def __init__(self, parent: "TrieveApi"):
        self.parent = parent

    def delete_file_handler(
        self,
        tr_dataset: str,
        file_id: str,
        delete_chunks: bool,
    ) -> Any:
        """
        Delete a file from S3 attached to the server based on its id. This will disassociate chunks from the file, but only delete them all together if you specify delete_chunks to be true. Auth'ed user or api key must have an admin or owner role for the specified dataset's organization.

        Args:
            tr_dataset: The dataset id or tracking_id to use for the request. We assume you intend to use an id if the value is a valid uuid.
            file_id: The id of the file to delete
            delete_chunks: Delete the chunks within the group

        Returns:
            Response data
        """
        path = f"/api/file/{file_id}"
        params = {}
        headers = {}
        if tr_dataset is not None:
            headers["TR-Dataset"] = tr_dataset
        if delete_chunks is not None:
            params["delete_chunks"] = delete_chunks
        json_data = None

        response = self.parent._make_request(
            method="DELETE",
            path=path,
            params=params,
            headers=headers,
            json_data=json_data,
        )
        return response.json()
