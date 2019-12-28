from setuptools import setup
from otftp import __version__


description = 'Python 3 asynchronous TFTP server for Oberon'
long_description = description

setup(
    name='otftp',
    version=__version__,
    description=description,
    long_description=long_description,
    url='https://github.com/pedrudehuere/otftpd',
    author='ap',
    author_email='miao@miao.bau',
    license='MIT',
    keywords='async asynchronous tftp Oberon',
    packages=['otftp'],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'otftp = otftp.__main__:main'
        ]
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'Topic :: Utilities',
        'Topic :: Software Development',
        'License :: OSI Approved :: MIT License',
    ],
)
