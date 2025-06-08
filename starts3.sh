#!/usr/bin/env bash

docker run -p 9000:9000 -p 9001:9001 --volume miniodata:/data --network docknet \
  quay.io/minio/minio server /data --console-address ":9001"
