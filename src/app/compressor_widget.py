# compressor_widget.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QRadioButton, QCheckBox, 
                               QFileDialog, QMessageBox, QHBoxLayout, QGridLayout, QApplication)
import os
import subprocess
import json
import hashlib
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

LANG = {
    'en': {
        'switch_language': "Switch Language",
        'success': "Success",
        'error': "Error",
        'file_compressed': "File {file_path} compressed into {archive_name}",
        'file_split_compressed': "File {file_path} is too large, split and compressed into {archive_path} with {part_count} parts",
        'failed_compress': "Failed to compress {file_path} with error: {error}",
        'failed_copy': "Failed to copy {file_path} due to {error}",
        'select_input': "Please select an input file or directory.",
        'output_dir_not_exist': "Output directory does not exist.",
        'input_file': "Input File",
        'input_directory': "Input Directory",
        'output_directory': "Output Directory:",
        'size_threshold': "Size Threshold (MB):",
        'large_volume_size': "Large Volume Size (MB):",
        'small_volume_size': "Small Volume Size (MB):",
        'compress_subdirs': "Compress Each Subdirectory Separately",
        'small_file_action': "Action for Small Files:",
        'compress': "Compress",
        'split_compress': "Split and Compress",
        'password': "Password (Optional):",
        'compression_level': "Compression Level (0-9):",
        'start': "Start"
    },
    'zh': {
        'switch_language': "切换语言",
        'success': "成功",
        'error': "错误",
        'file_compressed': "文件 {file_path} 压缩到 {archive_name}",
        'file_split_compressed': "文件 {file_path} 太大，分割并压缩到 {archive_path}，共 {part_count} 个部分",
        'failed_compress': "压缩 {file_path} 失败，错误: {error}",
        'failed_copy': "复制 {file_path} 失败，错误: {error}",
        'select_input': "请选择一个输入文件或目录。",
        'output_dir_not_exist': "输出目录不存在。",
        'input_file': "输入文件",
        'input_directory': "输入目录",
        'output_directory': "输出目录:",
        'size_threshold': "大小阈值 (MB):",
        'large_volume_size': "大卷大小 (MB):",
        'small_volume_size': "小卷大小 (MB):",
        'compress_subdirs': "单独压缩每个子目录",
        'small_file_action': "小文件的操作:",
        'compress': "压缩",
        'split_compress': "分割并压缩",
        'password': "密码 (可选):",
        'compression_level': "压缩级别 (0-9):",
        'start': "开始"
    }
}

current_lang = 'en'

def localize(key, **kwargs):
    return LANG[current_lang].get(key, key).format(**kwargs)

class CompressorWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.setWindowTitle(localize('File or Directory Split and Compress'))
        
        layout = QVBoxLayout(self)

        # Radio buttons for selecting file or directory
        self.rb_file = QRadioButton(localize('input_file'))
        self.rb_dir = QRadioButton(localize('input_directory'))
        self.rb_file.setChecked(True)
        self.rb_file.toggled.connect(self.enable_file_selection)
        self.rb_dir.toggled.connect(self.enable_directory_selection)

        layout.addWidget(self.rb_file)
        layout.addWidget(self.rb_dir)

        # Input fields for file, directory and output directory
        self.entry_file_path = QLineEdit(self)
        self.btn_browse_file = QPushButton("Browse", self)
        self.btn_browse_file.clicked.connect(self.select_file)

        self.entry_dir_path = QLineEdit(self)
        self.entry_dir_path.setDisabled(True)
        self.btn_browse_dir = QPushButton("Browse", self)
        self.btn_browse_dir.clicked.connect(self.select_directory)
        self.btn_browse_dir.setDisabled(True)

        self.entry_output_dir = QLineEdit(self)
        self.btn_browse_output = QPushButton("Browse", self)
        self.btn_browse_output.clicked.connect(self.select_output_dir)

        layout.addWidget(QLabel(localize('input_file')))
        layout.addWidget(self.entry_file_path)
        layout.addWidget(self.btn_browse_file)
        layout.addWidget(QLabel(localize('input_directory')))
        layout.addWidget(self.entry_dir_path)
        layout.addWidget(self.btn_browse_dir)
        layout.addWidget(QLabel(localize('output_directory')))
        layout.addWidget(self.entry_output_dir)
        layout.addWidget(self.btn_browse_output)

        # Other input fields and options
        self.entry_size_threshold = QLineEdit(self)
        self.entry_size_threshold.setText("25")
        self.entry_large_volume_size = QLineEdit(self)
        self.entry_large_volume_size.setText("25")
        self.entry_small_volume_size = QLineEdit(self)
        self.entry_small_volume_size.setText("25")
        self.entry_password = QLineEdit(self)
        self.entry_password.setEchoMode(QLineEdit.Password)
        self.entry_compression_level = QLineEdit(self)
        self.entry_compression_level.setText("1")

        layout.addWidget(QLabel(localize('size_threshold')))
        layout.addWidget(self.entry_size_threshold)
        layout.addWidget(QLabel(localize('large_volume_size')))
        layout.addWidget(self.entry_large_volume_size)
        layout.addWidget(QLabel(localize('small_volume_size')))
        layout.addWidget(self.entry_small_volume_size)
        layout.addWidget(QLabel(localize('password')))
        layout.addWidget(self.entry_password)
        layout.addWidget(QLabel(localize('compression_level')))
        layout.addWidget(self.entry_compression_level)

        # Checkbox and radio buttons for additional options
        self.chk_include_subdirs = QCheckBox(localize('compress_subdirs'))
        self.rb_compress = QRadioButton(localize('compress'))
        self.rb_split_compress = QRadioButton(localize('split_compress'))
        self.rb_compress.setChecked(True)

        layout.addWidget(self.chk_include_subdirs)
        layout.addWidget(QLabel(localize('small_file_action')))
        layout.addWidget(self.rb_compress)
        layout.addWidget(self.rb_split_compress)

        # Start button
        self.btn_start = QPushButton(localize('start'), self)
        self.btn_start.clicked.connect(self.start_processing)
        layout.addWidget(self.btn_start)

        self.setLayout(layout)

    def select_file(self):
        file_path = QFileDialog.getOpenFileName(self, "Select File")[0]
        if file_path:
            self.entry_file_path.setText(file_path)

    def select_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if dir_path:
            self.entry_dir_path.setText(dir_path)

    def select_output_dir(self):
        output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if output_dir:
            self.entry_output_dir.setText(output_dir)

    def enable_file_selection(self):
        self.entry_file_path.setEnabled(True)
        self.btn_browse_file.setEnabled(True)
        self.entry_dir_path.setDisabled(True)
        self.btn_browse_dir.setDisabled(True)
        self.entry_dir_path.clear()

    def enable_directory_selection(self):
        self.entry_dir_path.setEnabled(True)
        self.btn_browse_dir.setEnabled(True)
        self.entry_file_path.setDisabled(True)
        self.btn_browse_file.setDisabled(True)
        self.entry_file_path.clear()

    def start_processing(self):
        file_path = self.entry_file_path.text()
        dir_path = self.entry_dir_path.text()
        output_dir = self.entry_output_dir.text()
        size_threshold = int(self.entry_size_threshold.text()) * 1024 * 1024
        large_volume_size = int(self.entry_large_volume_size.text()) * 1024 * 1024
        small_volume_size = int(self.entry_small_volume_size.text()) * 1024 * 1024
        include_subdirs = self.chk_include_subdirs.isChecked()
        small_file_action = "compress" if self.rb_compress.isChecked() else "split_compress"
        password = self.entry_password.text()
        compression_level = int(self.entry_compression_level.text())

        if not file_path and not dir_path:
            QMessageBox.critical(self, localize('error'), localize('select_input'))
            return

        if not output_dir or not os.path.exists(output_dir):
            QMessageBox.critical(self, localize('error'), localize('output_dir_not_exist'))
            return

        if file_path:
            self.copy_file(file_path, output_dir, size_threshold, large_volume_size, small_volume_size, small_file_action, password, compression_level)
        elif dir_path:
            self.process_directory(dir_path, output_dir, size_threshold, large_volume_size, small_volume_size, include_subdirs, small_file_action, password, compression_level)

    # The rest of the functions (calculate_md5, get_directory_size, split_and_compress_file, compress_file, process_directory, copy_file) remain unchanged
    def calculate_md5(file_path, chunk_size=8192):
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(chunk_size), b""):
                    hash_md5.update(chunk)
        except Exception as e:
            logging.error(f"Failed to calculate MD5 for {file_path}: {e}")
        return hash_md5.hexdigest()

    def get_directory_size(directory):
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(directory):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    total_size += os.path.getsize(fp)
        except Exception as e:
            logging.error(f"Failed to get directory size for {directory}: {e}")
        return total_size

    def split_and_compress_file(file_path, output_dir, volume_size, password=None, compression_level=1):
        base_name = os.path.basename(file_path)
        os.makedirs(output_dir, exist_ok=True)
        archive_path = os.path.join(output_dir, base_name)
        archive_name = os.path.join(archive_path, base_name + ".7z")
        try:
            volume_size_mb = volume_size // (1024 * 1024)
            zip_command = [
                '7z','a', '-md=192m', '-v{}m'.format(volume_size_mb), '-mx={}'.format(compression_level), archive_name, file_path
            ]
            if password:
                zip_command[2:2] = ['-p{}'.format(password), '-mhe']

            subprocess.run(zip_command, check=True)
            part_file_paths = [os.path.join(archive_path, f) for f in os.listdir(archive_path) if f.startswith(base_name)]

            info_path = os.path.join(archive_path, "info.json")
            info_data = {
                "original_file_path": file_path,
                "original_file_size": os.path.getsize(file_path),
                "part_count": len(part_file_paths),
                "parts": [{"part_number": i+1, "part_size": os.path.getsize(part_file)} for i, part_file in enumerate(part_file_paths)]
            }
            with open(info_path, 'w') as info_file:
                json.dump(info_data, info_file, indent=4)

            logging.info(localize('file_split_compressed', file_path=file_path, archive_path=archive_path, part_count=len(part_file_paths)))
        except subprocess.CalledProcessError as e:
            logging.error(localize('failed_compress', file_path=file_path, error=e))

    def compress_file(file_path, output_dir, password=None, compression_level=1):
        base_name = os.path.basename(file_path)
        archive_name = os.path.join(output_dir, base_name + ".7z")
        try:
            zip_command = ['7z', 'a', '-md=192m', '-mx={}'.format(compression_level), archive_name, file_path]
            if password:
                zip_command[2:2] = ['-p{}'.format(password), '-mhe']

            subprocess.run(zip_command, check=True)
            logging.info(localize('file_compressed', file_path=file_path, archive_name=archive_name))
        except subprocess.CalledProcessError as e:
            logging.error(localize('failed_compress', file_path=file_path, error=e))

    def process_directory(directory, output_dir, size_threshold, large_volume_size, small_volume_size, include_subdirs, small_file_action, password, compression_level):
        try:
            if include_subdirs:
                for root, dirs, files in os.walk(directory):
                    if root == directory:
                        for d in dirs:
                            dir_path = os.path.join(root, d)
                            dir_size = get_directory_size(dir_path)
                            if dir_size > size_threshold:
                                split_and_compress_file(dir_path, output_dir, large_volume_size, password, compression_level)
                            else:
                                if small_file_action == "compress":
                                    compress_file(dir_path, output_dir, password, compression_level)
                                else:
                                    split_and_compress_file(dir_path, output_dir, small_volume_size, password, compression_level)
                        break
            else:
                dir_size = get_directory_size(directory)
                if dir_size > size_threshold:
                    split_and_compress_file(directory, output_dir, large_volume_size, password, compression_level)
                else:
                    if small_file_action == "compress":
                        compress_file(directory, output_dir, password, compression_level)
                    else:
                        split_and_compress_file(directory, output_dir, small_volume_size, password, compression_level)
        except Exception as e:
            logging.error(f"Failed to process directory {directory}: {e}")

    def copy_file(file_path, output_dir, size_threshold, large_volume_size, small_volume_size, small_file_action, password, compression_level):
        try:
            file_size = os.path.getsize(file_path)
            if file_size > size_threshold:
                split_and_compress_file(file_path, output_dir, large_volume_size, password, compression_level)
            else:
                if small_file_action == "compress":
                    compress_file(file_path, output_dir, password, compression_level)
                else:
                    split_and_compress_file(file_path, output_dir, small_volume_size, password, compression_level)
            return True
        except Exception as e:
            logging.error(localize('failed_copy', file_path=file_path, error=e))
            return False

