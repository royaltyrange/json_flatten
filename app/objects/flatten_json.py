import json
from glob import glob
import pandas as pd
import gc
from pandas import json_normalize
from tqdm import tqdm
import collections
gc.enable()


class FlattenJson(object):
    def __init__(self, folder_path=None, encoding=None, amount_of_examples=1000):
        self.folder_paths = self.get_files_from_folder(folder_path)
        self.encoding = encoding
        self.collected_data_from_file = {}
        self.flatten_json = None
        self.flatten_json_counter = None
        self.amount_of_examples = amount_of_examples
        self.temp_examples = []
        self.examples = None

    @staticmethod
    def chunk(l, n):
        n = max(1, n)
        gc.collect()
        return list(l[i:i + n] for i in range(0, len(l), n))

    @staticmethod
    def get_files_from_folder(folder_path):
        if not folder_path.endswith('*.json'):
            folder_path = folder_path + '*.json'
        files = glob(folder_path, recursive=True)
        if len(files) == 0:
            raise ValueError("0 files in folder.")
        return files

    @staticmethod
    def flatten_dict(y, schema_name=""):
        """
        A utility function to flatten json structure into dict
        Adapted from here: https://stackoverflow.com/questions/51359783/python-flatten-multilevel-json
        :param y: dict
        :param schema_name: A optional schema name to add in front of all key names
        :return: flattened dict
        """
        out = collections.OrderedDict()
        if schema_name != '':
            schema_name = schema_name + ' => '

        def flatten(x, name=''):
            if type(x) is dict:
                for a in x:
                    if a.startswith('http://') or a.startswith('https://'):
                        flatten(x[a], name + '[url]' + ' => ')
                    else:
                        flatten(x[a], name + a + ' => ')
            elif type(x) is list:
                [flatten(a, name + '[]' + ' => ') for a in x]
            else:
                x = str(x)
                if name[:-4] not in out:
                    out[name[:-4]] = x
                else:
                    if type(out[name[:-4]]) == str:
                        out[name[:-4]] = [value for key, value in out.items() if key == name[:-4]]
                    if x not in out[name[:-4]]:
                        out[name[:-4]].append(x)
        flatten(y, schema_name)
        for key, value in out.items():
            if type(value) == list:
                out[key] = '; '.join(value[:10])
        return out

    def get_keys(self, json_input):
        flatten = self.flatten_dict(json_input)
        if len(self.temp_examples) < self.amount_of_examples:
            self.temp_examples.append(flatten)
        for key, value in flatten.items():
            if key not in self.collected_data_from_file:
                self.collected_data_from_file.update({key: {"counter": 1}})
            else:
                self.collected_data_from_file[key]["counter"] += 1
            del key, value
        del flatten, json_input

    def get_flatten(self, file_path):
        try:
            with open(file_path, 'r', encoding=self.encoding) as f:
                content = json.loads(f.read())
                self.get_keys(content)
                del f, file_path, content
        except:
            pass

    def fix_dictionary(self):
        temp_dict = []
        for key in tqdm(self.collected_data_from_file):
            counter = self.collected_data_from_file[key]["counter"]
            temp_dict.append({"key": key, "counter": counter})
            del key, counter
        self.collected_data_from_file = temp_dict
        del temp_dict

    def read_files(self):
        # Get data from files
        print(f'Getting keys from {len(self.folder_paths)} files.')
        [self.get_flatten(file_path) for file_path in tqdm(self.folder_paths)]
        del self.folder_paths
        gc.collect()

    def get_flatten_json(self):
        print(f'Fixing {len(self.collected_data_from_file)} keys.')
        self.fix_dictionary()

        print('Preparing flatten data.')
        self.flatten_json = pd.DataFrame(self.collected_data_from_file)['key']

        print('Preparing counter data.')
        self.flatten_json_counter = pd.DataFrame(self.collected_data_from_file).sort_values(
            by='counter', ascending=False
        )

        print('Preparing examples data.')
        self.examples = pd.DataFrame(json_normalize(self.temp_examples)).T
        del self.temp_examples

    def save_flatten_json_to_csv(self, output_file_name):
        print('Writing data to excel.')
        writer = pd.ExcelWriter(f"{output_file_name}.xlsx", engine='xlsxwriter')

        # write each DataFrame to a specific sheet
        self.flatten_json.to_excel(writer, sheet_name='unique keys', index=False, encoding=self.encoding)
        self.flatten_json_counter.to_excel(writer, sheet_name='count of keys', index=False, encoding=self.encoding)
        self.examples.to_excel(writer, sheet_name='examples', index=True, encoding=self.encoding)

        writer.save()

        print(f'Excel file saved:\n{output_file_name}')
        del self.flatten_json, self.flatten_json_counter, self.examples, output_file_name
        gc.collect()
