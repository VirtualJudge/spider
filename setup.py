import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(name='VirtualJudgeSpider',
                 version='1.0',
                 description='Virtual Judge Spider',
                 author='prefixai',
                 author_email='xudian.cn@gmail.com',
                 long_description=long_description,
                 long_description_content_type="text/markdown",
                 packages=setuptools.find_packages(),
                 install_requires=['beautifulsoup4', 'lxml', 'requests'],
                 classifiers=[
                     "Programming Language :: Python :: 3",
                     "License :: OSI Approved :: MIT License",
                     "Operating System :: OS Independent",
                 ]
                 )
