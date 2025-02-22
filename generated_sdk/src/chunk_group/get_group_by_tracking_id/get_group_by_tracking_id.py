# generated by borea

# if you want to edit this file, add it to ignores in borea.config.json, glob syntax

# TODO: not implemented

from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING
from ....models.models import *

if TYPE_CHECKING:
    from ...trieve_api import TrieveApi


class GetGroupByTrackingId:
    def __init__(self, parent: "TrieveApi"):
        self.parent = parent

    def get_group_by_tracking_id(
        self,
        tr_dataset: str,
        tracking_id: str,
    ) -> Any:
        """
                Fetch the group with the given tracking id.
        get_group_by_tracking_id

                Args:
                    tr_dataset: The dataset id or tracking_id to use for the request. We assume you intend to use an id if the value is a valid uuid.
                    tracking_id: The tracking id of the group to fetch.

                Returns:
                    Response data
        """
        path = f"/api/chunk_group/tracking_id/{tracking_id}"
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
