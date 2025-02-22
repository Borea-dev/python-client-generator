# generated by borea

# if you want to edit this file, add it to ignores in borea.config.json, glob syntax

# TODO: not implemented

from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING
from ....models.models import *

if TYPE_CHECKING:
    from ...trieve_api import TrieveApi


class GetSuggestedQueries:
    def __init__(self, parent: "TrieveApi"):
        self.parent = parent

    def get_suggested_queries(
        self,
        tr_dataset: str,
        context: Optional[str] = None,
        filters: Optional[ChunkFilter] = None,
        query: Optional[str] = None,
        search_type: Optional[SearchMethod] = None,
        suggestion_type: Optional[SuggestType] = None,
        suggestions_to_create: Optional[int] = None,
    ) -> Any:
        """
        This endpoint will generate 3 suggested queries based off a hybrid search using RAG with the query provided in the request body and return them as a JSON object.

        Args:
            tr_dataset: The dataset id or tracking_id to use for the request. We assume you intend to use an id if the value is a valid uuid.
            context: Context is the context of the query. This can be any string under 15 words and 200 characters. The context will be used to generate the suggested queries. Defaults to None.
            filters: ChunkFilter is a JSON object which can be used to filter chunks. This is useful for when you want to filter chunks by arbitrary metadata. Unlike with tag filtering, there is a performance hit for filtering on metadata.
            query: The query to base the generated suggested queries off of using RAG. A hybrid search for 10 chunks from your dataset using this query will be performed and the context of the chunks will be used to generate the suggested queries.
            search_type: No description provided
            suggestion_type: No description provided
            suggestions_to_create: The number of suggested queries to create, defaults to 10

        Returns:
            Response data
        """
        path = f"/api/chunk/suggestions"
        params = {}
        headers = {}
        if tr_dataset is not None:
            headers["TR-Dataset"] = tr_dataset
        json_data = {
            "context": context if context is not None else None,
            "filters": filters if filters is not None else None,
            "query": query if query is not None else None,
            "search_type": search_type if search_type is not None else None,
            "suggestion_type": suggestion_type if suggestion_type is not None else None,
            "suggestions_to_create": (
                suggestions_to_create if suggestions_to_create is not None else None
            ),
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
