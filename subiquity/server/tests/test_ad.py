# Copyright 2023 Canonical, Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import unittest
from subiquity.common.types import ADConnectionInfo, AdJoinResult
from subiquity.server.controllers.ad import ADController
from subiquity.models.ad import ADModel
from subiquitycore.tests.mocks import make_app


class TestAdJoin(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.app = make_app()
        self.controller = ADController(self.app)
        self.controller.model = ADModel()

    async def test_never_join(self):
        # Calling join_result_GET has no effect if the model is not set.
        result = await self.controller.join_result_GET(wait=True)
        self.assertEqual(result, AdJoinResult.UNKNOWN)

    async def test_join_Unknown(self):
        # Result remains UNKNOWN while ADController.join_domain is not called.
        self.controller.model.set(ADConnectionInfo(domain_name='ubuntu.com',
                                                   admin_name='Helper',
                                                   password='1234'))

        result = await self.controller.join_result_GET(wait=False)
        self.assertEqual(result, AdJoinResult.UNKNOWN)

    async def test_join_OK(self):
        # The equivalent of a successful POST
        self.controller.model.set(ADConnectionInfo(domain_name='ubuntu.com',
                                                   admin_name='Helper',
                                                   password='1234'))
        # Mimics a client requesting the join result. Blocking by default.
        result = self.controller.join_result_GET()
        # Mimics a calling from the install controller.
        await self.controller.join_domain('this', 'AD Join')
        self.assertEqual(await result, AdJoinResult.OK)

    async def test_join_Join_Error(self):
        self.controller.model.set(ADConnectionInfo(domain_name='jubuntu.com',
                                                   admin_name='Helper',
                                                   password='1234'))
        await self.controller.join_domain('this', 'AD Join')
        result = await self.controller.join_result_GET(wait=True)
        self.assertEqual(result, AdJoinResult.JOIN_ERROR)

    async def test_join_Pam_Error(self):
        self.controller.model.set(ADConnectionInfo(domain_name='pubuntu.com',
                                                   admin_name='Helper',
                                                   password='1234'))
        await self.controller.join_domain('this', 'AD Join')
        result = await self.controller.join_result_GET(wait=True)
        self.assertEqual(result, AdJoinResult.PAM_ERROR)
