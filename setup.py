"""
Directory API client core
"""
from setuptools import find_packages, setup

setup(
    name='directory_client_core',
    version='7.2.10',
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
        'sigauth>=5.2.4,<6.0.0',
        'django>=4.2.8,<5.0',
        'w3lib>=1.19.0,<2.0.0',
    ],
    extras_require={
        'test': [
            'flake8==5.0.4',
            'freezegun==1.0.0',
            'pytest-django==4.1.0',
            'pytest-sugar==0.9.5',
            'pytest==5.4.0',
            'pytest-cov',
            'pytest-codecov',
            'GitPython',
            'requests_mock==1.8.0',
            'setuptools>=38.6.0,<39.0.0',
            'twine',
            'wheel>=0.31.0,<1.0.0',
        ]
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Framework :: Django :: 2.2',
        'Framework :: Django :: 3.1',
        'Framework :: Django :: 3.2',
        'Framework :: Django :: 4.2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
