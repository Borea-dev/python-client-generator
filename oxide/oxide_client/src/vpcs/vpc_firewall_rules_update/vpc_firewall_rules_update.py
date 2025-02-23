# generated by borea

# if you want to edit this file, add it to ignores in borea.config.json, glob syntax

# TODO: not implemented

from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING
from ....models.models import *

if TYPE_CHECKING:
    from ...oxide_region_api import OxideRegionAPI


class VpcFirewallRulesUpdate:
    def __init__(self, parent: "OxideRegionAPI"):
        self.parent = parent

    def vpc_firewall_rules_update(
        self,
        vpc: NameOrId,
        rules: List[VpcFirewallRuleUpdate],
        project: Optional[NameOrId] = None,
    ) -> Any:
        """
                The maximum number of rules per VPC is 1024.

        Targets are used to specify the set of instances to which a firewall rule applies. You can target instances directly by name, or specify a VPC, VPC subnet, IP, or IP subnet, which will apply the rule to traffic going to all matching instances. Targets are additive: the rule applies to instances matching ANY target. The maximum number of targets is 256.

        Filters reduce the scope of a firewall rule. Without filters, the rule applies to all packets to the targets (or from the targets, if it's an outbound rule). With multiple filters, the rule applies only to packets matching ALL filters. The maximum number of each type of filter is 256.

                Args:
                    vpc: Name or ID of the VPC
                    rules: Updated list of firewall rules. Will replace all existing rules.
                    project: Name or ID of the project, only required if `vpc` is provided as a `Name`

                Returns:
                    Response data
        """
        path = f"/v1/vpc-firewall-rules"
        params = {}
        headers = {}
        if project is not None:
            params["project"] = project
        if vpc is not None:
            params["vpc"] = vpc
        json_data = {
            "rules": rules if rules is not None else None,
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
