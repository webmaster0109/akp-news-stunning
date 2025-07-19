from storages.backends.s3 import S3Storage


class MediaFileStorage(S3Storage):
  location = "media"

class StaticFileStorage(S3Storage):
  location = "static"