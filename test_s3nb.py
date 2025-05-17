from s3nb import S3Shell


def test_cd():
    s3 = S3Shell()
    assert s3.cd('root') == 'root/'
    assert s3.cd('dir1/') == 'root/dir1/'
    assert s3.cd('dir2/') == 'root/dir1/dir2/'
    assert s3.cd('..') == 'root/dir1/'
    assert s3.cd('..') == 'root/'

def test_parse_path():
    s3 = S3Shell()
    s3.cb('bucket1')
    assert s3._parse_path('root/dir1/') == ('bucket1', 'root/dir1/')
    assert s3._parse_path('/bucket2/root/dir1/') == ('bucket2', 'root/dir1/')
