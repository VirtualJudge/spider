# VirtualJudgeSpider
VirtualJudge - Judge Spider  
[![Build Status](https://travis-ci.org/VirtualJudge/Spider.svg?branch=master)](https://travis-ci.org/VirtualJudge/Spider)
[![Coverage Status](https://coveralls.io/repos/github/VirtualJudge/Spider/badge.svg?branch=master)](https://coveralls.io/github/VirtualJudge/Spider?branch=master)
***
### build script
`python3 setup.py bdist_wheel`

### feature
 - 对于每道题目爬取标题，时间限制，空间限制，和题面。
 - 删除题面的样式，统一使用style(后面可以自定义style)
 - 标注题面标题，内容，图片，文件。
 - 保存登录session，提高抓取效率

### now supports
 - HDU
 - WUST
 - POJ
 - FZU
 - Aizu
 - ZOJ
