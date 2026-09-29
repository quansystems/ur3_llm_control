from glob import glob
import os

from setuptools import find_packages, setup

package_name = 'ur3_llm_control'

setup(
    name=package_name,
    version='1.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml', 'README.md']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Nguyen Van Quan',
    maintainer_email='nguyenvanquan.student@example.com',
    description='Student-owned LLM-controlled pick-and-place system for UR3/UR3e in Gazebo',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'llm_robot_node = ur3_llm_control.natural_language_robot:main',
            'send_command = ur3_llm_control.command_sender:main',
            'check_scene = ur3_llm_control.reachability_check:main',
            'offline_cli = ur3_llm_control.offline_cli:main',
        ],
    },
)
