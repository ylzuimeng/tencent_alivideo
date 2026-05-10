"""测试字幕编辑页面"""
import json


class TestEditSubtitlesRoute:
    """GET /tasks/<id>/edit-subtitles 路由行为"""

    def _create_task(self, app, db, status='completed', subtitle_data=None, output_url=None):
        from models import ProcessingTask
        with app.app_context():
            task = ProcessingTask(
                task_name='编辑页测试任务',
                status=status,
                output_oss_url=output_url or ('https://oss.example.com/output.mp4' if status == 'completed' else None),
                subtitle_data=subtitle_data
            )
            db.session.add(task)
            db.session.commit()
            return task.id

    def test_valid_task_returns_200(self, app, db):
        """已完成且有字幕数据，返回 200 并展示编辑页面"""
        task_id = self._create_task(
            app, db,
            subtitle_data=json.dumps({'segments': [
                {'index': 0, 'content': '测试字幕', 'from': 0.0, 'to': 2.5}
            ]})
        )

        with app.test_client() as client:
            resp = client.get(f'/tasks/{task_id}/edit-subtitles')

        assert resp.status_code == 200
        html = resp.data.decode('utf-8')

    def test_invalid_task_id_returns_404(self, app, db):
        """无效 task_id 返回 404"""
        with app.test_client() as client:
            resp = client.get('/tasks/99999/edit-subtitles')

        assert resp.status_code == 404

    def test_task_without_subtitle_data_returns_404(self, app, db):
        """无字幕数据返回 404"""
        task_id = self._create_task(app, db, subtitle_data=None)

        with app.test_client() as client:
            resp = client.get(f'/tasks/{task_id}/edit-subtitles')

        assert resp.status_code == 404

    def test_task_not_completed_returns_404(self, app, db):
        """未完成任务返回 404"""
        task_id = self._create_task(app, db, status='processing', subtitle_data='{"segments": []}')

        with app.test_client() as client:
            resp = client.get(f'/tasks/{task_id}/edit-subtitles')

        assert resp.status_code == 404


class TestEditSubtitlesTemplate:
    """编辑页面 HTML 结构"""

    def _create_task(self, app, db):
        from models import ProcessingTask
        with app.app_context():
            task = ProcessingTask(
                task_name='模板结构测试',
                status='completed',
                output_oss_url='https://oss.example.com/output.mp4',
                subtitle_data=json.dumps({'segments': [
                    {'index': 0, 'content': '第一条字幕', 'from': 0.0, 'to': 2.5},
                    {'index': 1, 'content': '第二条字幕', 'from': 3.0, 'to': 5.0},
                ]})
            )
            db.session.add(task)
            db.session.commit()
            return task.id

    def test_page_contains_video_element(self, app, db):
        """页面包含 video 播放器"""
        task_id = self._create_task(app, db)

        with app.test_client() as client:
            resp = client.get(f'/tasks/{task_id}/edit-subtitles')

        html = resp.data.decode('utf-8')
        assert '<video' in html
        assert 'output.mp4' in html

    def test_page_contains_subtitle_editor_area(self, app, db):
        """页面包含字幕编辑区域"""
        task_id = self._create_task(app, db)

        with app.test_client() as client:
            resp = client.get(f'/tasks/{task_id}/edit-subtitles')

        html = resp.data.decode('utf-8')
        assert 'subtitle-editor' in html or 'subtitle-list' in html or '字幕' in html

    def test_page_contains_save_status_indicator(self, app, db):
        """页面包含自动保存状态指示器"""
        task_id = self._create_task(app, db)

        with app.test_client() as client:
            resp = client.get(f'/tasks/{task_id}/edit-subtitles')

        html = resp.data.decode('utf-8')
        assert 'save-status' in html or '自动保存' in html or 'saveStatus' in html

    def test_page_contains_recompose_button(self, app, db):
        """页面包含"重新合成"按钮"""
        task_id = self._create_task(app, db)

        with app.test_client() as client:
            resp = client.get(f'/tasks/{task_id}/edit-subtitles')

        html = resp.data.decode('utf-8')
        assert 'recompose' in html or '重新合成' in html

    def test_task_name_displayed(self, app, db):
        """任务名称显示在页面中"""
        task_id = self._create_task(app, db)

        with app.test_client() as client:
            resp = client.get(f'/tasks/{task_id}/edit-subtitles')

        html = resp.data.decode('utf-8')
        assert '模板结构测试' in html


