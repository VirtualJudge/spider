import setuptools

setuptools.setup(name='spider',
                 version='1.0',
                 description='Virtual Judge Spider',
                 author='dianhsu',
                 author_email='xudian.cn@gmail.com',
                 packages=setuptools.find_packages(),
                 install_requires=['beautifulsoup4', 'lxml', 'requests'],
                 classifiers=[
                     "Programming Language :: Python :: 3",
                     "License :: OSI Approved :: MIT License",
                     "Operating System :: OS Independent",
                 ]
                 )
