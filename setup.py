from setuptools import setup
from setuptools.command.test import test as TestCommand
import sys


class PyTest(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['test']
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)

setup(
    name='pelican_oembed',
    version='1.0.0',
    author='Ben Caller',
    author_email='bcaller [at] gmail',
    description='Python Pelican extension for embedding content using OEmbed',
    packages=['pelican_oembed'],
    install_requires=[
        'pyembed_markdown',
        'markdown'
    ],
    tests_require=[
        'mock',
        'pytest',
        'vcrpy'
    ],

    cmdclass={'test': PyTest},

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Text Processing'
    ]
)