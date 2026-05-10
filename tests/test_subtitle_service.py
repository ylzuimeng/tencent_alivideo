"""测试字幕相关功能"""
import json
import pytest
from models import ProcessingTask
from utils.time_helpers import utcnow
from unittest.mock import patch, MagicMock, PropertyMock


class TestProcessingTaskSubtitleData:
    """ProcessingTask.subtitle_data 字段行为"""

    def test_subtitle_data_field_exists_and_is_nullable(self, app, db):
        """subtitle_data 字段存在，新建任务时为 None"""
        task = ProcessingTask(
            task_name='测试任务',
            source_file_id=None,
            status='completed'
        )
        db.session.add(task)
        db.session.commit()

        loaded = db.session.get(ProcessingTask, task.id)
        assert loaded.subtitle_data is None

    def test_subtitle_data_stores_json(self, app, db):
        """subtitle_data 可以存储 JSON 字符串"""
        subtitle_json = json.dumps({
            'segments': [
                {'index': 0, 'content': '你好世界', 'from': 0.0, 'to': 2.5}
            ],
            'srt_file_url': 'https://oss.example.com/subtitles/test.srt',
            'generated_at': utcnow().isoformat()
        })

        task = ProcessingTask(
            task_name='测试任务',
            source_file_id=None,
            status='completed',
            subtitle_data=subtitle_json
        )
        db.session.add(task)
        db.session.commit()

        loaded = db.session.get(ProcessingTask, task.id)
        assert loaded.subtitle_data is not None
        data = json.loads(loaded.subtitle_data)
        assert data['segments'][0]['content'] == '你好世界'
        assert data['srt_file_url'] == 'https://oss.example.com/subtitles/test.srt'

    def test_existing_tasks_backward_compatible(self, app, db):
        """已有任务（没有 subtitle_data）仍然可以正常读取"""
        task = ProcessingTask(
            task_name='旧任务',
            source_file_id=None,
            status='completed',
            output_oss_url='https://oss.example.com/old.mp4'
        )
        db.session.add(task)
        db.session.commit()

        loaded = db.session.get(ProcessingTask, task.id)
        assert loaded.output_oss_url == 'https://oss.example.com/old.mp4'
        assert loaded.subtitle_data is None


class TestGenerateSrtContent:
    """SubtitleService.generate_srt_content 行为"""

    def test_converts_single_segment_to_srt(self):
        """单条字幕正确转为 SRT 格式"""
        from services.subtitle_service import SubtitleService

        segments = [
            {'index': 0, 'content': '你好世界', 'from': 0.0, 'to': 2.5}
        ]
        result = SubtitleService.generate_srt_content(segments)

        # SRT 格式：序号、时间轴、内容、空行
        lines = result.strip().split('\n')
        assert lines[0] == '1'
        assert '-->' in lines[1]
        assert lines[2] == '你好世界'

    def test_converts_multiple_segments(self):
        """多条字幕正确编号和分隔"""
        from services.subtitle_service import SubtitleService

        segments = [
            {'index': 0, 'content': '第一句', 'from': 0.0, 'to': 2.0},
            {'index': 1, 'content': '第二句', 'from': 2.5, 'to': 5.0},
            {'index': 2, 'content': '第三句', 'from': 5.5, 'to': 8.0},
        ]
        result = SubtitleService.generate_srt_content(segments)

        blocks = result.strip().split('\n\n')
        assert len(blocks) == 3
        assert '第一句' in blocks[0]
        assert '第二句' in blocks[1]
        assert '第三句' in blocks[2]
        # 序号正确
        assert blocks[1].startswith('2')

    def test_srt_timestamp_format(self):
        """SRT 时间戳格式为 HH:MM:SS,mmm"""
        from services.subtitle_service import SubtitleService

        segments = [
            {'index': 0, 'content': 'test', 'from': 1.5, 'to': 65.123}
        ]
        result = SubtitleService.generate_srt_content(segments)

        lines = result.strip().split('\n')
        timestamp_line = lines[1]
        parts = timestamp_line.split(' --> ')
        assert len(parts) == 2
        # 格式：00:00:01,500 --> 00:01:05,123
        assert parts[0] == '00:00:01,500'
        assert parts[1] == '00:01:05,123'

    def test_empty_segments_returns_empty(self):
        """空 segments 返回空字符串"""
        from services.subtitle_service import SubtitleService

        result = SubtitleService.generate_srt_content([])
        assert result == ''

    def test_long_text_segment(self):
        """超长文本正常处理"""
        from services.subtitle_service import SubtitleService

        long_text = '这是一段很长的字幕内容' * 50
        segments = [
            {'index': 0, 'content': long_text, 'from': 0.0, 'to': 10.0}
        ]
        result = SubtitleService.generate_srt_content(segments)
        assert long_text in result


