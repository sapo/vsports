from setuptools import setup, find_packages

setup(
    name='vsports',
    version='1.0.1',
    author='SAPO',
    author_email='eduardo.pinto@gmail.com',
    description='A Python client for the Vsports API',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/poingg/vsports',
    packages=find_packages(),
    install_requires=[
        'requests',
        'redis',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
)
