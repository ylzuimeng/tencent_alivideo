from werkzeug.utils import secure_filename
from utils.time_helpers import utcnow


class FileHandler:
    ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'wmv', 'flv', 'mkv'}

    @staticmethod
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in FileHandler.ALLOWED_EXTENSIONS

    @staticmethod
    def generate_oss_path(filename, prefix='uploads'):
        safe_filename = secure_filename(filename)
        timestamp = utcnow().strftime('%Y%m%d_%H%M%S')
        return f'{prefix}/{timestamp}_{safe_filename}'
