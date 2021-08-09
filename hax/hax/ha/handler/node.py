# Copyright (c) 2021 Seagate Technology LLC and/or its Affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# For any questions about this software or licensing,
# please email opensource@seagate.com or cortx-questions@seagate.com.
#

import logging

from hax.ha.events import Event
from hax.ha.handler import EventHandler
from hax.message import BroadcastHAStates
from hax.motr.planner import WorkPlanner
from hax.types import HAState, ServiceHealth
from hax.util import ConsulUtil

LOG = logging.getLogger('hax')


class NodeEventHandler(EventHandler):
    """
    Handles HA events with resource_type == 'node'.

    As a result of such HA event the corresponding BroadcastHAStates is
    offered to WorkPlanner.
    """
    def __init__(self, consul: ConsulUtil, planner: WorkPlanner):
        """Constructor."""
        self.cns = consul
        self.planner = planner

    def handle(self, msg: Event) -> None:
        node_fid = self.cns.get_node_fid(msg.node_id)
        if not node_fid:
            LOG.warn('Unknown [node_id=%s] provided. HA event is ignored',
                     msg.node_id)
            return

        get_health = self._get_status_by_text

        self.planner.add_command(
            BroadcastHAStates(states=[
                HAState(fid=node_fid, status=get_health(msg.event_type))
            ],
                              reply_to=None))

    def _get_status_by_text(self, status: str):
        if status == 'online':
            return ServiceHealth.OK
        elif status == 'offline':
            return ServiceHealth.FAILED
        else:
            return ServiceHealth.UNKNOWN
