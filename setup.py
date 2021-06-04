import os
from setuptools import setup, find_packages


version = "0.1"

install_requires = [
    'bjoern',
    'colorlog',
    'importscan',
    'minicli',
    'omegaconf',
    'rutter',
    'zope.dottedname',
]

test_requires = [
    'pytest',
]


setup(
    name='horsebox',
    version=version,
    author='Souheil CHELFOUH',
    author_email='trollfot@gmail.com',
    url='http://',
    download_url='http://pypi.python.org/pypi/horsebox',
    description='Deployment utility for WSGI apps',
    long_description=(open("README.txt").read() + "\n" +
                      open(os.path.join("docs", "HISTORY.txt")).read()),
    license='ZPL',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python:: 3 :: Only',
    ],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    extras_require={
        'test': test_requires,
    },
    entry_points={
        'console_scripts': [
            'horsebox = horsebox.runner:serve'
        ],
    },
)
