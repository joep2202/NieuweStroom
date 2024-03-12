import logging
import sys
import pandas as pd
import xarray as xr
import os
import requests


class OpenDataAPI:
    def __init__(self, api_token: str):
        # determine base url and api token
        self.base_url = "https://api.dataplatform.knmi.nl/open-data/v1"
        self.headers = {"Authorization": api_token}

    def __get_data(self, url, params=None):
        # requests data
        return requests.get(url, headers=self.headers, params=params).json()

    def list_files(self, dataset_name: str, dataset_version: str, params: dict):
        return self.__get_data(
            f"{self.base_url}/datasets/{dataset_name}/versions/{dataset_version}/files",
            params=params,
        )

    def get_file_url(self, dataset_name: str, dataset_version: str, file_name: str):
        return self.__get_data(
            f"{self.base_url}/datasets/{dataset_name}/versions/{dataset_version}/files/{file_name}/url"
        )


class TemperatureAPICall:
    def __init__(self, timestamp):
        # initialize logger
        logging.basicConfig()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel("INFO")
        # set up df to save data
        self.first_time = True
        self.new_df = pd.DataFrame()
        # get timestamps
        self.station_names_check = None
        self.timestamp = timestamp

    def nc_to_csv(self, filepath, x, max_keys):
        # Change nc to df
        ds = xr.open_dataset(filepath)
        df = ds.to_dataframe().reset_index()
        station_names = df['stationname'].tolist()

        # Check each stationname of the new file to the stationnames of the first files
        if self.first_time == True:
            self.first_time = False
            self.station_names_check = df['stationname'].tolist()
            self.new_df['stationname'] = df['stationname']

        if station_names == self.station_names_check:
            # https://english.knmidata.nl/open-data/actuele10mindataknmistations (for documentation)
            self.new_df[df['time'].loc[0]] = (df['tn'] + df['tx']) / 2
        else:
            # if there is a difference loop over stationnames to fill
            for index, row in enumerate(self.new_df['stationname']):
                for index2, row2 in enumerate(df['stationname']):
                    if row == row2:
                        self.new_df.loc[index, df['time'].loc[0]] = (df.loc[index2, 'tn'] + df.loc[index2, 'tx']) / 2

        if x == (max_keys - 1):
            # Write to csv
            self.new_df.to_csv(f'data/temperature_data/temperature_data_{self.timestamp}.csv', index=True)

    def download_file_from_temporary_download_url(self, download_url, filename, x, max_keys):
        try:
            directory = "data/temperature_data/TempAPIData"  # Directory name
            filepath = os.path.join(directory, filename)
            with requests.get(download_url, stream=True) as r:
                r.raise_for_status()
                with open(filepath, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
        except Exception:
            self.logger.exception("Unable to download file using download URL")
            sys.exit(1)

        self.logger.info(f"Successfully downloaded dataset file to {filename}")
        self.nc_to_csv(filepath, x, max_keys)

    def main(self):
        api_key = "eyJvcmciOiI1ZTU1NGUxOTI3NGE5NjAwMDEyYTNlYjEiLCJpZCI6ImRmYjZjMjQyMDU0OTRiZTY4OTcwMjUxOWUzNWI1MzVjIiwiaCI6Im11cm11cjEyOCJ9"
        dataset_name = "Actuele10mindataKNMIstations"
        dataset_version = "2"

        api = OpenDataAPI(api_token=api_key)

        # since the filenames are prefixed with a timestamp, we can use the current date to filter the files
        # and start listing files after the first file of the day
        max_keys = 144
        begin = f"KMDS__OPER_P___10M_OBS_L2_{self.timestamp}"

        self.logger.info(f"Fetching files of {dataset_name} version {dataset_version} on {self.timestamp}")

        # order the files by filename and begin listing after the specified filename
        params = {"order_by": "filename", "begin": begin, "maxKeys": f"{max_keys}"}
        response = api.list_files(dataset_name, dataset_version, params)
        response_full_list = response
        if "error" in response:
            self.logger.error(f"Unable to retrieve list of files: {response['error']}")
            sys.exit(1)

        # As each 10 minutes is one file loop through the files to retrieve the right data
        for x in range(response_full_list['resultCount']):
            # print("repsonse", response_full_list)
            file_name = response_full_list["files"][x].get("filename")
            self.logger.info(f"File handled {self.timestamp} is: {file_name}")

            # fetch the download url and download the file
            response = api.get_file_url(dataset_name, dataset_version, file_name)
            self.download_file_from_temporary_download_url(response["temporaryDownloadUrl"], file_name, x, max_keys)
