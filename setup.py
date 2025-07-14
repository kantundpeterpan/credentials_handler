from setuptools import setup, find_packages

setup(
    name='kestra secret encoder',  # Replace with your package name
    version='0.1.0',  # Replace with your package version
    description='A commandline tool to encode secrets for use with the open-source version of kestra',  # Replace with a description
    long_description=open('README.md').read(),  # Optional: Long description from README
    long_description_content_type='text/markdown',  # If using Markdown in README
    url='https://github.com/kantundpeterpan/kestra_secret_encoder',  # Replace with your repo URL
    author='Heiner Atze',  # Replace with your name
    author_email='heiner.atze@gmx.net',  # Replace with your email
    license='GNU',  # Replace with your license
    packages=find_packages(),  # Automatically find your package(s)
    install_requires=[  # List your package's dependencies
        'toml',
        'pyyaml'
    ],

    entry_points={
        'console_scripts': [
            'credentials_handler = credentials_handler:main',
        ],
    },
)
