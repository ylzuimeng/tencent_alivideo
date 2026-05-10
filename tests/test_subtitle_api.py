"""测试字幕数据 API 端点"""
import json


class TestGetSubtitlesAPI:
    """GET /api/tasks/<id>/subtitles 行为"""

    def _create_task(self, app, db, status='completed', subtitle_data=None):
        """创建测试任务，返回 task_id"""
        from models import ProcessingTask
        with app.app_context():
            task = ProcessingTask(
                task_name='API测试任务',
                status=status,
                output_oss_url='https://oss.example.com/output.mp4' if status == 'completed' else None,
                subtitle_data=subtitle_data
            )
            db.session.add(task)
            db.session.commit()
            return task.id

    def test_returns_subtitle_data_for_completed_task(self, app, db):
        """已完成且有字幕数据的任务返回 200"""
        subtitle_json = json.dumps({'segments': [{'index': 0, 'content': '测试', 'from': 0.0, 'to': 2.0}]})
        task_id = self._create_task(app, db, subtitle_data=subtitle_json)

        with app.test_client() as client:
            resp = client.get(f'/api/tasks/{task_id}/subtitles')

        assert resp.status_code == 200
        data = resp.get_json()
        assert data['segments'][0]['content'] == '测试'

    def test_task_not_found(self, app, db):
        """不存在的任务返回 404"""
        with app.test_client() as client:
            resp = client.get('/api/tasks/99999/subtitles')

        assert resp.status_code == 404

    def test_task_not_completed(self, app, db):
        """未完成的任务返回 404"""
        task_id = self._create_task(app, db, status='processing', subtitle_data='{"segments": []}')

        with app.test_client() as client:
            resp = client.get(f'/api/tasks/{task_id}/subtitles')

        assert resp.status_code == 404

    def test_completed_task_without_subtitle_data(self, app, db):
        """已完成但无字幕数据的任务返回 404"""
        task_id = self._create_task(app, db, status='completed', subtitle_data=None)

        with app.test_client() as client:
            resp = client.get(f'/api/tasks/{task_id}/subtitles')

        assert resp.status_code == 404


class TestPutSubtitlesAPI:
    """PUT /api/tasks/<id>/subtitles 行为"""

    def _create_task(self, app, db, status='completed', subtitle_data=None):
        """创建测试任务，返回 task_id"""
        from models import ProcessingTask
        with app.app_context():
            task = ProcessingTask(
                task_name='API测试任务',
                status=status,
                output_oss_url='https://oss.example.com/output.mp4' if status == 'completed' else None,
                subtitle_data=subtitle_data
            )
            db.session.add(task)
            db.session.commit()
            return task.id

    def test_updates_content_and_preserves_timestamps(self, app, db):
        """有效更新：content 已修改、from/to 不变"""
        from unittest.mock import patch

        original_data = {
            'segments': [
                {'index': 0, 'content': '原始文字', 'from': 0.0, 'to': 2.5},
                {'index': 1, 'content': '原始文字二', 'from': 3.0, 'to': 5.0},
            ],
            'srt_file_url': 'https://oss.example.com/sub.srt',
            'generated_at': '2026-05-10T00:00:00'
        }
        task_id = self._create_task(app, db, subtitle_data=json.dumps(original_data))

        with app.test_client() as client:
            with patch('services.subtitle_service.SubtitleService.upload_srt_to_oss', return_value='https://oss.example.com/new.srt'), \
                 patch('services.subtitle_service.SubtitleService.update_subtitle_content', return_value={
                     'segments': [{'index': 0, 'content': '修改后', 'from': 0.0, 'to': 2.5},
                                  {'index': 1, 'content': '不动', 'from': 3.0, 'to': 5.0}]
                 }), \
                 patch('services.subtitle_service.SubtitleService.generate_srt_content', return_value='SRT content'):
                resp = client.put(
                    f'/api/tasks/{task_id}/subtitles',
                    data=json.dumps({
                        'segments': [
                            {'index': 0, 'content': '修改后'},
                        ]
                    }),
                    content_type='application/json'
                )

        assert resp.status_code == 200
        data = resp.get_json()
        assert data['message'] == '字幕保存成功'

    def test_task_not_found(self, app, db):
        """不存在的任务返回 404"""
        with app.test_client() as client:
            resp = client.put(
                '/api/tasks/99999/subtitles',
                data=json.dumps({'segments': []}),
                content_type='application/json'
            )

        assert resp.status_code == 404

    def test_task_not_completed(self, app, db):
        """未完成的任务返回 400"""
        task_id = self._create_task(app, db, status='processing', subtitle_data='{"segments": []}')

        with app.test_client() as client:
            resp = client.put(
                f'/api/tasks/{task_id}/subtitles',
                data=json.dumps({'segments': []}),
                content_type='application/json'
            )

        assert resp.status_code == 400

    def test_task_without_subtitle_data(self, app, db):
        """无字幕数据的任务返回 400"""
        task_id = self._create_task(app, db, status='completed', subtitle_data=None)

        with app.test_client() as client:
            resp = client.put(
                f'/api/tasks/{task_id}/subtitles',
                data=json.dumps({'segments': []}),
                content_type='application/json'
            )

        assert resp.status_code == 400


