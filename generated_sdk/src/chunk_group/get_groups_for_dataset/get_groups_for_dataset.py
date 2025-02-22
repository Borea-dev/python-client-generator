# generated by borea

# if you want to edit this file, add it to ignores in borea.config.json, glob syntax

# TODO: not implemented

from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING
from ....models.models import *

if TYPE_CHECKING:
    from ...trieve_api import TrieveApi


class GetGroupsForDataset:
    def __init__(self, parent: "TrieveApi"):
        self.parent = parent

    def get_groups_for_dataset(
        self,
        tr_dataset: str,
        dataset_id: str,
        page: int,
    ) -> Any:
        """
        Fetch the groups which belong to a dataset specified by its id.

        Args:
            tr_dataset: The dataset id or tracking_id to use for the request. We assume you intend to use an id if the value is a valid uuid.
            dataset_id: The id of the dataset to fetch groups for.
            page: The page of groups to fetch. Page is 1-indexed.

        Returns:
            Response data
        """
        path = f"/api/dataset/groups/{dataset_id}/{page}"
        params = {}
        headers = {}
        if tr_dataset is not None:
            headers["TR-Dataset"] = tr_dataset
        json_data = None

        response = self.parent._make_request(
            method="GET",
            path=path,
            params=params,
            headers=headers,
            json_data=json_data,
        )
        return response.json()
