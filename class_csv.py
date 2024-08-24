import csv
import io
import os

class CSVFile:
    def __init__(self, file_path):
        self.file_path = file_path

    def read(self):
        with io.open(self.file_path, 'r', encoding='latin-1') as file:
            reader = csv.reader(file)
            data = list(reader)
        return data

    def write(self, data):
        with io.open(self.file_path, 'w', newline='', encoding='latin-1') as file:
            writer = csv.writer(file)
            writer.writerows(data)
