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
		self.common_para_dict["pwd"] = get_md5(self.config_file.get("app", "login_pwd"))

		# 模拟APP登录操作，获取Token
		# um_login_pwd build msg
		msg = API_router_management.build_msg_password_login(self.common_para_dict)

		# send msg to router
		self.router_logged = True
		if self.socket_send_to_router(json.dumps(msg) + '\n'):
			pass
		else:
			return self.case_fail("um_login_pwd Send msg to router failed!")

		# recv msg from router
		data = self.socket_recv_from_router()
		if data:
			dst_package = self.get_package_by_keyword(
				data, ['um_login_pwd', 'success'], except_keyword_list=['mdp_msg'])
			self.LOG.debug(self.convert_to_dictstr(dst_package[0]))
			data_dict = eval(dst_package[0])
			token = data_dict['content']['result']['token']
			self.LOG.debug(u"登录并获取Token成功！！")
		else:
			return self.case_fail("timeout, server no response!")

		# dm_unbind_router build msg
		msg_unbind = API_router_management.build_msg_unbind_router(self.common_para_dict)

		# dm_bind_router build msg
		msg_bind = API_router_management.build_msg_bind_router(self.common_para_dict, token=token)

		# send msg to router
		if self.socket_send_to_router(json.dumps(msg_unbind) + '\n'):
			pass
		else:
			return self.case_fail("dm_unbind_router Send msg to router failed!")

		# recv msg from router
		data = self.socket_recv_from_router()
		if data:
			dst_packge = self.get_package_by_keyword(
				data, ['dm_unbind_router', 'success'], except_keyword_list=['mdp_msg'])
			self.LOG.debug(self.convert_to_dictstr(dst_packge[0]))
			self.LOG.debug(u"已解绑，前置条件配置成功，开始测试！！！")
		else:
			return self.case_fail("dm_unbind_router timeout, server no response!")

		# send msg to router
		if self.socket_send_to_router(json.dumps(msg_bind) + '\n'):
			pass
		else:
			return self.case_fail("dm_bind_router Send msg to router failed!")

		# recv msg from router
		data = self.socket_recv_from_router()
		if data:
			dst_packge = self.get_package_by_keyword(
				data, ['dm_bind_router', 'result'], except_keyword_list=['mdp_msg'])
			self.LOG.debug(self.convert_to_dictstr(dst_packge[0]))
		else:
			return self.case_fail("dm_bind_router timeout, server no response!")

		# msg check
		template = {
			"content": {
				"code": 0,
				"method": "dm_bind_router",
				"msg": "success",
				"req_id": "no_need",
				"result": {
					"default_name": "no_need",
					"default_room": "no_need",
					"default_room_id": "no_need",
					#"family_id": self.common_para_dict["family_id"],
					#"router_id": self.common_para_dict["device_uuid"],
					#"user_id": self.common_para_dict['user_id'],
				},
				"timestamp": "no_need",
			},
			"encry": "no_need",
			"uuid": "no_need",
		}
		if self.json_compare(template, dst_packge[0]):
			pass
		else:
			return self.case_fail("msg check failed!")
		return self.case_pass()


if __name__ == '__main__':
	Test().test()
