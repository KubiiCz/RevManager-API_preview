import os
from typing import Any

from werkzeug.utils import secure_filename
from unidecode import unidecode

from rev_manager import cli

# TODO: Upravit validaci inputu
# TODO: Upravit set path, upravit jestli je přidaná koncovka

'''
Replace CZ chars to ENG equivalents.
Replace whitespace with "-"
'''

def translate_rev_name(revission_name):
    string = unidecode(revission_name)
    return string.replace(" ", "-")


class RevFile:
    def __init__(self):
        self.filename = ''
        self.uploads_dir = ''
        # TODO:Upravit načítání z configu
        #self.root_path = os.path.join(cli.flask_app.instance_path, 'uploads')
        self.root_path = "D:/RevManager/UPLOAD_FILES"
        self.relative_path = ''

    ''' Make relative path to file (Location acc_id, Device acc_id, RevType id)
    eaxample: /999/1/
    '''

    def setRelativePath(self, loc_acc, device_acc):
        self.relative_path = '\\' + str(loc_acc) + '\\' + str(device_acc) + '\\'

    '''
    Save file to file directory
    '''

    def saveFile(self, file, file_type):
        filename = self.filename + "-" + file_type + ".pdf"  # Make filename
        self.uploads_dir = self.root_path + self.relative_path  # Save directory path
        os.makedirs(self.uploads_dir, exist_ok=True)  # Make dir root if not exist
        return file.save(os.path.join(self.uploads_dir, secure_filename(filename=filename)))

    def getRootPath(self):
        return str(self.root_path)