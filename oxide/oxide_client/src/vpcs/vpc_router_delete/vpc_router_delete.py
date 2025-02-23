# generated by borea

# if you want to edit this file, add it to ignores in borea.config.json, glob syntax

# TODO: not implemented

from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING
from ....models.models import *

if TYPE_CHECKING:
    from ...oxide_region_api import OxideRegionAPI


class VpcRouterDelete:
    def __init__(self, parent: "OxideRegionAPI"):
        self.parent = parent

    def vpc_router_delete(
        self,
        router: NameOrId,
        project: Optional[NameOrId] = None,
        vpc: Optional[NameOrId] = None,
    ) -> Any:
        """


        Args:
            router: Name or ID of the router
            project: Name or ID of the project, only required if `vpc` is provided as a `Name`
            vpc: Name or ID of the VPC

        Returns:
            Response data
        """
        path = f"/v1/vpc-routers/{router}"
        params = {}
        headers = {}
        if project is not None:
            params["project"] = project
        if vpc is not None:
            params["vpc"] = vpc
        json_data = None

        response = self.parent._make_request(
            method="DELETE",
            path=path,
            params=params,
            headers=headers,
            json_data=json_data,
        )
        return response.json()
