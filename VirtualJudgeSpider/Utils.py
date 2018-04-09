import requests


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


def deal_with_image_url(remote_path, oj_prefix):
    if not remote_path.startswith('http://') and not remote_path.startswith('https://'):
        remote_path = oj_prefix.rstrip('/') + '/' + remote_path.lstrip('/')
    file_name = str(str(remote_path).split('/')[-1])
    return file_name, remote_path
