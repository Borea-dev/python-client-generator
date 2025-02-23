# generated by borea

# if you want to edit this file, add it to ignores in borea.config.json, glob syntax

# TODO: not implemented

from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING
from ....models.models import *

if TYPE_CHECKING:
    from ...oxide_region_api import OxideRegionAPI


class NetworkingLoopbackAddressDelete:
    def __init__(self, parent: "OxideRegionAPI"):
        self.parent = parent

    def networking_loopback_address_delete(
        self,
        address: str,
        rack_id: str,
        subnet_mask: int,
        switch_location: Name,
    ) -> Any:
        """


        Args:
            address: The IP address and subnet mask to use when selecting the loopback address.
            rack_id: The rack to use when selecting the loopback address.
            subnet_mask: The IP address and subnet mask to use when selecting the loopback address.
            switch_location: The switch location to use when selecting the loopback address.

        Returns:
            Response data
        """
        path = f"/v1/system/networking/loopback-address/{rack_id}/{switch_location}/{address}/{subnet_mask}"
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
