import json
import os
import sys
from typing import List
from dotenv import load_dotenv

# 加载.env文件中的环境变量
load_dotenv(dotenv_path='/workspace/Python/example/.env')

access_key_id = os.getenv('ACCESS_KEY_ID')
access_key_secret = os.getenv('ACCESS_KEY_SECRET')
print(access_key_id,access_key_secret)
print("hello",os.environ['OSS_ACCESS_KEY_ID'],"hello")
# region = "shanghahi"
os.environ['ALIBABA_CLOUD_ACCESS_KEY_ID'] = access_key_id
os.environ['ALIBABA_CLOUD_ACCESS_KEY_SECRET'] = access_key_secret
os.environ['OSS_ACCESS_KEY_ID'] = access_key_id
os.environ['OSS_ACCESS_KEY_SECRET'] = access_key_secret


from alibabacloud_ice20201109.client import Client as ICE20201109Client
# 引入阿里云IMS SDK
from alibabacloud_ice20201109 import models as ice20201109_models
# Credentials和云产品SDK都需引入Client，此处为创建别名
from alibabacloud_credentials.client import Client as CredClient
# 引入阿里云SDK核心包
from alibabacloud_tea_openapi.models import Config


#######需要的依赖#############
#pip install alibabacloud_credentials
#pip install alibabacloud_ice20201109==1.3.11
class Sample:

    # 初始化客户端
    @staticmethod
    def create_client(region: str) -> ICE20201109Client:
        # 使用默认凭证初始化Credentials Client
        cred = CredClient()
        config = Config(credential = cred)
        # 配置云产品服务接入地址（endpoint）
        config.endpoint = 'ice.' + region + '.aliyuncs.com'
        # 使用Credentials Client初始化ECS Client
        return ICE20201109Client(config)           

    # @staticmethod
    # def create_client(
    #     access_key_id: str,
    #     access_key_secret: str,
    #     region: str,

    # ) -> ICE20201109Client:
    #     # 如需硬编码AccessKey ID和AccessKey Secret，代码如下，但强烈建议不要把AccessKey ID和AccessKey Secret保存到工程代码里，否则可能导致AccessKey泄露，威胁您账号下所有资源的安全
    #     print(access_key_id)
    #     config = Config(
    #         # 必填，您的 AccessKey ID,
    #         access_key_id = access_key_id,
    #         # 必填，您的 AccessKey Secret,
    #         access_key_secret = access_key_secret
    #     )
    #     # 访问的域名
    #     config.endpoint = 'ice.' + region + '.aliyuncs.com'
    #     return ICE20201109Client(config)

    # 读取命令行参数
    @staticmethod
    def main() -> None:
        region = 'cn-shanghai'
        # 初始化客户端
        client = Sample.create_client(region)

        # 创建云剪辑工程
        create_editing_project = ice20201109_models.CreateEditingProjectRequest()
        create_editing_project.title = '测试工程名字'
        create_editing_project.description = '测试工程描述'
        create_editing_project.timeline = "{\"VideoTracks\":[{\"VideoTrackClips\":[{\"MediaId\":\"****81539d420bb04d8ac4f48f2c****\"},{\"MediaId\":\"****20b48fb04483915d4f2cd8ac****\"}]}]}"
        create_editing_project.cover_url = 'http://xxxx/coverUrl.jpg'
        create_editing_response = client.create_editing_project(create_editing_project)
        print(create_editing_response)
        print('request id:', create_editing_response.body.request_id)
        print('project:', create_editing_response.body.project)

if __name__ == '__main__':
    Sample.main()    