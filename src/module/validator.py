from src.importer import *


class ExeListValidator(ConfigValidator):
    def validate(self, value):
        if not isinstance(value, list):
            return False
        if len(value) == 0:
            return True  # 空列表有效
        for item in value:
            file_path = Path(item)
            if not file_path.exists() or file_path.suffix != '.exe':
                return False
        return True

    def correct(self, value):
        if not isinstance(value, list):
            raise ValueError("The value must be a list.")
        corrected_list = []
        for item in value:
            file_path = Path(item)
            if not file_path.exists() or file_path.suffix != '.exe':
                raise ValueError(f"The path {item} is not a valid .exe file.")
            corrected_list.append(str(file_path.absolute()).replace("\\", "/"))
        return corrected_list


class ExeValidator(ConfigValidator):
    def validate(self, value):
        if value is None or value == "":
            return True  # 空值有效
        file_path = Path(value)
        return file_path.exists() and file_path.suffix == '.exe'

    def correct(self, value):
        if value is None or value == "":
            return value  # 空值有效, 直接返回
        file_path = Path(value)
        if not file_path.exists() or file_path.suffix != '.exe':
            raise ValueError(f"The path {value} is not a valid .exe file.")
        return str(file_path.absolute()).replace("\\", "/")


class StringValidator(ConfigValidator):
    def validate(self, value):
        return value.strip() != ''

    def correct(self, value):
        if not value.strip():
            return ""
        return value
