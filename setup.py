"""
Directory API client core
"""
from setuptools import setup, find_packages


setup(
    name='directory_client_core',
    version='4.3.1',
    url='https://github.com/uktrade/directory-client-core',
    license='MIT',
    author='Department for International Trade',
    description='Python common code for Directory API clients.',
    packages=find_packages(exclude=["tests.*", "tests"]),
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    include_package_data=True,
    install_requires=[
        'requests>=2.21.0,<3.0.0',
        'monotonic>=1.2,<3.0',
        'sigauth>=4.0.1,<5.0.0',
        'django>=1.9,<2.0a1',
        'w3lib>=1.19.0<2.0.0',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