class TestParseSubtitleData:
    """SubtitleService.parse_subtitle_data 行为"""

    def test_parses_valid_json(self):
        """正常 JSON 字符串正确解析"""
        from services.subtitle_service import SubtitleService

        subtitle_json = json.dumps({
            'segments': [{'index': 0, 'content': 'test', 'from': 0.0, 'to': 1.0}],
            'srt_file_url': 'https://oss.example.com/test.srt'
        })
        result = SubtitleService.parse_subtitle_data(subtitle_json)

        assert result is not None
        assert result['segments'][0]['content'] == 'test'
        assert result['srt_file_url'] == 'https://oss.example.com/test.srt'

    def test_returns_none_for_none_input(self):
        """None 输入返回 None"""
        from services.subtitle_service import SubtitleService

        assert SubtitleService.parse_subtitle_data(None) is None

    def test_returns_none_for_empty_string(self):
        """空字符串返回 None"""
        from services.subtitle_service import SubtitleService

        assert SubtitleService.parse_subtitle_data('') is None

    def test_returns_none_for_invalid_json(self):
        """无效 JSON 返回 None"""
        from services.subtitle_service import SubtitleService

        assert SubtitleService.parse_subtitle_data('not json') is None

    def test_returns_none_for_non_dict_json(self):
        """非字典类型的 JSON（如数组）返回 None"""
        from services.subtitle_service import SubtitleService

        assert SubtitleService.parse_subtitle_data('[1,2,3]') is None


class TestUpdateSubtitleContent:
    """SubtitleService.update_subtitle_content 行为"""

    def _make_subtitle_data(self):
        return {
            'segments': [
                {'index': 0, 'content': '原始文字一', 'from': 0.0, 'to': 2.5},
                {'index': 1, 'content': '原始文字二', 'from': 3.0, 'to': 5.5},
                {'index': 2, 'content': '原始文字三', 'from': 6.0, 'to': 8.0},
            ],
            'srt_file_url': 'https://oss.example.com/test.srt',
            'generated_at': '2026-05-10T00:00:00'
        }

    def test_updates_only_content(self):
        """仅更新 content 字段"""
        from services.subtitle_service import SubtitleService

        data = self._make_subtitle_data()
        updated = SubtitleService.update_subtitle_content(data, [
            {'index': 0, 'content': '修改后的文字'},
            {'index': 2, 'content': '也是修改后的'},
        ])

        assert updated['segments'][0]['content'] == '修改后的文字'
        assert updated['segments'][2]['content'] == '也是修改后的'
        # 未修改的保持不变
        assert updated['segments'][1]['content'] == '原始文字二'

    def test_preserves_timestamps(self):
        """from/to 时间戳保持不变"""
        from services.subtitle_service import SubtitleService

        data = self._make_subtitle_data()
        updated = SubtitleService.update_subtitle_content(data, [
            {'index': 0, 'content': '修改'},
        ])

        assert updated['segments'][0]['from'] == 0.0
        assert updated['segments'][0]['to'] == 2.5

    def test_preserves_metadata(self):
        """srt_file_url 等元数据保持不变"""
        from services.subtitle_service import SubtitleService

        data = self._make_subtitle_data()
        updated = SubtitleService.update_subtitle_content(data, [
            {'index': 0, 'content': '修改'},
        ])

        assert updated['srt_file_url'] == 'https://oss.example.com/test.srt'
        assert updated['generated_at'] == '2026-05-10T00:00:00'


class TestUploadSrtToOss:
    """SubtitleService.upload_srt_to_oss 行为"""

    def test_uploads_srt_and_returns_url(self):
        """上传 SRT 内容并返回 OSS URL"""
        from services.subtitle_service import SubtitleService
        from unittest.mock import patch, MagicMock

        mock_client = MagicMock()
        mock_config = MagicMock()
        mock_config.get_file_url.return_value = 'https://test-bucket.oss-cn-shanghai.aliyuncs.com/subtitles/42_20260510.srt'

        with patch('services.oss_service.OSSConfig', return_value=mock_config), \
             patch('services.oss_service.OSSClient', return_value=mock_client):
            url = SubtitleService.upload_srt_to_oss('1\n00:00:00,000 --> 00:00:02,500\n你好\n', 42)

        assert url.startswith('https://test-bucket')
        assert '/subtitles/' in url
        mock_client.upload_file.assert_called_once()

        # 验证上传的是 bytes
        call_args = mock_client.upload_file.call_args
        assert isinstance(call_args[0][0], bytes)


