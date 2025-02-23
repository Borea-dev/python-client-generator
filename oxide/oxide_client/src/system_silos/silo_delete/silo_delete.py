# generated by borea

# if you want to edit this file, add it to ignores in borea.config.json, glob syntax

# TODO: not implemented

from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING
from ....models.models import *

if TYPE_CHECKING:
    from ...oxide_region_api import OxideRegionAPI


class SiloDelete:
    def __init__(self, parent: "OxideRegionAPI"):
        self.parent = parent

    def silo_delete(
        self,
        silo: NameOrId,
    ) -> Any:
        """
        Delete a silo by name or ID.

        Args:
            silo: Name or ID of the silo

        Returns:
            Response data
        """
        path = f"/v1/system/silos/{silo}"
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
