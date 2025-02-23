# generated by borea

# if you want to edit this file, add it to ignores in borea.config.json, glob syntax

# TODO: not implemented

from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING
from ....models.models import *

if TYPE_CHECKING:
    from ...oxide_region_api import OxideRegionAPI


class VpcCreate:
    def __init__(self, parent: "OxideRegionAPI"):
        self.parent = parent

    def vpc_create(
        self,
        project: NameOrId,
        description: str,
        dns_name: Name,
        name: Name,
        ipv6_prefix: Optional[Ipv6Net] = None,
    ) -> Any:
        """


        Args:
            project: Name or ID of the project
            description: Create-time parameters for a `Vpc`
            dns_name: Names must begin with a lower case ASCII letter, be composed exclusively of lowercase ASCII, uppercase ASCII, numbers, and '-', and may not end with a '-'. Names cannot be a UUID, but they may contain a UUID. They can be at most 63 characters long.
            name: Names must begin with a lower case ASCII letter, be composed exclusively of lowercase ASCII, uppercase ASCII, numbers, and '-', and may not end with a '-'. Names cannot be a UUID, but they may contain a UUID. They can be at most 63 characters long.
            ipv6_prefix: An IPv6 subnet, including prefix and subnet mask

        Returns:
            Response data
        """
        path = f"/v1/vpcs"
        params = {}
        headers = {}
        if project is not None:
            params["project"] = project
        json_data = {
            "description": description if description is not None else None,
            "dns_name": dns_name if dns_name is not None else None,
            "ipv6_prefix": ipv6_prefix if ipv6_prefix is not None else None,
            "name": name if name is not None else None,
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
