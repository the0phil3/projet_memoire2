from setuptools import setup, Extension
from Cython.Build import cythonize

ext_modules = [
    Extension(
        "similarity_cython",
        sources=["similarity_cython.pyx"],
        libraries=["m"],  # You may need to add other libraries if necessary
    )
]

setup(
    name="YourPackageName",
    ext_modules=cythonize(ext_modules)
)
