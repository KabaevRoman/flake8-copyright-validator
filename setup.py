from setuptools import setup

with open('README.md') as readme:
    long_description = readme.read()
classifiers = [
    'Framework :: Flake8',
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Natural Language :: Russian',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Topic :: Software Development',
]

setup(
    name='flake8-copyright-validator',
    description='Check if python file contain copyright text',
    long_description=long_description,
    classifiers=classifiers,
    author='Roman Kabaev',
    author_email='kabaevgithub@gmail.com',
    license='MIT',
    url='https://github.com/KabaevRoman/flake8-copyright-validator',
    python_requires='>=3.7',
    install_requires=[
        'setuptools>=58.1.0',
        'flake8>=7.0.0',
        'importlib-metadata>=7.0.1'
    ],
)