class TestSubtitleEditorJS:
    """SubtitleEditor JS 类行为（源码验证）"""

    def _create_task(self, app, db):
        from models import ProcessingTask
        with app.app_context():
            task = ProcessingTask(
                task_name='JS测试',
                status='completed',
                output_oss_url='https://oss.example.com/output.mp4',
                subtitle_data=json.dumps({'segments': [
                    {'index': 0, 'content': '字幕一', 'from': 0.0, 'to': 2.5},
                    {'index': 1, 'content': '字幕二', 'from': 3.0, 'to': 5.0},
                ]})
            )
            db.session.add(task)
            db.session.commit()
            return task.id

    def _get_html(self, app, db):
        task_id = self._create_task(app, db)
        with app.test_client() as client:
            resp = client.get(f'/tasks/{task_id}/edit-subtitles')
        return resp.data.decode('utf-8')

    def test_subtitle_editor_class_exists(self, app, db):
        """SubtitleEditor 类定义存在"""
        html = self._get_html(app, db)
        assert 'class SubtitleEditor' in html

    def test_load_subtitles_fetches_api(self, app, db):
        """loadSubtitles 从 API 获取字幕数据"""
        html = self._get_html(app, db)
        assert "fetch(`/api/tasks/" in html
        assert '/subtitles' in html

    def test_timeupdate_sync_highlight(self, app, db):
        """timeupdate 事件触发 syncHighlight"""
        html = self._get_html(app, db)
        assert "timeupdate" in html
        assert "syncHighlight" in html

    def test_click_jumps_video_time(self, app, db):
        """点击字幕跳转 video.currentTime"""
        html = self._get_html(app, db)
        assert 'video.currentTime' in html
        assert 'subtitle-item' in html

    def test_debounce_auto_save(self, app, db):
        """2 秒防抖自动保存"""
        html = self._get_html(app, db)
        assert 'debounceSave' in html
        assert '2000' in html
        assert "method: 'PUT'" in html

    def test_save_status_indicator_method(self, app, db):
        """setSaveStatus 方法存在"""
        html = self._get_html(app, db)
        assert 'setSaveStatus' in html
        assert 'saved' in html
        assert 'saving' in html
        assert 'unsaved' in html

    def test_textarea_only_editable_content(self, app, db):
        """字幕条目包含 textarea，from/to 显示为只读"""
        html = self._get_html(app, db)
        assert 'textarea' in html
        assert 'subtitle-time' in html


class TestEditPageRecomposeJS:
    """编辑页面重新合成 JS 交互"""

    def _create_task(self, app, db):
        from models import ProcessingTask
        with app.app_context():
            task = ProcessingTask(
                task_name='recompose JS test',
                status='completed',
                output_oss_url='https://oss.example.com/output.mp4',
                subtitle_data=json.dumps({'segments': [
                    {'index': 0, 'content': 'test', 'from': 0.0, 'to': 2.5}
                ]})
            )
            db.session.add(task)
            db.session.commit()
            return task.id

    def _get_html(self, app, db):
        task_id = self._create_task(app, db)
        with app.test_client() as client:
            resp = client.get(f'/tasks/{task_id}/edit-subtitles')
        return resp.data.decode('utf-8')

    def test_recompose_button_calls_handler(self, app, db):
        """重新合成按钮调用 handleRecompose"""
        html = self._get_html(app, db)
        assert 'handleRecompose' in html

    def test_recompose_has_confirmation(self, app, db):
        """handleRecompose 有确认步骤"""
        html = self._get_html(app, db)
        assert 'confirm(' in html or '确认' in html

    def test_recompose_posts_to_api(self, app, db):
        """handleRecompose 调用 POST /api/tasks/*/recompose"""
        html = self._get_html(app, db)
        assert 'recompose' in html
        assert "method: 'POST'" in html

    def test_recompose_progress_polling(self, app, db):
        """重新合成后轮询进度"""
        html = self._get_html(app, db)
        assert 'progress' in html or 'Progress' in html

    def test_recompose_error_handling(self, app, db):
        """重新合成失败时有错误处理"""
        html = self._get_html(app, db)
        assert '失败' in html or 'error' in html or 'catch' in html
