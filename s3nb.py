import boto3
import configparser


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
            self.prefix = '/'.join(self.prefix.split('/')[:-1])[1:]
        else:
            self.prefix = '/'.join([self.prefix, path])[1:]

        return self.prefix

    def cb(self, bucket):
        old_bucket = self.bucket
        self.bucket = bucket
        return old_bucket

    def ls(self, path='', max_keys=1000, start_after=''):
        if path.startswith('/'):
            bucket = path.split('/')[1]
            prefix = '/'.join(path.split('/')[2:]) 
        else:
            bucket = self.bucket
            prefix = self.prefix

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
                    'last_modified':obj['LastModified'].strftime('%Y-%m-%d %H:%M:%S'),
                    'storage_class':obj['StorageClass']
                })

        if 'CommonPrefixes' in response:
            for prefix in response['CommonPrefixes']:
                items.append({
                    'key': prefix['Prefix'],
                    'size': 0,
                    'last_modified': '',
                    'storage_class': ''
                })

        return items
