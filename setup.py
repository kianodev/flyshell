# setup.py

from setuptools import Extension, setup
import sys

sources = [
    "c_src/diskops/diskops.c",
]

if sys.platform == "win32":
    sources.append("c_src/diskops/win32/placeholder.c")
else:
    sources.append("c_src/diskops/posix/placeholder.c")

native_disk = Extension(
    name="flyshell.bin._native_diskops",
    sources=sources,
)

setup(
    ext_modules=[native_disk],
)
