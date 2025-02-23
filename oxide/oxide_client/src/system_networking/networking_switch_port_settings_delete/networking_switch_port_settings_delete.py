# generated by borea

# if you want to edit this file, add it to ignores in borea.config.json, glob syntax

# TODO: not implemented

from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING
from ....models.models import *

if TYPE_CHECKING:
    from ...oxide_region_api import OxideRegionAPI


class NetworkingSwitchPortSettingsDelete:
    def __init__(self, parent: "OxideRegionAPI"):
        self.parent = parent

    def networking_switch_port_settings_delete(
        self,
        port_settings: Optional[NameOrId] = None,
    ) -> Any:
        """


        Args:
            port_settings: An optional name or id to use when selecting port settings.

        Returns:
            Response data
        """
        path = f"/v1/system/networking/switch-port-settings"
        params = {}
        headers = {}
        if port_settings is not None:
            params["port_settings"] = port_settings
        json_data = None

        response = self.parent._make_request(
            method="DELETE",
            path=path,
            params=params,
            headers=headers,
            json_data=json_data,
        )
        return response.json()