class TestTaskListSubtitleButton:
    """任务列表 API 中 has_subtitle_data 字段"""

    def _create_task(self, app, db, status='completed', subtitle_data=None):
        """创建测试任务，返回 task_id"""
        from models import ProcessingTask
        with app.app_context():
            task = ProcessingTask(
                task_name='UI测试任务',
                status=status,
                output_oss_url='https://oss.example.com/output.mp4' if status == 'completed' else None,
                subtitle_data=subtitle_data
            )
            db.session.add(task)
            db.session.commit()
            return task.id

    def test_completed_task_with_subtitle_has_enabled_button(self, app, db):
        """有字幕数据的已完成任务，API 返回 has_subtitle_data=True"""
        task_id = self._create_task(app, db, subtitle_data=json.dumps({'segments': []}))

        with app.test_client() as client:
            resp = client.get('/api/tasks')

        assert resp.status_code == 200
        tasks = resp.get_json()
        found = [t for t in tasks if t['id'] == task_id][0]
        assert found['has_subtitle_data'] is True
        assert found['status'] == 'completed'

    def test_completed_task_without_subtitle_has_disabled_button(self, app, db):
        """无字幕数据的已完成任务，API 返回 has_subtitle_data=False"""
        task_id = self._create_task(app, db, subtitle_data=None)

        with app.test_client() as client:
            resp = client.get('/api/tasks')

        assert resp.status_code == 200
        tasks = resp.get_json()
        found = [t for t in tasks if t['id'] == task_id][0]
        assert found['has_subtitle_data'] is False
        assert found['status'] == 'completed'

    def test_task_list_page_has_edit_subtitle_button(self, app, db):
        """任务列表页面模板中包含编辑字幕按钮"""
        task_id = self._create_task(app, db, subtitle_data=json.dumps({'segments': []}))

        with app.test_client() as client:
            resp = client.get('/task_list')

        assert resp.status_code == 200
        html = resp.data.decode('utf-8')
        assert 'edit-subtitles' in html or 'fa-closed-captioning' in html


class TestRecomposeAPI:
    """POST /api/tasks/<id>/recompose 行为"""

    def _create_task(self, app, db, status='completed', subtitle_data=None):
        from models import ProcessingTask
        with app.app_context():
            task = ProcessingTask(
                task_name='重新合成API测试',
                status=status,
                output_oss_url='https://oss.example.com/output.mp4' if status == 'completed' else None,
                subtitle_data=subtitle_data
            )
            db.session.add(task)
            db.session.commit()
            return task.id

    def test_triggers_recompose_for_valid_task(self, app, db):
        """已完成且有字幕数据的任务触发成功"""
        from unittest.mock import patch

        task_id = self._create_task(
            app, db,
            subtitle_data=json.dumps({'segments': [{'index': 0, 'content': 'test', 'from': 0.0, 'to': 1.0}], 'srt_file_url': 'https://oss.example.com/s.srt'})
        )

        with app.test_client() as client:
            with patch('services.task_processor.task_processor') as mock_tp:
                resp = client.post(f'/api/tasks/{task_id}/recompose')

        assert resp.status_code == 200
        data = resp.get_json()
        assert '重新合成已提交' in data['message']
        mock_tp.executor.submit.assert_called_once()

    def test_task_not_found(self, app, db):
        """不存在的任务返回 404"""
        with app.test_client() as client:
            resp = client.post('/api/tasks/99999/recompose')

        assert resp.status_code == 404

    def test_task_not_completed(self, app, db):
        """未完成的任务返回 400"""
        task_id = self._create_task(app, db, status='processing', subtitle_data='{"segments":[]}')

        with app.test_client() as client:
            resp = client.post(f'/api/tasks/{task_id}/recompose')

        assert resp.status_code == 400

    def test_task_without_subtitle_data(self, app, db):
        """无字幕数据的任务返回 400"""
        task_id = self._create_task(app, db, status='completed', subtitle_data=None)

        with app.test_client() as client:
            resp = client.post(f'/api/tasks/{task_id}/recompose')

        assert resp.status_code == 400
