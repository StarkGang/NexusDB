import sqlite3
from typing import Union
import time
import random


class SQLITEDATABASE:
    def __init__(self, client: sqlite3.Cursor, table_name: str):
        self.client = client
        self.table_name = table_name

    def insert(self, data: Union[dict, list], list_name: str = None):
        """Inserts data into table"""

        orginal_key_name = None
        if list_name:
            tb_name = list_name + "_table"
        else:
            tb_name = self.table_name
        table_name = _id = None
        for key, value in data.items():
            if isinstance(value, dict):
                table_name, _id = self.insert(value, key)
        col_decide = ""
        for key, value in data.items():
            if isinstance(value, str):
                col_decide += f"{key} VARCHAR(255), "
            if isinstance(value, int):
                col_decide += f"{key} INT, "
            if isinstance(value, float):
                col_decide += f"{key} FLOAT, "
            if isinstance(value, bool):
                col_decide += f"{key} BOOLEAN, "
            if not value:
                col_decide += f"{key} NULL, "
            if isinstance(value, dict):
                orginal_key_name = key.rsplit("_table", 1)[0]
                col_decide += f"other_table_{orginal_key_name} Varchar(9), "
        col_decide = col_decide[:-2]
        id_ = generate_unique_5_digit_number()
        cmd = f"""CREATE TABLE IF NOT EXISTS {tb_name} (_id INT,{col_decide}"""
        if list_name:
            if (table_name or _id) is not None:
                orginal_key_name = table_name.rsplit("_table", 1)[0]
                cmd += f", FOREIGN KEY ({orginal_key_name}) REFERENCES {table_name}(_id)"
        cmd += ")"

        self.client.execute(cmd)
        columns = ""
        for key in data.keys():
            if key == orginal_key_name:
                columns += f"other_table_{key}, "
                continue
            columns += f"{key}, "
        columns = columns[:-2]
        values_ = ""
        for value in data.values():
            if isinstance(value, str):
                values_ += f"'{value}', "
            elif isinstance(value, bool):
                values_ += f"{value}, "
            elif isinstance(value, int):
                values_ += f"{value}, "
            elif isinstance(value, dict):
                values_ += f"'{_id}_ft', "
        values_ = values_[:-2]
        if values_:
            cmd = f"INSERT INTO {tb_name} (_id, {columns}) VALUES ({id_}, {values_})"
        else:
            cmd = f"INSERT INTO {tb_name} (_id, {columns}) VALUES ({id_})"

        self.client.execute(cmd)
        return (table_name or tb_name, id_)
    
    def find(self, m_data: dict, tb_name=None):
        """Finds data in table"""
        if tb_name:
            tb_name = tb_name
        else:
            tb_name = self.table_name
        if m_data:
            columns = ''
            for key in m_data.keys():
                if isinstance(m_data[key], dict):
                    continue
                columns += f"{key}, "
            columns = columns[:-2]
            values_ = ""
            for value in m_data.values():
                if isinstance(value, str):
                    values_ += f"'{value}', "
                if isinstance(value, dict):
                    continue
                elif isinstance(value, bool):
                    values_ += f"{value}, "
                elif isinstance(value, int):
                    values_ += f"{value}, "
            values_ = values_[:-2]
            if values_:
                cmd = f"SELECT * FROM {tb_name} WHERE {columns} = {values_}"
            else:
                cmd = f"SELECT * FROM {tb_name} WHERE {columns}"
        else:
            cmd = f"SELECT * FROM {tb_name}"

        self.client.execute(cmd)
        fetch_all = self.client.fetchall()
        self.client.execute(f"PRAGMA table_info({tb_name})")
        columns_info = self.client.fetchall()
        column_names = [column[1] for column in columns_info]
        to_return = []
        for data in fetch_all:
            x_data = dict(zip(column_names, data))
            to_return.append(x_data)
        for col in column_names:
            if col.startswith("other_table_"):
                child_table_name = col.rsplit("other_table_", 1)[1] + "_table"
                orginal_key_name = child_table_name.rsplit("_table", 1)[0]
                if orginal_key_name in m_data:
                    child_table_data = m_data[orginal_key_name]
                else:
                    child_table_data = None
                n_data = self.find(child_table_data, child_table_name)
                x_data[col] = n_data
        if len(to_return) == 1:
            return to_return[0]
        return to_return

def generate_unique_5_digit_number():
    timestamp = int(time.time() * 1000) 
    random_suffix = random.randint(0, 99999)
    unique_number = (timestamp % 100000) * 100000 + random_suffix
    return unique_number


_client = sqlite3.connect("test.db").cursor()
client = SQLITEDATABASE(_client, "x_table")
client.insert({"hello": "hi", "test": {"x": "y"}})

_client.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = _client.fetchall()

found_data = client.find({"hello": "hi", "test": {"x": "y"}})
print(found_data)


# another 
client.insert({"hello": "bye", "test": {"x": "z"}})
found_data = client.find({"hello": "bye", "test": {"x": "z"}})
print(found_data)