# generated by borea

# if you want to edit this file, add it to ignores in borea.config.json, glob syntax

# TODO: not implemented

from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING
from ....models.models import *

if TYPE_CHECKING:
    from ...trieve_api import TrieveApi


class CreateMessage:
    def __init__(self, parent: "TrieveApi"):
        self.parent = parent

    def create_message(
        self,
        tr_dataset: str,
        topic_id: str,
        audio_input: Optional[str] = None,
        concat_user_messages_query: Optional[bool] = None,
        context_options: Optional[ContextOptions] = None,
        filters: Optional[ChunkFilter] = None,
        highlight_options: Optional[HighlightOptions] = None,
        image_urls: Optional[List[str]] = None,
        llm_options: Optional[LLMOptions] = None,
        new_message_content: Optional[str] = None,
        no_result_message: Optional[str] = None,
        only_include_docs_used: Optional[bool] = None,
        page_size: Optional[int] = None,
        score_threshold: Optional[float] = None,
        search_query: Optional[str] = None,
        search_type: Optional[SearchMethod] = None,
        sort_options: Optional[SortOptions] = None,
        use_group_search: Optional[bool] = None,
        user_id: Optional[str] = None,
    ) -> Any:
        """
        Create message. Messages are attached to topics in order to coordinate memory of gen-AI chat sessions.Auth'ed user or api key must have an admin or owner role for the specified dataset's organization.

        Args:
            tr_dataset: The dataset id or tracking_id to use for the request. We assume you intend to use an id if the value is a valid uuid.
            topic_id: The ID of the topic to attach the message to.
            audio_input: The base64 encoded audio input of the user message to attach to the topic and then generate an assistant message in response to.
            concat_user_messages_query: If concat user messages query is set to true, all of the user messages in the topic will be concatenated together and used as the search query. If not specified, this defaults to false. Default is false.
            context_options: Context options to use for the completion. If not specified, all options will default to false.
            filters: ChunkFilter is a JSON object which can be used to filter chunks. This is useful for when you want to filter chunks by arbitrary metadata. Unlike with tag filtering, there is a performance hit for filtering on metadata.
            highlight_options: Highlight Options lets you specify different methods to highlight the chunks in the result set. If not specified, this defaults to the score of the chunks.
            image_urls: The URL of the image(s) to attach to the message.
            llm_options: LLM options to use for the completion. If not specified, this defaults to the dataset's LLM options.
            new_message_content: The content of the user message to attach to the topic and then generate an assistant message in response to.
            no_result_message: No result message for when there are no chunks found above the score threshold.
            only_include_docs_used: Only include docs used in the completion. If not specified, this defaults to false.
            page_size: Page size is the number of chunks to fetch during RAG. If 0, then no search will be performed. If specified, this will override the N retrievals to include in the dataset configuration. Default is None.
            score_threshold: Set score_threshold to a float to filter out chunks with a score below the threshold. This threshold applies before weight and bias modifications. If not specified, this defaults to 0.0.
            search_query: Query is the search query. This can be any string. The search_query will be used to create a dense embedding vector and/or sparse vector which will be used to find the result set. If not specified, will default to the last user message or HyDE if HyDE is enabled in the dataset configuration. Default is None.
            search_type: No description provided
            sort_options: Sort Options lets you specify different methods to rerank the chunks in the result set. If not specified, this defaults to the score of the chunks.
            use_group_search: If use_group_search is set to true, the search will be conducted using the `search_over_groups` api. If not specified, this defaults to false.
            user_id: The user_id is the id of the user who is making the request. This is used to track user interactions with the RAG results.

        Returns:
            Response data
        """
        path = f"/api/message"
        params = {}
        headers = {}
        if tr_dataset is not None:
            headers["TR-Dataset"] = tr_dataset
        json_data = {
            "audio_input": audio_input if audio_input is not None else None,
            "concat_user_messages_query": (
                concat_user_messages_query
                if concat_user_messages_query is not None
                else None
            ),
            "context_options": context_options if context_options is not None else None,
            "filters": filters if filters is not None else None,
            "highlight_options": (
                highlight_options if highlight_options is not None else None
            ),
            "image_urls": image_urls if image_urls is not None else None,
            "llm_options": llm_options if llm_options is not None else None,
            "new_message_content": (
                new_message_content if new_message_content is not None else None
            ),
            "no_result_message": (
                no_result_message if no_result_message is not None else None
            ),
            "only_include_docs_used": (
                only_include_docs_used if only_include_docs_used is not None else None
            ),
            "page_size": page_size if page_size is not None else None,
            "score_threshold": score_threshold if score_threshold is not None else None,
            "search_query": search_query if search_query is not None else None,
            "search_type": search_type if search_type is not None else None,
            "sort_options": sort_options if sort_options is not None else None,
            "topic_id": topic_id if topic_id is not None else None,
            "use_group_search": (
                use_group_search if use_group_search is not None else None
            ),
            "user_id": user_id if user_id is not None else None,
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
