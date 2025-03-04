# generated by borea

# if you want to edit this file, add it to ignores in borea.config.json, glob syntax

# TODO: not implemented

from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING
from ....models.models import *

if TYPE_CHECKING:
    from ...oxide_region_api import OxideRegionAPI


class SystemPolicyUpdate:
    def __init__(self, parent: "OxideRegionAPI"):
        self.parent = parent

    def system_policy_update(
        self,
        role_assignments: List[FleetRoleRoleAssignment],
    ) -> Any:
        """


        Args:
            role_assignments: Roles directly assigned on this resource

        Returns:
            Response data
        """
        path = f"/v1/system/policy"
        params = None
        headers = None
        json_data = {
            "role_assignments": role_assignments
            if role_assignments is not None
            else None,
        }
        json_data = {k: v for k, v in json_data.items() if v is not None}

        response = self.parent._make_request(
            method="PUT",
            path=path,
            params=params,
            headers=headers,
            json_data=json_data,
        )
        return response.json()
