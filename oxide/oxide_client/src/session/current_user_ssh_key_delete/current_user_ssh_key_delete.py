# generated by borea

# if you want to edit this file, add it to ignores in borea.config.json, glob syntax

# TODO: not implemented

from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING
from ....models.models import *

if TYPE_CHECKING:
    from ...oxide_region_api import OxideRegionAPI


class CurrentUserSshKeyDelete:
    def __init__(self, parent: "OxideRegionAPI"):
        self.parent = parent

    def current_user_ssh_key_delete(
        self,
        ssh_key: NameOrId,
    ) -> Any:
        """
        Delete an SSH public key associated with the currently authenticated user.

        Args:
            ssh_key: Name or ID of the SSH key

        Returns:
            Response data
        """
        path = f"/v1/me/ssh-keys/{ssh_key}"
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
