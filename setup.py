from distutils.core import setup
import setuptools


setup(name='OnlineJudgeSpider',
      version='0.1',
      description='Online Judge Spider',
      author='dian xu',
      author_email='xudian.cn@gmail.com',
      packages=['OnlineJudgeSpider','OnlineJudgeSpider/OJs'],
      install_requires=['beautifulsoup4', 'lxml']
      )
