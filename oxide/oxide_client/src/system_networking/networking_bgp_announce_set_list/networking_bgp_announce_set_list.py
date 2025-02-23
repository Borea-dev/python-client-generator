# generated by borea

# if you want to edit this file, add it to ignores in borea.config.json, glob syntax

# TODO: not implemented

from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING
from ....models.models import *

if TYPE_CHECKING:
    from ...oxide_region_api import OxideRegionAPI


class NetworkingBgpAnnounceSetList:
    def __init__(self, parent: "OxideRegionAPI"):
        self.parent = parent

    def networking_bgp_announce_set_list(
        self,
        limit: Optional[int] = None,
        page_token: Optional[str] = None,
        sort_by: Optional[NameOrIdSortMode] = None,
    ) -> Any:
        """


        Args:
            limit: Maximum number of items returned by a single call
            page_token: Token returned by previous call to retrieve the subsequent page
            sort_by:

        Returns:
            Response data
        """
        path = f"/v1/system/networking/bgp-announce-set"
        params = {}
        headers = {}
        if limit is not None:
            params["limit"] = limit
        if page_token is not None:
            params["page_token"] = page_token
        if sort_by is not None:
            params["sort_by"] = sort_by
        json_data = None

        response = self.parent._make_request(
            method="GET",
            path=path,
            params=params,
            headers=headers,
            json_data=json_data,
        )
        return response.json()