class TestICESubtitleJob:
    """ICEClient 字幕作业方法行为"""

    def _make_ice_client(self):
        """创建 mock ICEClient 实例（跳过真实连接）"""
        from services.ice_service import ICEClient
        with patch.object(ICEClient, '_create_client', return_value=MagicMock()):
            return ICEClient()

    def test_submit_subtitle_job_returns_job_info(self):
        """submit_subtitle_job 返回 job_id 和 request_id"""
        client = self._make_ice_client()

        mock_response = MagicMock()
        mock_response.body.job_id = 'job-123'
        mock_response.body.request_id = 'req-456'
        client.client.submit_asrjob.return_value = mock_response

        result = client.submit_subtitle_job('https://oss.example.com/video.mp4')

        assert result is not None
        assert result['job_id'] == 'job-123'
        assert result['request_id'] == 'req-456'

        # 验证调用的是 submit_asrjob
        client.client.submit_asrjob.assert_called_once()

    def test_query_subtitle_job_result_returns_segments(self):
        """query_subtitle_job_result 解析 AiResult 为 segments 数组"""
        client = self._make_ice_client()

        # 模拟 ICE GetSmartHandleJob 返回结果
        ai_result = json.dumps([
            {'content': '第一句话', 'from': 0.0, 'to': 2.5},
            {'content': '第二句话', 'from': 3.0, 'to': 5.0},
        ])
        mock_response = MagicMock()
        mock_response.body.to_map.return_value = {
            'State': 'Finished',
            'JobResult': {'AiResult': ai_result}
        }
        client.client.get_smart_handle_job.return_value = mock_response

        segments = client.query_subtitle_job_result('job-123')

        assert len(segments) == 2
        assert segments[0]['content'] == '第一句话'
        assert segments[0]['from'] == 0.0
        assert segments[0]['to'] == 2.5
        assert segments[1]['content'] == '第二句话'

    def test_query_subtitle_job_result_returns_none_on_failure(self):
        """查询失败时返回 None"""
        client = self._make_ice_client()
        client.client.get_smart_handle_job.side_effect = Exception('ICE error')

        result = client.query_subtitle_job_result('job-bad')
        assert result is None


class TestExtractSubtitles:
    """TaskProcessor._extract_subtitles 行为"""

    def _create_completed_task(self, db):
        """创建一个已完成的任务"""
        task = ProcessingTask(
            task_name='字幕提取测试',
            status='completed',
            output_oss_url='https://oss.example.com/output.mp4'
        )
        db.session.add(task)
        db.session.commit()
        return task

    def test_extracts_subtitles_and_writes_subtitle_data(self, app, db):
        """成功提取字幕后 subtitle_data 被正确写入"""
        from services.task_processor import TaskProcessor
        from services.subtitle_service import SubtitleService

        with app.app_context():
            task = self._create_completed_task(db)
            task_id = task.id
            processor = TaskProcessor()

            mock_segments = [
                {'index': 0, 'content': '你好', 'from': 0.0, 'to': 2.0},
            ]

            with patch('services.task_processor.ICEClient') as MockICE, \
                 patch.object(SubtitleService, 'upload_srt_to_oss', return_value='https://oss.example.com/sub.srt'):
                mock_ice = MockICE.return_value
                mock_ice.submit_subtitle_job.return_value = {'job_id': 'sub-job-1'}
                mock_ice.query_subtitle_job_result.return_value = mock_segments

                processor._extract_subtitles(task)

            # 验证 subtitle_data 已写入
            loaded = db.session.get(ProcessingTask, task_id)
            assert loaded.subtitle_data is not None
            data = json.loads(loaded.subtitle_data)
            assert data['segments'][0]['content'] == '你好'
            assert data['srt_file_url'] == 'https://oss.example.com/sub.srt'

    def test_extraction_failure_does_not_affect_task_status(self, app, db):
        """字幕提取失败时任务状态仍为 completed"""
        from services.task_processor import TaskProcessor

        with app.app_context():
            task = self._create_completed_task(db)
            task_id = task.id
            processor = TaskProcessor()

            with patch('services.task_processor.ICEClient') as MockICE:
                mock_ice = MockICE.return_value
                mock_ice.submit_subtitle_job.side_effect = Exception('ICE 连接失败')

                processor._extract_subtitles(task)

            # 任务状态仍为 completed，subtitle_data 为 None
            loaded = db.session.get(ProcessingTask, task_id)
            assert loaded.status == 'completed'
            assert loaded.subtitle_data is None


