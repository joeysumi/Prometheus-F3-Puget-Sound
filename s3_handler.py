import boto3


class S3Handler:

    def __init__(self, bucket_name, **kwargs):
        self._s3_resource = None
        self._s3_bucket = None
        self.bucket_name = bucket_name

    @property
    def s3_resource(self):
        if self._s3_resource is None:
            self._s3_resource = boto3.resource("s3")
            print("Connected to S3 resource.")
        return self._s3_resource

    @property
    def s3_bucket(self):
        if self._s3_bucket is None:
            self._s3_bucket = self.s3_resource.Bucket(self.bucket_name)
        return self._s3_bucket

    def is_file_in_directory(self, directory_path: str, file_name: str) -> bool:
        """ Checks to see if file exists in directory (s3 uses "key")

        Returns:
            True if file exists
            False if file does not exist in an existing path, creating path if necessary
        """
        bucket_collection = self.s3_bucket.objects.filter(Prefix=directory_path)
        object_name_list = [obj.key for obj in bucket_collection]
        for name in object_name_list:
            if file_name in name:
                return True
        return False

    def save_file_to_directory(self, file_data: bytes, directory_path: str, max_files_in_directory: int = None):
        """ Saves the file to the S3 Bucket, if the path doesn't exist, it will create one
            Thus it is important to have the correct path or there will be variations and different "folders"
        """
        img_obj = self.s3_resource.Object(self.bucket_name, directory_path)
        img_obj.put(Body=file_data)

        if max_files_in_directory:
            self._cleanup_directory(directory_path, max_files_in_directory)

    def _cleanup_directory(self, file_path, max_file_number) -> None:
        directory_break_line = file_path.rfind("/")
        directory = file_path[:directory_break_line]
        directory_object_list = [image for image in self.s3_bucket.objects.filter(Prefix=directory)]
        if len(directory_object_list) <= max_file_number:
            return

        directory_object_list.sort(key=lambda x: x.last_modified)
        directory_object_list[0].delete()

    def get_s3_resource_object_data(self, directory_path: str):
        object_summary = self._get_s3_object_summary(directory_path)
        return object_summary.get()

    def _get_s3_object_summary(self, directory_path):
        bucket_collection = self.s3_bucket.objects.filter(Prefix=directory_path)
        object_list = [object for object in bucket_collection]
        return object_list[0]

    def update_s3_resource_object(self, directory_path: str, updated_text: str):
        object_summary = self._get_s3_object_summary(directory_path)
        new_text_bytes = updated_text.encode()
        object_summary.put(Body=new_text_bytes)
