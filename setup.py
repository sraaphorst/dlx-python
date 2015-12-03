#!/usr/bin/env python

from setuptools import setup
setup(name='dlx',
      version='1.0.4',
      description="Implementation of Donald Knuth's Dancing Links algorithm.",
      author='Sebastian Raaphorst',
      author_email='srcoding@gmail.com',
      url='http://www.site.uottawa.ca/~mraap046',
      packages=['dlx'],
      long_description="""
         This package provides an implementation of Donald Knuth's Dancing
         Links algorithm for solving exact set cover problems.

         1.0.4: Minor Python 3 bugfix.
         1.0.3: Attempt to make code compatible with Python 3.
         1.0.2: Removed extraneous code (had switched from callbacks for solutions to
                making solve a generator to yield, but had forgotten to remove the
                solution callback function parameter from the solve method).
         1.0.1: Critical bugfix (N array was one short: did not account for header).
         1.0.0: Initial release.
      """,
      classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Mathematics',
        ],
      keywords='exact cover algorithm dlx dancing links',
      license='Apache 2.0'
      )

