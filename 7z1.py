import os
import subprocess
import json
import shutil
import hashlib
import tkinter as tk
from tkinter import filedialog, messagebox
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Language dictionary for localization
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

# Set default language
current_lang = 'en'

def localize(key, **kwargs):
    return LANG[current_lang].get(key, key).format(**kwargs)

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
        messagebox.showerror(localize('error'), localize('failed_compress', file_path=file_path, error=e))
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
        messagebox.showerror(localize('error'), localize('failed_compress', file_path=file_path, error=e))
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
        messagebox.showerror(localize('error'), localize('failed_copy', file_path=file_path, error=e))
        logging.error(localize('failed_copy', file_path=file_path, error=e))
        return False

def select_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        entry_file_path.delete(0, tk.END)
        entry_file_path.insert(0, file_path)

def select_directory():
    dir_path = filedialog.askdirectory()
    if dir_path:
        entry_dir_path.delete(0, tk.END)
        entry_dir_path.insert(0, dir_path)

def select_output_dir():
    output_dir = filedialog.askdirectory()
    if output_dir:
        entry_output_dir.delete(0, tk.END)
        entry_output_dir.insert(0, output_dir)

def enable_file_selection():
    entry_file_path.config(state='normal')
    btn_browse_file.config(state='normal')
    entry_dir_path.config(state='disabled')
    btn_browse_dir.config(state='disabled')
    entry_dir_path.delete(0, tk.END)  # Clear the directory path if file selection is enabled

def enable_directory_selection():
    entry_dir_path.config(state='normal')
    btn_browse_dir.config(state='normal')
    entry_file_path.config(state='disabled')
    btn_browse_file.config(state='disabled')
    entry_file_path.delete(0, tk.END)  # Clear the file path if directory selection is enabled

def start_processing():
    file_path = entry_file_path.get()
    dir_path = entry_dir_path.get()
    output_dir = entry_output_dir.get()
    size_threshold = int(entry_size_threshold.get()) * 1024 * 1024
    large_volume_size = int(entry_large_volume_size.get()) * 1024 * 1024
    small_volume_size = int(entry_small_volume_size.get()) * 1024 * 1024
    include_subdirs = var_include_subdirs.get()
    small_file_action = var_small_file_action.get()
    password = entry_password.get()
    compression_level = int(entry_compression_level.get())

    if not file_path and not dir_path:
        messagebox.showerror(localize('error'), localize('select_input'))
        return

    if not output_dir or not os.path.exists(output_dir):
        messagebox.showerror(localize('error'), localize('output_dir_not_exist'))
        return

    if file_path:
        dir_path = ""  # Ignore directory if file is selected
        copy_file(file_path, output_dir, size_threshold, large_volume_size, small_volume_size, small_file_action, password, compression_level)
    elif dir_path:
        file_path = ""  # Ignore file if directory is selected
        process_directory(dir_path, output_dir, size_threshold, large_volume_size, small_volume_size, include_subdirs, small_file_action, password, compression_level)

def switch_language():
    global current_lang
    current_lang = 'zh' if current_lang == 'en' else 'en'
    update_labels()

def update_labels():
    rb_file.config(text=localize('input_file'))
    rb_dir.config(text=localize('input_directory'))
    lbl_output_dir.config(text=localize('output_directory'))
    lbl_size_threshold.config(text=localize('size_threshold'))
    lbl_large_volume_size.config(text=localize('large_volume_size'))
    lbl_small_volume_size.config(text=localize('small_volume_size'))
    chk_include_subdirs.config(text=localize('compress_subdirs'))
    lbl_small_file_action.config(text=localize('small_file_action'))
    rb_compress.config(text=localize('compress'))
    rb_split_compress.config(text=localize('split_compress'))
    lbl_password.config(text=localize('password'))
    lbl_compression_level.config(text=localize('compression_level'))
    btn_start.config(text=localize('start'))
    btn_switch_lang.config(text=localize('switch_language'))

app = tk.Tk()
app.title("File or Directory Split and Compress")

frame = tk.Frame(app)
frame.pack(padx=10, pady=10)

