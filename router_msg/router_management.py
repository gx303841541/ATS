# -*- coding: utf-8 -*-

"""common methods
by Ann 2017-11-28
use:
	methods in class CommMethod can be used by all the testcases
"""
import json
import re
import sys
import time


class API_router_management():
	def __init__(self):
		pass

	@staticmethod
	def build_msg_bind_router(common_para_dict, token, client_uuid="123"):
		msg = {
			"uuid": client_uuid,
			"encry": "false",
			"content": {
				"method": 'dm_bind_router',
				"req_id": 123,
				"timestamp": 1511230237309,
				"params": {
					"family_id": common_para_dict['family_id'],
					"family_name": common_para_dict['family_name'],
					"token": token,
				}
			}
		}
		return msg

	@staticmethod
	def build_msg_unbind_verify(common_para_dict, client_uuid="123"):
		msg = {
			"uuid": client_uuid,
			"encry": "false",
			"content": {
				"method": "um_verify_user",
				"req_id": 123,
				"timestamp": 1511230237309,
				"params": {
					"phone": common_para_dict['phone'],
					"password": common_para_dict['pwd'],
					"family_id": common_para_dict['family_id'],
				}
			}
		}
		return msg

	@staticmethod
	def build_msg_unbind_router(common_para_dict, client_uuid="123"):
		msg = {
			"uuid": client_uuid,
			"encry": "false",
			"content": {
				"method": "dm_unbind_router",
				"req_id": 123,
				"timestamp": 1511230237309,
				"params": {
					"phone": common_para_dict['phone'],
					"family_id": common_para_dict['family_id'],
					"clear_data": 0,
				}
			}
		}
		return msg

	@staticmethod
	def build_msg_password_login(common_para_dict, client_uuid="123"):
		msg = {
			"uuid": client_uuid,
			"encry": "false",
			"content": {
				"method": 'um_login_pwd',
				"timestamp": 12345667,
				"req_id": 123,
				"params": {
					"phone": common_para_dict['phone'],
					"pwd": common_para_dict['pwd'],
					"os_type": "Android",
					"app_version": "v0.5",
					"os_version": "android4.3",
					"hardware_version": "Huawei",
				}
			}
		}
		return msg

	@staticmethod
	def build_msg_logout_router(common_para_dict, client_uuid="123"):
		msg = {
			"uuid": client_uuid,
			"encry": "false",
			"content": {
				"method": 'acc_logout',
				"timestamp": 12345667,
				"req_id": 123,
				"params": {
				}
			}
		}
		return msg

	@staticmethod
	def build_msg_sync_pwd(common_para_dict):
		msg = {
			"uuid": client_uuid,
			"encry": "false",
			"content": {
				"method": 'um_sync_pwd',
				"timestamp": 12345667,
				"req_id": 123,
				"params": {
					"token": common_para_dict['token'],
					"os_type": "Android"
				}
			}
		}
		return msg

	@staticmethod
	def build_msg_token_login(common_para_dict, client_uuid="123"):
		msg = {
			"uuid": client_uuid,
			"encry": "false",
			"content": {
				"method": 'um_auth',
				"timestamp": 12345667,
				"req_id": 123,
				"params": {
					"user_id": common_para_dict['user_id'],
					"token": common_para_dict['token'],
					"os_type": "Android",
				}
			}
		}
		return msg

	@staticmethod
	def build_msg_verify_router(common_para_dict, client_uuid="123"):
		msg = {
			"uuid": client_uuid,
			"encry": "false",
			"content": {
				"method": 'um_auth',
				"timestamp": 12345667,
				"req_id": 123,
				"params": {
					"user_id": common_para_dict['user_id'],
					"token": common_para_dict['token'],
					"os_type": "Android",
				}
			}
		}
		return msg