def get_directory_size(directory):
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(directory):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
    except Exception as e:
        logging.error(f"Failed to get directory size for {directory}: {e}")
    return total_size

def split_and_compress_file(file_path, output_dir, volume_size, password=None, compression_level=1):
    base_name = os.path.basename(file_path)
    os.makedirs(output_dir, exist_ok=True)
    archive_path = os.path.join(output_dir, base_name)
    archive_name = os.path.join(archive_path, base_name + ".7z")
    try:
        volume_size_mb = volume_size // (1024 * 1024)
        zip_command = [
            '7z','a', '-md=192m', '-v{}m'.format(volume_size_mb), '-mx={}'.format(compression_level), archive_name, file_path
        ]
        if password:
            zip_command[2:2] = ['-p{}'.format(password), '-mhe']
        
        subprocess.run(zip_command, check=True)
        part_file_paths = [os.path.join(archive_path, f) for f in os.listdir(archive_path) if f.startswith(base_name)]

        info_path = os.path.join(archive_path, "info.json")
        info_data = {
            "original_file_path": file_path,
            "original_file_size": os.path.getsize(file_path),
            "part_count": len(part_file_paths),
            "parts": [{"part_number": i+1, "part_size": os.path.getsize(part_file)} for i, part_file in enumerate(part_file_paths)]
        }
        with open(info_path, 'w') as info_file:
            json.dump(info_data, info_file, indent=4)

        logging.info(localize('file_split_compressed', file_path=file_path, archive_path=archive_path, part_count=len(part_file_paths)))
    except subprocess.CalledProcessError as e:
        logging.error(localize('failed_compress', file_path=file_path, error=e))

