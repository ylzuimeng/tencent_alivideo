from flask import Blueprint, render_template, redirect
from models import Template, TaskStyle

pages_bp = Blueprint('pages', __name__)


@pages_bp.route('/')
def index():
    return render_template('upload_videos.html')


@pages_bp.route('/upload/video')
def upload():
    return render_template('upload_videos.html')


@pages_bp.route('/upload/enhanced')
def upload_enhanced():
    return render_template('upload_enhanced.html')


@pages_bp.route('/files')
def files():
    files = Template.query.all()  # Note: using Template model intentionally? Original code used File
    from models import File
    files = File.query.all()
    return render_template('files.html', files=files)


@pages_bp.route('/files/enhanced')
def files_enhanced():
    return render_template('files_enhanced.html')


@pages_bp.route('/task_list')
def task_list():
    return render_template('task_list.html')


@pages_bp.route('/templates')
def templates():
    files = Template.query.all()
    return render_template('templates.html', files=files)


@pages_bp.route('/taskstyles')
def taskstyles():
    files = Template.query.all()
    taskstyles = TaskStyle.query.all()
    return render_template('taskstyles.html', files=files, taskstyles=taskstyles)


@pages_bp.route('/video_templates')
def video_templates():
    return redirect('/templates/unified')


@pages_bp.route('/doctors')
def doctors():
    return render_template('doctors.html')


@pages_bp.route('/templates/unified')
def unified_templates_page():
    return render_template('unified_templates.html')
