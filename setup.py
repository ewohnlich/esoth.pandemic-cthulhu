from setuptools import find_packages
from setuptools import setup


version = '1.0'

setup(name='esoth.pandemic_cthulhu',
      version=version,
      description="personal project to replicate the board game",
      classifiers=[
          "Programming Language :: Python",
          "Programming Language :: Python :: 3.6",
      ],
      author='Eric Wohnlich',
      author_email='eric.wohnlich@gmail.com',
      url='https://github.com/ewohnlich/esoth.pandemic_cthulhu',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['esoth'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[],
)