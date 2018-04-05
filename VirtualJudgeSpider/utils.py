import os


def deal_with_image_url(remote_path, oj_prefix):
    if not remote_path.startswith('http://') and not remote_path.startswith('https://'):
        remote_path = os.path.join(oj_prefix, remote_path)

    file_name = str(str(remote_path).split('/')[-1].split('.')[0])
    return file_name
