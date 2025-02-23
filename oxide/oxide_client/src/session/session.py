# generated by borea

# if you want to edit this file, add it to ignores in borea.config.json, glob syntax

from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING
from ...models.models import *

from .current_user_view.current_user_view import CurrentUserView
from .current_user_groups.current_user_groups import CurrentUserGroups
from .current_user_ssh_key_list.current_user_ssh_key_list import CurrentUserSshKeyList
from .current_user_ssh_key_create.current_user_ssh_key_create import (
    CurrentUserSshKeyCreate,
)
from .current_user_ssh_key_view.current_user_ssh_key_view import CurrentUserSshKeyView
from .current_user_ssh_key_delete.current_user_ssh_key_delete import (
    CurrentUserSshKeyDelete,
)

if TYPE_CHECKING:
    from ..oxide_region_api import OxideRegionAPI


class Session:
    def __init__(self, parent: "OxideRegionAPI"):
        """
        Information pertaining to the current session.

        Args:
            parent: The parent client to use for the requests
        """
        self.parent = parent

        self.current_user_view = CurrentUserView(parent=parent).current_user_view
        self.current_user_groups = CurrentUserGroups(parent=parent).current_user_groups
        self.current_user_ssh_key_list = CurrentUserSshKeyList(
            parent=parent
        ).current_user_ssh_key_list
        self.current_user_ssh_key_create = CurrentUserSshKeyCreate(
            parent=parent
        ).current_user_ssh_key_create
        self.current_user_ssh_key_view = CurrentUserSshKeyView(
            parent=parent
        ).current_user_ssh_key_view
        self.current_user_ssh_key_delete = CurrentUserSshKeyDelete(
            parent=parent
        ).current_user_ssh_key_delete
