# generated by borea

# if you want to edit this file, add it to ignores in borea.config.json, glob syntax

# TODO: not implemented

from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING
from ....models.models import *

if TYPE_CHECKING:
    from ...oxide_region_api import OxideRegionAPI


class NetworkingAllowListView:
    def __init__(self, parent: "OxideRegionAPI"):
        self.parent = parent

    def networking_allow_list_view(
        self,
    ) -> Any:
        """


        Returns:
            Response data
        """
        path = f"/v1/system/networking/allow-list"
        params = None
        headers = None
        json_data = None

        response = self.parent._make_request(
            method="GET",
            path=path,
            params=params,
            headers=headers,
            json_data=json_data,
        )
        return response.json()
