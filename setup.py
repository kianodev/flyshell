# setup.py

from setuptools import Extension, find_packages, setup

native_disk = Extension(
    name="flyshell._native_disk",
    sources=["c_src/diskops.c"],
)

setup(
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    ext_modules=[native_disk],
)
