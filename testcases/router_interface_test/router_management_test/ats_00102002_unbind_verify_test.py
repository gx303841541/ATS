# coding=utf-8
import os
import sys
import re
import time
import datetime
import json
import random
import hashlib
from APIs.common_APIs import register_caseid, get_md5
import APIs.common_methods as common_methods
from router_msg.router_management import API_router_management


@register_caseid(casename=__name__)
class Test(common_methods.CommMethod):
	def run(self):
		self.common_para_dict["pwd"] = get_md5(self.config_file.get("app", "login_pwd"))

		# dm_unbind_router build msg
		msg_unbind = API_router_management.build_msg_unbind_verify(self.common_para_dict)

		# send msg to router
		if self.socket_send_to_router(json.dumps(msg_unbind) + '\n'):
			pass
		else:
			return self.case_fail("dm_unbind_router Send msg to router failed!")

		# recv msg from router
		data = self.socket_recv_from_router()
		if data:
			dst_packge = self.get_package_by_keyword(data, ['um_verify_user', 'result'], except_keyword_list=['mdp_msg'])
			self.LOG.debug(self.convert_to_dictstr(dst_packge[0]))
		else:
			return self.case_fail("timeout, server no response!")

		# msg check
		template = {
			"content": {
				"code": 0,
				"method": "um_verify_user",
				"msg": "success",
				"req_id": "no_need",
				"result": {
				},
				"timestamp": "no_need",
			},
			"encry": "no_need",
			"uuid": self.common_para_dict["device_uuid"],
		}
		if self.json_compare(template, dst_packge[0]):
			pass
		else:
			return self.case_fail("msg check failed!")
		return self.case_pass()


if __name__ == '__main__':
	Test().test()
