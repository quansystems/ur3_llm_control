import os

from ament_index_python.packages import get_package_share_directory


def config_path(filename: str) -> str:
    package_dir = get_package_share_directory('ur3_llm_control')
    return os.path.join(package_dir, 'config', filename)
