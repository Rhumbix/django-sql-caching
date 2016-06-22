from setuptools import setup

setup(name='django-sql-caching',
      version='0.1.0',
      description='Cache DB reads on per-request basis.',
      url='https://github.com/Rhumbix/django-sql-caching.git',
      author='Kenneth Jiang',
      author_email='kenneth@rhumbix.com',
      license='MIT',
      packages=['sql_caching'],
      install_requires=[
          'Django',
      ],
      zip_safe=False)