class TestGetAllTasksHasSubtitleData:
    """get_all_tasks 返回 has_subtitle_data 字段"""

    def test_has_subtitle_data_true(self, app, db):
        """有字幕数据的任务，has_subtitle_data 为 True"""
        from services.task_processor import TaskProcessor

        with app.app_context():
            task = ProcessingTask(
                task_name='有字幕的任务',
                status='completed',
                subtitle_data=json.dumps({'segments': [{'index': 0, 'content': 'test', 'from': 0.0, 'to': 1.0}]})
            )
            db.session.add(task)
            db.session.commit()

            processor = TaskProcessor()
            tasks = processor.get_all_tasks()

            assert len(tasks) > 0
            found = [t for t in tasks if t['id'] == task.id][0]
            assert found['has_subtitle_data'] is True

    def test_has_subtitle_data_false(self, app, db):
        """无字幕数据的任务，has_subtitle_data 为 False"""
        from services.task_processor import TaskProcessor

        with app.app_context():
            task = ProcessingTask(
                task_name='无字幕的任务',
                status='completed'
            )
            db.session.add(task)
            db.session.commit()

            processor = TaskProcessor()
            tasks = processor.get_all_tasks()

            found = [t for t in tasks if t['id'] == task.id][0]
            assert found['has_subtitle_data'] is False


class TestBuildSubtitleTimeline:
    """SubtitleService.build_subtitle_timeline 行为"""

    def _make_timeline(self):
        return {
            "VideoTracks": [{
                "VideoTrackClips": [
                    {"MediaURL": "https://oss.example.com/header.mp4"},
                    {"MediaURL": "https://oss.example.com/main.mp4", "MainTrack": True},
                ]
            }],
            "AudioTracks": [{
                "AudioTrackClips": [
                    {"MediaURL": "https://oss.example.com/audio.mp3"}
                ]
            }],
            "SubtitleTracks": [{
                "SubtitleTrackClips": [
                    {"Type": "Text", "Text": "旧字幕", "X": 0.1, "Y": 0.9}
                ]
            }]
        }

    def test_preserves_video_tracks(self):
        """VideoTracks 保持不变"""
        from services.subtitle_service import SubtitleService

        timeline = self._make_timeline()
        result = SubtitleService.build_subtitle_timeline(
            json.dumps(timeline, ensure_ascii=False),
            'https://oss.example.com/sub.srt'
        )
        result_obj = json.loads(result)

        assert result_obj['VideoTracks'] == timeline['VideoTracks']

    def test_preserves_audio_tracks(self):
        """AudioTracks 保持不变"""
        from services.subtitle_service import SubtitleService

        timeline = self._make_timeline()
        result = SubtitleService.build_subtitle_timeline(
            json.dumps(timeline, ensure_ascii=False),
            'https://oss.example.com/sub.srt'
        )
        result_obj = json.loads(result)

        assert result_obj['AudioTracks'] == timeline['AudioTracks']

    def test_replaces_subtitle_tracks_with_srt(self):
        """SubtitleTracks 被替换为基于 SRT 的引用轨道"""
        from services.subtitle_service import SubtitleService

        timeline = self._make_timeline()
        result = SubtitleService.build_subtitle_timeline(
            json.dumps(timeline, ensure_ascii=False),
            'https://oss.example.com/sub.srt'
        )
        result_obj = json.loads(result)

        new_subtitle = result_obj['SubtitleTracks']
        assert len(new_subtitle) == 1
        clip = new_subtitle[0]['SubtitleTrackClips'][0]
        assert clip['Type'] == 'Subtitle'
        assert clip['SubtitleURL'] == 'https://oss.example.com/sub.srt'

    def test_handles_timeline_without_subtitle_tracks(self):
        """原始 Timeline 无 SubtitleTracks 时新增"""
        from services.subtitle_service import SubtitleService

        timeline = {
            "VideoTracks": [{"VideoTrackClips": [{"MediaURL": "https://oss.example.com/v.mp4"}]}]
        }
        result = SubtitleService.build_subtitle_timeline(
            json.dumps(timeline, ensure_ascii=False),
            'https://oss.example.com/sub.srt'
        )
        result_obj = json.loads(result)

        assert 'SubtitleTracks' in result_obj
        assert result_obj['SubtitleTracks'][0]['SubtitleTrackClips'][0]['SubtitleURL'] == 'https://oss.example.com/sub.srt'

    def test_handles_timeline_without_audio_tracks(self):
        """原始 Timeline 无 AudioTracks 正常处理"""
        from services.subtitle_service import SubtitleService

        timeline = {
            "VideoTracks": [{"VideoTrackClips": [{"MediaURL": "https://oss.example.com/v.mp4"}]}]
        }
        result = SubtitleService.build_subtitle_timeline(
            json.dumps(timeline, ensure_ascii=False),
            'https://oss.example.com/sub.srt'
        )
        result_obj = json.loads(result)

        assert 'VideoTracks' in result_obj


