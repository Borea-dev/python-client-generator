# generated by borea

# if you want to edit this file, add it to ignores in borea.config.json, glob syntax

from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING
from ...models.models import *

from .system_metric.system_metric import SystemMetric
from .system_timeseries_query.system_timeseries_query import SystemTimeseriesQuery
from .system_timeseries_schema_list.system_timeseries_schema_list import (
    SystemTimeseriesSchemaList,
)

if TYPE_CHECKING:
    from ..oxide_region_api import OxideRegionAPI


class SystemMetrics:
    def __init__(self, parent: "OxideRegionAPI"):
        """
        Metrics provide insight into the operation of the Oxide deployment. These include telemetry on hardware and software components that can be used to understand the current state as well as to diagnose issues.

        Args:
            parent: The parent client to use for the requests
        """
        self.parent = parent

        self.system_metric = SystemMetric(parent=parent).system_metric
        self.system_timeseries_query = SystemTimeseriesQuery(
            parent=parent
        ).system_timeseries_query
        self.system_timeseries_schema_list = SystemTimeseriesSchemaList(
            parent=parent
        ).system_timeseries_schema_list
