"""
Directory API client core
"""
from setuptools import find_packages, setup

setup(
    name='directory_client_core',
    version='7.1.1',
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
        'sigauth>=4.0.1,<5.2.0',
        'django>=3.2.18,<4.0.0',
        'w3lib>=1.19.0,<2.0.0',
    ],
    extras_require={
        'test': [
            'codecov==2.1.9',
            'flake8==5.0.4',
            'freezegun==1.0.0',
            'pytest-cov==2.10.1',
            'pytest-django==4.1.0',
            'pytest-sugar==0.9.5',
            'pytest==5.4.0',
            'requests_mock==1.8.0',
            'setuptools>=38.6.0,<39.0.0',
            'twine>=1.11.0,<2.0.0',
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
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
