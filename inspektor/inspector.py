import os
import stat

PY_EXTENSIONS = ['.py']
SHEBANG = '#!'

class PathInspector(object):
    def __init__(self, path):
        self.path = path

    def _get_first_line(self):
        first_line = ""
        if os.path.isfile(self.path):
            checked_file = open(self.path, "r")
            first_line = checked_file.readline()
            checked_file.close()
        return first_line

    def has_exec_permission(self):
        mode = os.stat(self.path)[stat.ST_MODE]
        return mode & stat.S_IXUSR

    def is_script(self, language=None):
        first_line = self._get_first_line()
        if first_line:
            if first_line.startswith(SHEBANG):
                if language is None:
                    return True
                elif language in first_line:
                    return True
        return False

    def is_python(self):
        for extension in PY_EXTENSIONS:
            if self.path.endswith(extension):
                return True

        return self.is_script(language='python')
