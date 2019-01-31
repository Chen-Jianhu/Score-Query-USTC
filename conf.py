# -*- coding: utf-8 -*-
# @File 	: conf.py
# @Author 	: jianhuChen
# @Date 	: 2019-01-29 13:08:45
# @License 	: Copyright(C), USTC
# @Last Modified by  : jianhuChen
# @Last Modified time: 2019-02-01 01:12:48

# 账号
USER_ACCOUNTS = {
	'userId': 'SA18225001',
	'userPwd': '123456'
}

# 账号登录接口
# 登录科大研究生平台时，有两种途径：
# 1. 研究生信息平台，此接口的缺点是需要手动输入验证码，但是稳定
#    手动输入验证码：验证码的路径为此工程的根目录
# 2. 科大统一身份认证，此接口的好处是不用输入验证码（所以默认使用此接口），但是个人感觉没有上面的接口稳定
# 只能将下面两个接口其中一个设置为`True`
# 若两个均设为`True`，则使用 科大研究生平台接口 登录
USTC_YJS_PLATFORMS_LOGIN_API = False
# 科大统一身份认证接口
USTC_UNIFIED_IDENTITY_AUTHENTICATION_LOGIN_API = True


# 是否输出日志到文件
OUT_PUT_LOG_TO_FILE_ENABLED = True
OUT_PUT_LOG_TO_FILE_PATH = 'score.log'  # 日志目录
