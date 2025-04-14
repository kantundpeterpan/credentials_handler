from setuptools import setup, find_packages

setup(
    name='kestra secret encoder',  # Replace with your package name
    version='0.1.0',  # Replace with your package version
    description='A commandline tool to encode secrets for use the open-source version kestra',  # Replace with a description
    long_description=open('README.md').read(),  # Optional: Long description from README
    long_description_content_type='text/markdown',  # If using Markdown in README
    url='https://github.com/your_username/your_repo',  # Replace with your repo URL
    author='Your Name',  # Replace with your name
    author_email='your.email@example.com',  # Replace with your email
    license='MIT',  # Replace with your license
    packages=find_packages(),  # Automatically find your package(s)
    install_requires=[  # List your package's dependencies
        # 'dependency1',
        # 'dependency2>=1.0.0',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',  # Choose appropriate status
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',  # Choose your license
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    entry_points={
        'console_scripts': [
            'your_command_name = your_package.module:main_function',
        ],
    },
)