def compress_file(file_path, output_dir, password=None, compression_level=1):
    base_name = os.path.basename(file_path)
    archive_name = os.path.join(output_dir, base_name + ".7z")
    try:
        zip_command = ['7z', 'a', '-md=192m', '-mx={}'.format(compression_level), archive_name, file_path]
        if password:
            zip_command[2:2] = ['-p{}'.format(password), '-mhe']
        
        subprocess.run(zip_command, check=True)
        logging.info(localize('file_compressed', file_path=file_path, archive_name=archive_name))
    except subprocess.CalledProcessError as e:
        logging.error(localize('failed_compress', file_path=file_path, error=e))

def process_directory(directory, output_dir, size_threshold, large_volume_size, small_volume_size, include_subdirs, small_file_action, password, compression_level):
    try:
        if include_subdirs:
            for root, dirs, files in os.walk(directory):
                if root == directory:
                    for d in dirs:
                        dir_path = os.path.join(root, d)
                        dir_size = get_directory_size(dir_path)
                        if dir_size > size_threshold:
                            split_and_compress_file(dir_path, output_dir, large_volume_size, password, compression_level)
                        else:
                            if small_file_action == "compress":
                                compress_file(dir_path, output_dir, password, compression_level)
                            else:
                                split_and_compress_file(dir_path, output_dir, small_volume_size, password, compression_level)
                    break
        else:
            dir_size = get_directory_size(directory)
            if dir_size > size_threshold:
                split_and_compress_file(directory, output_dir, large_volume_size, password, compression_level)
            else:
                if small_file_action == "compress":
                    compress_file(directory, output_dir, password, compression_level)
                else:
                    split_and_compress_file(directory, output_dir, small_volume_size, password, compression_level)
    except Exception as e:
        logging.error(f"Failed to process directory {directory}: {e}")

def copy_file(file_path, output_dir, size_threshold, large_volume_size, small_volume_size, small_file_action, password, compression_level):
    try:
        file_size = os.path.getsize(file_path)
        if file_size > size_threshold:
            split_and_compress_file(file_path, output_dir, large_volume_size, password, compression_level)
        else:
            if small_file_action == "compress":
                compress_file(file_path, output_dir, password, compression_level)
            else:
                split_and_compress_file(file_path, output_dir, small_volume_size, password, compression_level)
        return True
    except Exception as e:
        logging.error(localize('failed_copy', file_path=file_path, error=e))
        return False