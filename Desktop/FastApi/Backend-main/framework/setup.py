from setuptools import setup

setup(name='framework',
      version='0.1',
      description='Code generation & runtime',
      url='',
      author='Prashanth Gopinath',
      author_email='',
      license='',
      packages=[''],
      package_data= {'model':['*.tx', '*.jinja']},
      install_requires=['fastapi', 'email-validator', 'elasticsearch[async]==7.13.1', 'httpx', 'jinja2', 'motor', 'textx', 'uvicorn', 'aioredis_cluster', 'aioredis', 'redis', 'cryptography', 'pyjwt', 'pydantic[dotenv]'],
      zip_safe=False
      )
