"""
The binx.io og image generator
"""
from setuptools import find_packages, setup

dependencies = ['click', 'pillow']

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='binx-og-image-generator',
    version="1.0.4",
    url='https://github.com/binxio/og-image-generator',
    license="restricted",
    author='Mark van Holsteijn',
    author_email='mark@binx.io',
    description='generates og image for the binx.io blog',
    long_description=long_description,
    long_description_content_type='text/markdown',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    package_data={
        # If any package contains .png or .ttf file,include them
        "binx_og_image_generator": ["fonts/*", "images/*"],
    },
    #include_package_data = True, # does not work if you set it.
    zip_safe=False,
    platforms='any',
    install_requires=dependencies,
    setup_requires=['twine>=4.0.0'],
    tests_require=dependencies +  ['pytest', 'pytest-runner'],
    test_suite='tests',
    entry_points={
        'console_scripts': [
            'binx-og-image-generator = binx_og_image_generator.__main__:main'
        ],
    },
    classifiers=[
        # As from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        # 'Development Status :: 1 - Planning',
        # 'Development Status :: 2 - Pre-Alpha',
        # 'Development Status :: 3 - Alpha',
        'Development Status :: 4 - Beta',
        #'Development Status :: 5 - Production/Stable',
        # 'Development Status :: 6 - Mature',
        # 'Development Status :: 7 - Inactive',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Operating System :: POSIX',
        'Operating System :: MacOS',
        'Operating System :: Unix',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
