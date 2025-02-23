# generated by borea

# if you want to edit this file, add it to ignores in borea.config.json, glob syntax

# TODO: not implemented

from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING
from ....models.models import *

if TYPE_CHECKING:
    from ...oxide_region_api import OxideRegionAPI


class InstanceEphemeralIpDetach:
    def __init__(self, parent: "OxideRegionAPI"):
        self.parent = parent

    def instance_ephemeral_ip_detach(
        self,
        instance: NameOrId,
        project: Optional[NameOrId] = None,
    ) -> Any:
        """


        Args:
            instance: Name or ID of the instance
            project: Name or ID of the project

        Returns:
            Response data
        """
        path = f"/v1/instances/{instance}/external-ips/ephemeral"
        params = {}
        headers = {}
        if project is not None:
            params["project"] = project
        json_data = None

        response = self.parent._make_request(
            method="DELETE",
            path=path,
            params=params,
            headers=headers,
            json_data=json_data,
        )
        return response.json()
