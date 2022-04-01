# from __future__ import print_function
#
# import os.path
# import io
# from zipfile import ZipFile
#
# from google.auth.transport.requests import Request
# from google.oauth2 import service_account
# from googleapiclient.discovery import build
# from googleapiclient.errors import HttpError
# from googleapiclient.http import MediaIoBaseDownload, MediaDownloadProgress
#
# SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
#
#
# def download_sleep_backup(file_id):
#   credentials = service_account.Credentials.from_service_account_file('/workspaces/core/homeassistant/components/sleep_as_android/credentials.json', scopes=SCOPES)
#   service = build('drive', 'v3', credentials=credentials)
#
#   request = service.files().get_media(fileId=file_id)
#   fh = io.BytesIO()
#   downloader = MediaIoBaseDownload(fh, request)
#   done = False
#   while done is False:
#     status, done = downloader.next_chunk()
#     print(f'Download {int(status.progress() * 100)}')
#   print('Download complete!\n')
#   unzipped = extract_zip(fh)
#   for name, content in unzipped.items():
#     print(name)
#     print(content.decode('utf-8'))
#     print()
#
#
#
# def extract_zip(in_memory_zip: io.BytesIO):
#   input_zip = ZipFile(in_memory_zip)
#   return {name: input_zip.read(name) for name in input_zip.namelist()}
#
#
# if __name__ == '__main__':
#   download_sleep_backup('1TJlO4y-vEcDOY_sVsAbM50F02v-mRZ4I')