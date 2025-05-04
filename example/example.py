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

        # 注册内容库资源
        # register_mediaInfo_request = ice20201109_models.RegisterMediaInfoRequest()
        # register_mediaInfo_request.input_url = 'http://krillin-3.oss-cn-shanghai.aliyuncs.com/main.mp4'
        # register_mediaInfo_request.media_type = 'video'
        # register_mediaInfo_request.business_type = 'video'
        # register_mediaInfo_request.title = 'default_title'

        # register_mediaInfo_response = client.register_media_info(register_mediaInfo_request)
        # print(register_mediaInfo_response)
        # print('request id:', register_mediaInfo_response.body.request_id)
        # print('media info:', register_mediaInfo_response.body.media_id)

        # 获取媒资内容信息
        get_mediaInfo_request = ice20201109_models.GetMediaInfoRequest()
        # get media info by mediaId
        # get_mediaInfo_request.media_id = '****20b48fb04483915d4f2cd8ac****'
        # get media info by inputUrl
        get_mediaInfo_request.input_url = 'http://krillin-3.oss-cn-shanghai.aliyuncs.com/main.mp4'

        get_mediaInfo_response = client.get_media_info(get_mediaInfo_request)

        print('request id:', get_mediaInfo_response.body.request_id)
        print('media info:', get_mediaInfo_response.body.media_info)

        # 更新媒体信息
        update_mediaInfo_request = ice20201109_models.UpdateMediaInfoRequest()
        # get media info by mediaId
        update_mediaInfo_request.media_id = '****20b48fb04483915d4f2cd8ac****'
        # get media info by inputUrl
        # request.input_url = 'http://example-bucket.oss-cn-shanghai.aliyuncs.com/example.mp4'

        update_mediaInfo_response = client.update_media_info(update_mediaInfo_request)
        print(update_mediaInfo_response)
        print('request id:', update_mediaInfo_response.body.request_id)
        print('media info:', update_mediaInfo_response.body.media_info)

        # 删除媒资信息
        delete_mediaInfos_request = ice20201109_models.DeleteMediaInfosRequest()
        # delete media info by mediaId
        delete_mediaInfos_request.media_ids = '****20b48fb04483915d4f2cd8ac****,****81539d420bb04d8ac4f48f2c****'
        # delete media info by inputUrl
        # request.input_urls = 'http://example-bucket.oss-cn-shanghai.aliyuncs.com/example.mp4,http://example-bucket.oss-cn-shanghai.aliyuncs.com/example2.mp4'

        delete_mediaInfos_response = client.delete_media_infos(delete_mediaInfos_request)
        print(delete_mediaInfos_response)
        print('request id:', delete_mediaInfos_response.body.request_id)
        print('ignored list:', delete_mediaInfos_response.body.ignored_list)

        # 列出媒资基础信息
        list_media_basicInfos_request = ice20201109_models.ListMediaBasicInfosRequest()
        # set start time (exclusive)
        list_media_basicInfos_request.start_time = '2020-12-20T12:00:00Z'
        # set end time (inclusive)
        list_media_basicInfos_request.end_time = '2020-12-20T13:00:00Z'
        # set max return entries
        list_media_basicInfos_request.max_results = 5

        list_media_basicInfos_response = client.list_media_basic_infos(list_media_basicInfos_request)
        print(list_media_basicInfos_response)
        print('request id:', list_media_basicInfos_response.body.request_id)
        print('media info list:', list_media_basicInfos_response.body.media_infos)
        print('next token', list_media_basicInfos_response.body.next_token)
        print('max results', list_media_basicInfos_response.body.max_results)

if __name__ == '__main__':
    Sample.main()    