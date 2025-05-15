import json
import os
import sys
from typing import List
from dotenv import load_dotenv

# 加载.env文件中的环境变量
load_dotenv(dotenv_path='./example/.env')

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
from alibabacloud_tea_util import models as util_models


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

        
        # 获取云剪辑工程
        get_editing_project = ice20201109_models.GetEditingProjectRequest()
        get_editing_project.project_id = 'b268ac091da347b180c2c17272253048'
        get_editing_response = client.get_editing_project(get_editing_project)
        print(get_editing_response)
        print('request id:', get_editing_response.body.request_id)
        print('project:', get_editing_response.body.project)

        # submit_asrjob_request = ice20201109_models.SubmitASRJobRequest(
        #     input_file='https://ice-document-materials.oss-cn-shanghai.aliyuncs.com/test_media/h5.mp4'
        # )
        # runtime = util_models.RuntimeOptions()
        # # 复制代码运行请自行打印 API 的返回值
        # api_call_back = client.submit_asrjob_with_options(submit_asrjob_request, runtime)
        # print("\n========================")
        # print(api_call_back.body)
        # print("========================")
         # 注册内容库资源
        # register_mediaInfo_request = ice20201109_models.RegisterMediaInfoRequest()
        # register_mediaInfo_request.input_url = 'http://krillin-3.oss-cn-shanghai.aliyuncs.com/main.mp4'
        # register_mediaInfo_request.media_type = 'video'
        # register_mediaInfo_request.business_type = 'video'
        # register_mediaInfo_request.title = 'default_title'

        # register_mediaInfo_response = client.register_media_info(register_mediaInfo_request)
        # print('request id:', register_mediaInfo_response.body.request_id)
        # print('media info:', register_mediaInfo_response.body.media_id)

        # media_id_test = register_mediaInfo_response.body.media_id
        
        # 
        timeline1 = """
                    {
                        "VideoTracks": 
                        [
                            {
                             "VideoTrackClips": 
                                [
                                    {
                                        "MediaURL": "http://krillin-3.oss-cn-shanghai.aliyuncs.com/start.mp4",
                                        "AdaptMode": "Cover",
                                        "Width": 1,
                                        "Height": 1,
                                    },
                                    {
                                        "Type": "Image",
                                        "MediaURL": "http://krillin-3.oss-cn-shanghai.aliyuncs.com/tranque.png",
                                        "AdaptMode": "Cover",
                                        "Width": 1,
                                        "Height": 1,
                                        "Duration": 3,
                                    },
                                    {
                                        "MediaURL": "http://krillin-3.oss-cn-shanghai.aliyuncs.com/main.mp4",
                                        "MainTrack": true,
                                        "AdaptMode": "Contain",
                                        "Effects": [{
                                            "Type": "AI_ASR",
                                            "Font": "AlibabaPuHuiTi",
                                            "Alignment": "TopCenter",   
                                            "Y": 600,
                                            "Outline": 10,
                                            "OutlineColour": "#ffffff",
                                            "FontSize": 60,
                                            "FontColor": "#000079",
                                            "FontFace": {
                                            "Bold": true,
                                            "Italic": false,
                                            "Underline": false
                                            }
                                        }]
                                    },
                                    {
                                        "MediaURL": "http://krillin-3.oss-cn-shanghai.aliyuncs.com/end.mp4",
                                         "Width": 1,
                                        "Height": 1,
                                        "AdaptMode": "Cover"
                                    }
                                ]
                            },
                            
                        ],
                        "AudioTracks": [{
                            "AudioTrackClips": [{
                            "Type": "AI_TTS",
                            "Content": "全球肺癌发病率上升的背后原因是什么",
                            "Voice": "sicheng",
                            "TimelineIn":3
                                            }],
                            
                        }],
                        "SubtitleTracks": [
                            {
                                "SubtitleTrackClips": [
                                    {
                                        "Type": "Text",
                                        "X": 0,
                                        "Y": 200,
                                        "Content": "主标题80号字",
                                        "Angle": 90,
                                        "Alignment": "TopCenter",
                                        "FontSize": 80,
                                        "FontColorOpacity": 1,
                                        "EffectColorStyle": "CS0003-000023",
                                        "FontFace": {
                                            "Bold": true
                                        },
                                        "TimelineIn": 0,
                                        "TimelineOut": 3,
                                    }
                                ]
                            }
                        ]
                    }
               """

        timeline1_1 = """
                    {
                        "VideoTracks": 
                        [
                            {
                             "VideoTrackClips": 
                                [
                                    {
                                        "MediaURL": "http://krillin-3.oss-cn-shanghai.aliyuncs.com/start.mp4",
                                        "AdaptMode": "Cover",
                                        "Width": 1,
                                        "Height": 1,
                                    },
                                    {
                                        "Type": "Image",
                                        "MediaURL": "http://krillin-3.oss-cn-shanghai.aliyuncs.com/tranque.png",
                                        "AdaptMode": "Cover",
                                        "Width": 1,
                                        "Height": 1,
                                        "Duration": 3,
                                    }
                                ]
                            },
                            
                        ],
                        "AudioTracks": [{
                            "AudioTrackClips": [{
                            "Type": "AI_TTS",
                            "Content": "全球肺癌发病率上升的背后原因是什么",
                            "Voice": "sicheng",
                            "TimelineIn":3
                                            }],
                            
                        }],
                        "SubtitleTracks": [
                            {
                                "SubtitleTrackClips": [
                                    {
                                        "Type": "Text",
                                        "X": 0,
                                        "Y": 200,
                                        "Content": "贵\n州\n市\n骨\n科\n医\n院\n\n\n骨\n科\n\n\n",
                                        "LineSpacing": -5,
                                        "Alignment": "TopCenter",
                                        "FontSize": 45,
                                        "FontColorOpacity": 1,
                                        "EffectColorStyle": "SiYuan Heiti",
                                        "FontFace": {
                                            "Bold": true
                                        },
                                        "TimelineIn": 0,
                                        "TimelineOut": 3,
                                        "SubtitleEffects": [
                                            {
                                                "Type": "Box",
                                                "ImageUrl": "https://krillin-3.oss-cn-shanghai.aliyuncs.com/hos_ks.png",
                                                "XShift":-1
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
               """


        timeline1_2 = """
                    {
                        "VideoTracks": 
                        [
                            {
                             "VideoTrackClips": 
                                [
                                    {
                                        "MediaURL": "http://krillin-3.oss-cn-shanghai.aliyuncs.com/start.mp4",
                                        "AdaptMode": "Cover",
                                        "Width": 1,
                                        "Height": 1,
                                    },
                                    {
                                        "Type": "Image",
                                        "MediaURL": "http://krillin-3.oss-cn-shanghai.aliyuncs.com/tranque.png",
                                        "AdaptMode": "Cover",
                                        "Width": 1,
                                        "Height": 1,
                                        "Duration": 3, 
                                        "ClipId": "main-1",
                                    }
                                ]
                            },
                            
                        ],
                        
                        "SubtitleTracks": [
                            {
                                "SubtitleTrackClips": [
                                    {
                                        "Type": "Text",
                                        "X": 128,
                                        "Y": 120,
                                        "Content": "贵\n州\n市\n骨\n科\n医\n院\n\n\n骨\n科\n\n\n",
                                        "LineSpacing": -5,
                                        "FontSize": 45,
                                        "FontColorOpacity": 1,
                                        "EffectColorStyle": "SiYuan Heiti",
                                        ReferenceClipId: "main-1",
                                        "FontFace": {
                                            "Bold": true
                                        },
                                        "SubtitleEffects": [
                                            {
                                                "Type": "Box",
                                                "ImageUrl": "https://krillin-3.oss-cn-shanghai.aliyuncs.com/hos_ks.png",
                                                "XShift":-6,
                                                "YBord": 20,
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
               """
    
        timeline2 = """
                    {
                        "VideoTracks": [{
                            "VideoTrackClips": [{
                            "MediaURL": "https://ice-document-materials.oss-cn-shanghai.aliyuncs.com/test_media/h5.mp4",
                            "Effects": [{
                                "Type": "AI_ASR",
                                "Font": "AlibabaPuHuiTi",
                                "Alignment": "BottomCenter",   
                            
                                "Outline": 10,
                                "OutlineColour": "#ffffff",
                                "FontSize": 60,
                                "FontColor": "#000079",
                                "FontFace": {
                                "Bold": true,
                                "Italic": false,
                                "Underline": false
                                }
                            }]
                            }]
                        }]
                    }
               """

        timeline3 = """
                    {
                         "VideoTracks": [{
                            "VideoTrackClips": [{
                                "MainTrack": true,
                                "MediaURL": "https://ice-document-materials.oss-cn-shanghai.aliyuncs.com/test_media/h5.mp4",
                            }]
                        }], 
                        "SubtitleTracks": [{
                                "SubtitleTrackClips": [{
                                    "Type": "Subtitle",
                                    "SubType": "srt",
                                    "FileURL": "http://krillin-3.oss-cn-shanghai.aliyuncs.com/subtitle.srt",
                                    "Font": "AlibabaPuHuiTi",
                                    "Alignment": "TopCenter",   
                                    "Y": 600,
                                    "Outline": 10,
                                    "OutlineColour": "#ffffff",
                                    "FontSize": 60,
                                    "FontColor": "#000079",
                                    "FontFace": {
                                    "Bold": true,
                                    "Italic": false,
                                    "Underline": false
                                    }
                                }]
                        }]
                    }
        """
        timeline4 = """
                    {
                        "VideoTracks": [{
                            "VideoTrackClips": [{
                                
                                "MainTrack": true,
                                "MediaURL": "http://ice-document-materials.oss-cn-shanghai.aliyuncs.com/test_media/h.mp4"
                            }]
                        }],
                        "SubtitleTracks": [{
                                "SubtitleTrackClips": [{
                                    "Effects": [{
                                        "Type": "AI_ASR",
                                        "Font": "AlibabaPuHuiTi",
                                        "Alignment": "TopCenter",
                                        "Y": 910,
                                        "Outline": 10,
                                        "OutlineColour": "#ffffff",
                                        "FontSize": 60,
                                        "FontColor": "#000079",
                                        "FontFace": {
                                        "Bold": true,
                                        "Italic": false,
                                        "Underline": false
                                        }
                                    }]
                                }]
                        }]
                    }
        """


        # 提交剪辑合成作业
        submit_media_producing_job_request = ice20201109_models.SubmitMediaProducingJobRequest()
        
        # projectId, timeline, templateId 有且只有一个非空
        submit_media_producing_job_request.project_id = get_editing_project.project_id
        submit_media_producing_job_request.timeline = timeline4
        submit_media_producing_job_request.output_media_config = "{\"mediaURL\":\"http://krillin-3.oss-cn-shanghai.aliyuncs.com/ice/testOutput6.mp4\",  \
                                                                      \"Width\": 1280, \"Height\": 720}"
        submit_media_producing_job_request.editing_produce_config = "{\"CoverConfig\":{\"StartTime\":2.8}}"

        # 提交视频剪辑
        submit_media_producing_job_response = client.submit_media_producing_job(submit_media_producing_job_request)
        print(submit_media_producing_job_response)
        print('request id:', submit_media_producing_job_response.body.request_id)
        print('project id:', submit_media_producing_job_response.body.project_id)
        print('job id', submit_media_producing_job_response.body.job_id)
if __name__ == '__main__':
    Sample.main()    