class TestRecomposePipeline:
    """TaskProcessor.recompose_with_subtitles 行为"""

    def _create_task(self, app, db):
        from models import ProcessingTask
        with app.app_context():
            task = ProcessingTask(
                task_name='重新合成测试',
                status='completed',
                output_oss_url='https://oss.example.com/old_output.mp4',
                subtitle_data=json.dumps({
                    'segments': [{'index': 0, 'content': '更新后的字幕', 'from': 0.0, 'to': 2.0}],
                    'srt_file_url': 'https://oss.example.com/updated.srt'
                })
            )
            db.session.add(task)
            db.session.commit()
            return task.id

    def test_updates_output_oss_url_after_recompose(self, app, db):
        """重新合成后 output_oss_url 更新为新视频地址"""
        from services.task_processor import TaskProcessor
        from unittest.mock import patch

        task_id = self._create_task(app, db)
        processor = TaskProcessor()

        with patch.object(processor, 'get_app_context', return_value=app.app_context()), \
             patch('services.task_processor.ICEClient') as MockICE, \
             patch('services.subtitle_service.SubtitleService.build_subtitle_timeline', return_value='{"VideoTracks":[]}'), \
             patch('services.oss_service.OSSClient.delete_file', return_value=True):
            mock_ice = MockICE.return_value
            mock_ice.submit_editing_job.return_value = {'job_id': 'recompose-job-1', 'project_id': 'proj-1'}
            mock_ice.query_job_status.return_value = {
                'status': 'completed',
                'progress': 100,
                'output_url': 'https://oss.example.com/new_output.mp4'
            }

            processor.recompose_with_subtitles(task_id)

        with app.app_context():
            updated = db.session.get(ProcessingTask, task_id)
            assert updated.output_oss_url == 'https://oss.example.com/new_output.mp4'

    def test_deletes_old_oss_file_after_recompose(self, app, db):
        """重新合成后删除旧 OSS 输出文件"""
        from services.task_processor import TaskProcessor
        from unittest.mock import patch

        task_id = self._create_task(app, db)
        processor = TaskProcessor()

        with patch.object(processor, 'get_app_context', return_value=app.app_context()), \
             patch('services.task_processor.ICEClient') as MockICE, \
             patch('services.subtitle_service.SubtitleService.build_subtitle_timeline', return_value='{"VideoTracks":[]}'), \
             patch('services.oss_service.OSSClient.delete_file') as mock_delete:
            mock_ice = MockICE.return_value
            mock_ice.submit_editing_job.return_value = {'job_id': 'recompose-job-2', 'project_id': 'proj-2'}
            mock_ice.query_job_status.return_value = {
                'status': 'completed', 'progress': 100,
                'output_url': 'https://oss.example.com/new_output.mp4'
            }

            processor.recompose_with_subtitles(task_id)

            mock_delete.assert_called_once()
            call_args = mock_delete.call_args[0][0]
            assert 'old_output' in call_args

    def test_old_file_deletion_failure_does_not_affect_result(self, app, db):
        """旧文件删除失败不影响重新合成结果"""
        from services.task_processor import TaskProcessor
        from unittest.mock import patch

        task_id = self._create_task(app, db)
        processor = TaskProcessor()

        with patch.object(processor, 'get_app_context', return_value=app.app_context()), \
             patch('services.task_processor.ICEClient') as MockICE, \
             patch('services.subtitle_service.SubtitleService.build_subtitle_timeline', return_value='{"VideoTracks":[]}'), \
             patch('services.oss_service.OSSClient.delete_file', side_effect=Exception('OSS delete failed')):
            mock_ice = MockICE.return_value
            mock_ice.submit_editing_job.return_value = {'job_id': 'recompose-job-3', 'project_id': 'proj-3'}
            mock_ice.query_job_status.return_value = {
                'status': 'completed', 'progress': 100,
                'output_url': 'https://oss.example.com/new_output.mp4'
            }

            processor.recompose_with_subtitles(task_id)

        with app.app_context():
            updated = db.session.get(ProcessingTask, task_id)
            assert updated.output_oss_url == 'https://oss.example.com/new_output.mp4'