var_input_selection = tk.StringVar(value="file")
rb_file = tk.Radiobutton(frame, text=localize('input_file'), variable=var_input_selection, value="file", command=enable_file_selection)
rb_file.grid(row=0, column=0, sticky=tk.W)
entry_file_path = tk.Entry(frame, width=50)
entry_file_path.grid(row=0, column=1, padx=5)
btn_browse_file = tk.Button(frame, text="Browse", command=select_file)
btn_browse_file.grid(row=0, column=2)

rb_dir = tk.Radiobutton(frame, text=localize('input_directory'), variable=var_input_selection, value="directory", command=enable_directory_selection)
rb_dir.grid(row=1, column=0, sticky=tk.W)
entry_dir_path = tk.Entry(frame, width=50, state='disabled')
entry_dir_path.grid(row=1, column=1, padx=5)
btn_browse_dir = tk.Button(frame, text="Browse", command=select_directory, state='disabled')
btn_browse_dir.grid(row=1, column=2)

lbl_output_dir = tk.Label(frame, text=localize('output_directory'))
lbl_output_dir.grid(row=2, column=0, sticky=tk.W)
entry_output_dir = tk.Entry(frame, width=50)
entry_output_dir.grid(row=2, column=1, padx=5)
btn_browse_output = tk.Button(frame, text="Browse", command=select_output_dir)
btn_browse_output.grid(row=2, column=2)

lbl_size_threshold = tk.Label(frame, text=localize('size_threshold'))
lbl_size_threshold.grid(row=3, column=0, sticky=tk.W)
entry_size_threshold = tk.Entry(frame)
entry_size_threshold.insert(0, "25")
entry_size_threshold.grid(row=3, column=1, padx=5, sticky=tk.W)

lbl_large_volume_size = tk.Label(frame, text=localize('large_volume_size'))
lbl_large_volume_size.grid(row=4, column=0, sticky=tk.W)
entry_large_volume_size = tk.Entry(frame)
entry_large_volume_size.insert(0, "25")
entry_large_volume_size.grid(row=4, column=1, padx=5, sticky=tk.W)

lbl_small_volume_size = tk.Label(frame, text=localize('small_volume_size'))
lbl_small_volume_size.grid(row=5, column=0, sticky=tk.W)
entry_small_volume_size = tk.Entry(frame)
entry_small_volume_size.insert(0, "25")
entry_small_volume_size.grid(row=5, column=1, padx=5, sticky=tk.W)

var_include_subdirs = tk.BooleanVar(value=False)
chk_include_subdirs = tk.Checkbutton(frame, text=localize('compress_subdirs'), variable=var_include_subdirs)
chk_include_subdirs.grid(row=6, columnspan=3, pady=5)

lbl_small_file_action = tk.Label(frame, text=localize('small_file_action'))
lbl_small_file_action.grid(row=7, column=0, sticky=tk.W)
var_small_file_action = tk.StringVar(value="compress")
rb_compress = tk.Radiobutton(frame, text=localize('compress'), variable=var_small_file_action, value="compress")
rb_split_compress = tk.Radiobutton(frame, text=localize('split_compress'), variable=var_small_file_action, value="split_compress")
rb_compress.grid(row=7, column=1, sticky=tk.W)
rb_split_compress.grid(row=7, column=2, sticky=tk.W)

lbl_password = tk.Label(frame, text=localize('password'))
lbl_password.grid(row=8, column=0, sticky=tk.W)
entry_password = tk.Entry(frame, show='*')
entry_password.grid(row=8, column=1, padx=5, sticky=tk.W)

lbl_compression_level = tk.Label(frame, text=localize('compression_level'))
lbl_compression_level.grid(row=9, column=0, sticky=tk.W)
entry_compression_level = tk.Entry(frame)
entry_compression_level.insert(0, "1")
entry_compression_level.grid(row=9, column=1, padx=5, sticky=tk.W)

btn_start = tk.Button(frame, text=localize('start'), command=start_processing)
btn_start.grid(row=10, columnspan=3, pady=10)

btn_switch_lang = tk.Button(frame, text=localize('switch_language'), command=switch_language)
btn_switch_lang.grid(row=11, columnspan=3, pady=10)

update_labels()
app.mainloop()
