# generated by borea

# if you want to edit this file, add it to ignores in borea.config.json, glob syntax

# TODO: not implemented

from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING
from ....models.models import *

if TYPE_CHECKING:
    from ...oxide_region_api import OxideRegionAPI


class ProjectUpdate:
    def __init__(self, parent: "OxideRegionAPI"):
        self.parent = parent

    def project_update(
        self,
        project: NameOrId,
        description: Optional[str] = None,
        name: Optional[Name] = None,
    ) -> Any:
        """


        Args:
            project: Name or ID of the project
            description: Updateable properties of a `Project`
            name: Names must begin with a lower case ASCII letter, be composed exclusively of lowercase ASCII, uppercase ASCII, numbers, and '-', and may not end with a '-'. Names cannot be a UUID, but they may contain a UUID. They can be at most 63 characters long.

        Returns:
            Response data
        """
        path = f"/v1/projects/{project}"
        params = {}
        headers = {}
        json_data = {
            "description": description if description is not None else None,
            "name": name if name is not None else None,
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
