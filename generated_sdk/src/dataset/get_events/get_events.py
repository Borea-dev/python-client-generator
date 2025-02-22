# generated by borea

# if you want to edit this file, add it to ignores in borea.config.json, glob syntax

# TODO: not implemented

from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING
from ....models.models import *

if TYPE_CHECKING:
    from ...trieve_api import TrieveApi


class GetEvents:
    def __init__(self, parent: "TrieveApi"):
        self.parent = parent

    def get_events(
        self,
        tr_dataset: str,
        event_types: Optional[List[EventTypeRequest]] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> Any:
        """
        Get events for the dataset specified by the TR-Dataset header.

        Args:
            tr_dataset: The dataset id or tracking_id to use for the request. We assume you intend to use an id if the value is a valid uuid.
            event_types: The types of events to get. Leave undefined to get all events.
            page: The page number to get. Default is 1.
            page_size: The number of items per page. Default is 10.

        Returns:
            Response data
        """
        path = f"/api/dataset/events"
        params = {}
        headers = {}
        if tr_dataset is not None:
            headers["TR-Dataset"] = tr_dataset
        json_data = {
            "event_types": event_types if event_types is not None else None,
            "page": page if page is not None else None,
            "page_size": page_size if page_size is not None else None,
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
