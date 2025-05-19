import boto3
import configparser
import datetime
import polars as pl


class S3Shell:
    def __init__(self, config_file="s3nb.ini", env="default", *args, **kwargs):
        config = configparser.ConfigParser()
        try:
            config.read(config_file)
        except FileNotFoundError:
            try:
                config.read('~/.s3nb.ini')
            except FileNotFoundError:
                print("Config file not found.")
                raise FileNotFoundError(f"{config_file} not found.")

        self.s3client = boto3.client('s3', *args, **{ **config[env], **kwargs})
        self.prefix = ''
        self.bucket = ''

    def cd(self, path):
        if path == '..':
            self.prefix = '/'.join(self.prefix.split('/')[:-2]) + '/'
        else:
            self.prefix += (path + '/') if not path.endswith('/') else path

        return self.prefix

    def cb(self, bucket):
        old_bucket = self.bucket
        self.bucket = bucket
        return old_bucket

    def _parse_path(self, path):
        if path.startswith('/'):
            bucket = path.split('/')[1]
            prefix = '/'.join(path.split('/')[2:]) 
        else:
            bucket = self.bucket
            prefix = self.prefix + path

        return bucket, prefix

    def lsb(self):
        response = self.s3client.list_buckets()
        if 'Buckets' in response:
            return [{'name': bucket['Name'], 'creation_date': bucket.get('CreationDate', datetime.datetime.now()).strftime('%Y-%m-%d %H:%M:%S'), 'region': bucket.get('BucketRegion', '')} for bucket in response['Buckets']]

        return []

    def ls(self, path='', max_keys=1000, start_after='', depth=1):
        bucket, prefix = self._parse_path(path)
        items = self._ls_recursive(bucket, prefix, max_keys, start_after, depth)
        if items:
            return pl.DataFrame(items)
        else:
            return pl.DataFrame()

    def _ls_recursive(self, bucket, prefix, max_keys, start_after, depth):
        response = self.s3client.list_objects_v2(
            Bucket=bucket, 
            Prefix=prefix, 
            Delimiter='/',
            MaxKeys=max_keys,
            StartAfter=start_after
        )

        items = []
        if 'Contents' in response:
            for obj in response['Contents']:
                items.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'].strftime('%Y-%m-%d %H:%M:%S'),
                    'storage_class': obj['StorageClass'],
                    'bucket': bucket,
                })

        if 'CommonPrefixes' in response:
            if depth > 0:
                for cp in response['CommonPrefixes']:
                    sub_prefix = cp['Prefix']
                    items.extend(self._ls_recursive(bucket, sub_prefix, max_keys, '', depth - 1))
            else:
                items.extend([{'key': cp['Prefix'], 'size': 0, 'last_modified': '', 'storage_class': '', 'bucket': bucket} for cp in response['CommonPrefixes']])

        return items

    def dl(self, path, local_path):
        bucket, prefix = self._parse_path(path)
        return self.s3client.download_file(bucket, prefix, local_path)
