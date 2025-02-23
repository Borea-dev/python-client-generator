# generated by borea

# if you want to edit this file, add it to ignores in borea.config.json, glob syntax

# TODO: not implemented

from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING
from ....models.models import *

if TYPE_CHECKING:
    from ...oxide_region_api import OxideRegionAPI


class NetworkingBgpAnnounceSetDelete:
    def __init__(self, parent: "OxideRegionAPI"):
        self.parent = parent

    def networking_bgp_announce_set_delete(
        self,
        announce_set: NameOrId,
    ) -> Any:
        """


        Args:
            announce_set: Name or ID of the announce set

        Returns:
            Response data
        """
        path = f"/v1/system/networking/bgp-announce-set/{announce_set}"
        params = {}
        headers = {}
        json_data = None

        response = self.parent._make_request(
            method="DELETE",
            path=path,
            params=params,
            headers=headers,
            json_data=json_data,
        )
        return response.json()
