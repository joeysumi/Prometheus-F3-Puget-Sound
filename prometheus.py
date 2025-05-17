import json
from io import BytesIO

import requests

from mysql_handler import MySqlHandler
from s3_handler import S3Handler


class Prometheus:

    S3_BUCKET = "f3pugetsound-slack-pictures"
    LAST_PULLED_IMAGE_NAME_DOCUMENT = "last_file.txt"
    MAX_FILES_IN_AO = 10
    SQL_QUERY_LIMIT = 10

    def __init__(self, credentials, mysql_handler=MySqlHandler, s3_handler=S3Handler):
        self.mysql_handler = mysql_handler(**credentials)
        self.s3_handler = s3_handler(self.S3_BUCKET)
        self.most_recent_image_pulled = None

    def run(self):
        self.most_recent_image_pulled = self._get_most_recently_used_image()
        new_images_list = self._get_list_of_new_images()
        if len(new_images_list) > 0:  # there are new images
            self._record_last_image_taken(new_images_list[-1])

        for image_data in new_images_list:
            image_data_with_image_information = self._get_image_data_from_url(image_data)
            self._save_image_to_s3_bucket(image_data_with_image_information)

    def _get_most_recently_used_image(self):
        if not self.s3_handler.is_file_in_directory(directory_path="", file_name=self.LAST_PULLED_IMAGE_NAME_DOCUMENT):
            return

        object_data = self.s3_handler.get_s3_resource_object_data(self.most_recent_image_pulled)
        most_recent_image_name = object_data.get("Body").read().decode() if object_data.get("Body") else None
        return most_recent_image_name

    def _get_list_of_new_images(self) -> list[dict]:
        query = (
            "SELECT ao, bd_date, json"
            "FROM beatdowns b"
            "JOIN aos a"
            "WHERE a.channel_id = b.ao_id"
            "AND ao LIKE \"ao%\""
            "AND json LIKE \"%http%\""
            "ORDER BY bd_date DESC"
        )
        self.mysql_handler.connect_to_database()

        image_list = []
        while True:  # there is no "False" because "return" breaks the while loop
            query_results = self._get_query_results(query)
            verified_query_results = self._remove_images_already_exported(query_results)

            #  Need to check if no results left OR the list is less than query result (stopped bc of last used image)
            if len(verified_query_results) == 0 or len(verified_query_results) % self.SQL_QUERY_LIMIT != 0:
                self.mysql_handler.disconnect_from_database()
                return image_list
            image_list += verified_query_results

    def _get_query_results(self, query) -> list[dict]:
        query_results = self.mysql_handler.run_query(query, limit=self.SQL_QUERY_LIMIT)
        formatted_results = self._format_results(query_results)
        return formatted_results

    @staticmethod
    def _format_results(query_results) -> list[dict]:
        """ Formats query results from the returned query results to something usable

            A returned query results returns a tuple like this:
            (ao-name, datetime.date(2025, 5, 8), {"files":["https://url-to-image"]})
            This method returns a usable dictionary:
            {"ao": "ao-name", "db_date": "2025-05=15", "filename": "image_name", "url": "https://url-to-image"}
        """
        formatted_list = []
        for result in query_results:
            url_str = json.loads(result[2])["files"][0]
            url_breakpoint_before_image_name = url_str.rfind("/") + 1
            filename = url_str[url_breakpoint_before_image_name:]

            formatted_result = {
                "ao": result[0],
                "db_date": result[1].strftime("%Y-%m-%d"),
                "filename": filename,
                "url": url_str,
            }
            formatted_list.append(formatted_result)

        return formatted_list

    def _remove_images_already_exported(self, formatted_results) -> list[dict]:
        """ Checks the results of the query and returns only images newer than last pulled image """
        results_checked = 0
        for result in formatted_results:
            if result["filename"] == self.most_recent_image_pulled:
                break
            results_checked += 1

        return formatted_results[:results_checked]  # returns list of only new images

    def _record_last_image_taken(self, image_data):
        filename = image_data["filename"]
        self.s3_handler.update_s3_resource_object(self.LAST_PULLED_IMAGE_NAME_DOCUMENT, filename)

    @staticmethod
    def _get_image_data_from_url(image_data_dict: dict) -> dict:
        url_response = requests.get(image_data_dict["url"], stream=True)
        image_data_bytes = BytesIO(url_response.content)
        return {"image_bytes": image_data_bytes, **image_data_dict}

    def _save_image_to_s3_bucket(self, image_data_dict):
        # if for some reason image already exists in directory
        if self.s3_handler.is_file_in_directory(image_data_dict["ao"], image_data_dict["filename"]):
            return

        self.s3_handler.save_file_to_directory(
            file_data=image_data_dict["image_bytes"],
            directory_path=f"{image_data_dict["ao"]}/{image_data_dict["filename"]}",
            max_files_in_directory=self.MAX_FILES_IN_AO,
        )
