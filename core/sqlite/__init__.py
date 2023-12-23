import sqlite3
from typing import Union
import re
import time
import random
import contextlib

class SQLITEDATABASE:
    def __init__(self, client: sqlite3.Cursor, table_name: str):
        self.client = client
        self.table_name = table_name


    def handle_insert_list(self, table_name, data_type, data, random_id, key_name):
        self.client.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({key_name} {data_type})")
        for value in data:
            self.client.execute(f"INSERT INTO {table_name} VALUES ({value})")
        return random_id, table_name


    def insert(self, data: Union[dict, list], key_name: str = None):
        random_id = generate_unique_5_digit_number()
        table_name = self.table_name
        if key_name:
            table_name = key_name if "_table" in key_name else f"{key_name}_table"
        if table_name.endswith("_list_table"):
            table_name += f"_{random_id}"
        if isinstance(data, list):
            type_of_data = "INT" if all(isinstance(x, int) for x in data) else "TEXT"
            return self.handle_insert_list(table_name, type_of_data, data, random_id, key_name)
        elif isinstance(data, dict):
            return self.handle_insert_dict(table_name, data, random_id)

    def handle_insert_dict(self, table_name, data, random_id):
        self.client.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        table_exists = self.client.fetchone()
        if not table_exists:
            column_names = ""
            for key, value in data.items():
                if isinstance(value, str):
                    column_names += f"{key} TEXT, "
                elif isinstance(value, int):
                    column_names += f"{key} INT, "
                elif isinstance(value, list):
                    column_names += f"{key}_list_table TEXT, "
                elif isinstance(value, dict):
                    column_names += f"{key}_dict_table TEXT, "
            self.client.execute(f"CREATE TABLE {table_name} (_id INTEGER PRIMARY KEY, {column_names[:-2]})")
        to_insert_columns = ""
        to_insert_values = ""
        for key, value in data.items():
            if isinstance(value, str):
                to_insert_columns += f"{key}, "
                to_insert_values += f"'{value}', "
            elif isinstance(value, int):
                to_insert_columns += f"{key}, "
                to_insert_values += f"{value}, "
            elif isinstance(value, list):
                generated_id, generated_table_name = self.insert(value, f"{key}_list_table")
                to_insert_columns += f"{key}_list_table, "
                to_insert_values += f"'{generated_id}_lt', "
            elif isinstance(value, dict):
                generated_id, generated_table_name = self.insert(value, f"{key}_dict")
                to_insert_columns += f"{key}_dict_table, "
                to_insert_values += f"'{generated_id}_dt', "
        self.client.execute(f"INSERT INTO {table_name} (_id, {to_insert_columns[:-2]}) VALUES ({random_id}, {to_insert_values[:-2]})")
        return random_id, table_name

    def find(self, data: dict, tb_name=None, type_of_data=None):
        table_name = tb_name or self.table_name
        if type_of_data == "list":
            sql_cmd = f"SELECT * FROM {table_name}"
            self.client.execute(sql_cmd)
            returned_data = self.client.fetchall()
            return [data[0] for data in returned_data]
        if data in (None, {}):
            sql_cmd = f"SELECT * FROM {table_name}"
        else:
            sql_cmd = f"SELECT * FROM {table_name} WHERE "
            for key, value in data.items():
                if isinstance(value, str):
                    sql_cmd += f"{key}='{value}' AND "
                elif isinstance(value, int):
                    sql_cmd += f"{key}={value} AND "
            sql_cmd = sql_cmd[:-4]
        self.client.execute(sql_cmd)
        returned_data = self.client.fetchall()
        returned_data = [list(x) for x in returned_data]
        self.client.execute(f"PRAGMA table_info({table_name})")
        table_info = self.client.fetchall()
        column_names = [column[1] for column in table_info]
        for x in returned_data:
            for y, m in zip(x, column_names):
                if isinstance(y, str) and y.endswith("_dt"):
                    raw_name = m.split("_dict_table")[0]
                    find_data = {"_id": y.split("_dt")[0]}
                    if data.get(raw_name):
                        find_data |= data.get(raw_name)
                    found_data: dict = self.find(find_data, m)
                    if isinstance(found_data, dict) and found_data.get("_id"):
                        found_data.pop("_id")
                    if found_data in (None, []):
                        print("mm", returned_data)
                        print("xx", returned_data[returned_data.index(x)])
                        continue
                    print("td", returned_data)
                    returned_data[returned_data.index(x)][x.index(y)] = found_data
                elif isinstance(y, str) and y.endswith("_lt"):
                    raw_name = m.split("_list_table")[0]
                    find_data = data.get(raw_name)
                    id_ = y.split("_lt")[0]
                    found_data = self.find(find_data, f"{m}_{id_}", "list")
                    if found_data in (None, []):
                        print("yy", returned_data[x])
                        continue
                    returned_data[returned_data.index(x)][x.index(y)] = found_data
        data_to_return = [dict(zip(self.return_clean_name(column_names), r_data)) for r_data in returned_data]
        return data_to_return[0] if len(data_to_return) == 1 else data_to_return
    

    def return_clean_name(self, column_names):
        return [x.split("_list_table")[0] if x.endswith("_list_table") else x.split("_dict_table")[0] if x.endswith("_dict_table") else x for x in column_names]



def generate_unique_5_digit_number():
    timestamp = int(time.time() * 1000)
    random_suffix = random.randint(0, 99999)
    return (timestamp % 100000) * 100000 + random_suffix


_client = sqlite3.connect("test.db").cursor()
client = SQLITEDATABASE(_client, "x_tble")
client.insert({"helo": "xi", "test": {"x": {"l": "c"}}, "p": [1, 2, 3]})
client.insert({"helo": "xi", "test": {"x": {"l": "k"}}, "p": [1, 2, 3]})
print(client.find({"helo": "xi", "test": {"x": {"l": "k"}}}))