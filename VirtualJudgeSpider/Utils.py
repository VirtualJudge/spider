import requests
from enum import Enum
from bs4 import element


class HttpUtil(object):
    def __init__(self, custom_headers=None, code_type=None):
        self._headers = custom_headers
        self._request = requests.session()
        self._code_type = code_type
        self._response = None
        if self._headers:
            self._request.headers.update(self._headers)

    def get(self, url, **kwargs):
        self._response = self._request.get(url, **kwargs)
        if self._code_type and self._response:
            self._response.encoding = self._code_type
        return self._response

    def post(self, url, data=None, json=None, **kwargs):
        self._response = self._request.post(url, data, json, **kwargs)
        if self._code_type and self._response:
            self._response.encoding = self._code_type
        return self._response

    @staticmethod
    def abs_url(remote_path, oj_prefix):
        if not remote_path.startswith('http://') and not remote_path.startswith('https://'):
            remote_path = oj_prefix.rstrip('/') + '/' + remote_path.lstrip('/')
        file_name = str(str(remote_path).split('/')[-1])
        return file_name, remote_path


def deal_with_image_url(remote_path, oj_prefix):
    if not remote_path.startswith('http://') and not remote_path.startswith('https://'):
        remote_path = oj_prefix.rstrip('/') + '/' + remote_path.lstrip('/')
    file_name = str(str(remote_path).split('/')[-1])
    return file_name, remote_path


class HtmlTag(object):
    class TagDesc(Enum):
        TITLE = 'vj-title'
        CONTENT = 'vj-content'
        IMAGE = 'vj-image'
        FILE = 'vj-file'
        ANCHOR = 'vj-anchor'

    @staticmethod
    def update_tag(tag, oj_prefix):
        if type(tag) == element.Tag:
            for child in tag.descendants:
                if child.name == 'a' and child.get('href'):
                    if not child.get('class'):
                        child['class'] = ()
                    child['class'] += (HtmlTag.TagDesc.ANCHOR.value,)
                    child['href'] = HttpUtil.abs_url(child.get('href'), oj_prefix=oj_prefix)[-1]
                if child.name == 'img' and child.get('src'):
                    if not child.get('class'):
                        child['class'] = ()
                    child['class'] += (HtmlTag.TagDesc.IMAGE.value,)
                    child['src'] = HttpUtil.abs_url(child.get('src'), oj_prefix=oj_prefix)[-1]
        return tag
