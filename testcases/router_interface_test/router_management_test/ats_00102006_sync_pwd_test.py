# coding=utf-8
import datetime
import hashlib
import json
import os
import random
import re
import sys
import time

import APIs.common_methods as common_methods
from APIs.common_APIs import register_caseid, get_md5
from router_msg.router_management import API_router_management


@register_caseid(casename=__name__)
class Test(common_methods.CommMethod):
	def run(self):
		# build msg
		msg = API_router_management.build_msg_sync_pwd(self.common_para_dict)

		# send msg to router
		if self.socket_send_to_router(json.dumps(msg) + '\n'):
			pass
		else:
			return self.case_fail("Send msg to router failed!")

		# recv msg from router
		data = self.socket_recv_from_router()
		if data:
			dst_package = self.get_package_by_keyword(
				data, ['um_sync_pwd', 'result'], except_keyword_list=['mdp_msg'])
			self.LOG.debug(self.convert_to_dictstr(dst_package[0]))
		else:
			return self.case_fail("timeout, server no response!")

		# msg check
		template = {
			"content": {
				"method": "um_sync_pwd",
				"req_id": "no_need",
				"timestamp": "no_need",
				"msg": "success",
				"code": 0,
				"result": {
					"token": "no_need",
					"user_id": self.common_para_dict["user_id"],
				}
			},
			"encry": "no_need",
			"uuid": "no_need",
		}
		if self.json_compare(template, dst_package[0]):
			pass
		else:
			return self.case_fail("msg check failed!")
		return self.case_pass()


if __name__ == '__main__':
	Test().test()
