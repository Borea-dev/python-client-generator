# generated by borea

# if you want to edit this file, add it to ignores in borea.config.json, glob syntax

# TODO: not implemented

from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING
from ....models.models import *

if TYPE_CHECKING:
    from ...trieve_api import TrieveApi


class GetAllTopicMessages:
    def __init__(self, parent: "TrieveApi"):
        self.parent = parent

    def get_all_topic_messages(
        self,
        tr_dataset: str,
        messages_topic_id: str,
    ) -> Any:
        """
        If the topic is a RAG topic then the response will include Chunks first on each message. The structure will look like `[chunks]||mesage`. See docs.trieve.ai for more information.

        Args:
            tr_dataset: The dataset id or tracking_id to use for the request. We assume you intend to use an id if the value is a valid uuid.
            messages_topic_id: The ID of the topic to get messages for.

        Returns:
            Response data
        """
        path = f"/api/messages/{messages_topic_id}"
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
