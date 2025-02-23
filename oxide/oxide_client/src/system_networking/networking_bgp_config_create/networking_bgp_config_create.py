# generated by borea

# if you want to edit this file, add it to ignores in borea.config.json, glob syntax

# TODO: not implemented

from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING
from ....models.models import *

if TYPE_CHECKING:
    from ...oxide_region_api import OxideRegionAPI


class NetworkingBgpConfigCreate:
    def __init__(self, parent: "OxideRegionAPI"):
        self.parent = parent

    def networking_bgp_config_create(
        self,
        asn: int,
        bgp_announce_set_id: NameOrId,
        description: str,
        name: Name,
        vrf: Optional[Name] = None,
    ) -> Any:
        """


        Args:
            asn: The autonomous system number of this BGP configuration.
            bgp_announce_set_id: No description provided
            description: Parameters for creating a BGP configuration. This includes and autonomous system number (ASN) and a virtual routing and forwarding (VRF) identifier.
            name: Names must begin with a lower case ASCII letter, be composed exclusively of lowercase ASCII, uppercase ASCII, numbers, and '-', and may not end with a '-'. Names cannot be a UUID, but they may contain a UUID. They can be at most 63 characters long.
            vrf: Names must begin with a lower case ASCII letter, be composed exclusively of lowercase ASCII, uppercase ASCII, numbers, and '-', and may not end with a '-'. Names cannot be a UUID, but they may contain a UUID. They can be at most 63 characters long.

        Returns:
            Response data
        """
        path = f"/v1/system/networking/bgp"
        params = None
        headers = None
        json_data = {
            "asn": asn if asn is not None else None,
            "bgp_announce_set_id": (
                bgp_announce_set_id if bgp_announce_set_id is not None else None
            ),
            "description": description if description is not None else None,
            "name": name if name is not None else None,
            "vrf": vrf if vrf is not None else None,
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
