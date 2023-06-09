from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in tencent_integration/__init__.py
from tencent_integration import __version__ as version

setup(
	name="tencent_integration",
	version=version,
	description="Tencent Cloud Integration",
	author="Alvin",
	author_email="alvin.zhang.00@qq.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
