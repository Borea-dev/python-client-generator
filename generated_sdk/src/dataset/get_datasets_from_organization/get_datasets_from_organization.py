# generated by borea

# if you want to edit this file, add it to ignores in borea.config.json, glob syntax

# TODO: not implemented

from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING
from ....models.models import *

if TYPE_CHECKING:
    from ...trieve_api import TrieveApi


class GetDatasetsFromOrganization:
    def __init__(self, parent: "TrieveApi"):
        self.parent = parent

    def get_datasets_from_organization(
        self,
        tr_organization: str,
        organization_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Any:
        """
        Auth'ed user or api key must have an admin or owner role for the specified dataset's organization.

        Args:
            tr_organization: The organization id to use for the request
            organization_id: id of the organization you want to retrieve datasets for
            limit: The number of records to return
            offset: The number of records to skip

        Returns:
            Response data
        """
        path = f"/api/dataset/organization/{organization_id}"
        params = {}
        headers = {}
        if tr_organization is not None:
            headers["TR-Organization"] = tr_organization
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        json_data = None

        response = self.parent._make_request(
            method="GET",
            path=path,
            params=params,
            headers=headers,
            json_data=json_data,
        )
        return response.json()
