import streamlit as st
import csv
import json
from io import StringIO
import pandas as pd

class PhoneBookReader:
    def __init__(self, file_content, file_name):
        self.file_content = file_content
        self.file_name = file_name
        self.file_type = self.determine_file_type()

    def determine_file_type(self):
        if "." in self.file_name:
            _, file_extension = self.file_name.rsplit(".", 1)
            return file_extension.lower()
        else:
            return None

    def read_phone_book_records(self):
        try:
            with StringIO(self.file_content) as file:
                if self.file_type == 'csv':
                    phone_book_records = self._read_csv(file)
                elif self.file_type == 'json':
                    phone_book_records = self._read_json(file)
                else:
                    raise ValueError("Unsupported file format. Please provide a CSV or JSON file.")
        except Exception as e:
            st.error(f"Error reading phone book records: {e}")
            phone_book_records = []

        return phone_book_records

    def _read_csv(self, file):
        reader = csv.DictReader(file)
        phone_book_records = [
            {'Name': record['name'], 'Email': record['email'], 'Phone 1': record['phone1'], 'Phone 2': record['phone2']}
            for record in reader
        ]
        return phone_book_records

    def _read_json(self, file):
        try:
            data = json.load(file)
            phone_book_records = [
                {'Name': record['name'], 'Email': record['email'], 'Phone 1': record['phone1'], 'Phone 2': record['phone2']}
                for record in data
            ]
            return phone_book_records
        except json.JSONDecodeError as e:
            st.error(f"Error decoding JSON: {e}")
            return []

    def execute_query(self, query):
        query_upper = query.strip().upper()
        if query_upper.startswith("SELECT * FROM PHONE_RECORDS"):
            if 'WHERE' in query_upper:
                condition = query_upper.split('WHERE')[1].strip()
                if 'NAME=' in condition:
                    value = condition.split('NAME=')[1].strip().strip("';")
                    records = self.filter_records_by_name(value)
                else:
                    st.warning("Unsupported condition. Only WHERE NAME='value' is supported.")
                    return
            else:
                records = self.read_phone_book_records()[:10]

            self.display_records_in_table(records)
        elif query_upper.startswith("INSERT INTO PHONE_RECORDS"):
            if 'VALUES' in query_upper:
                values_str = query_upper.split('VALUES')[1].strip().strip("';")
                values_list = [v.strip("',") for v in values_str.split(',')]
                new_record = {'Name': values_list[0], 'Email': values_list[1], 'Phone 1': values_list[2], 'Phone 2': values_list[3]}
                self.insert_record(new_record)
                st.success("Record inserted successfully.")
            else:
                st.warning("Invalid INSERT statement. Please provide VALUES.")
        elif query_upper.startswith("DELETE FROM PHONE_RECORDS"):
            if 'WHERE' in query_upper:
                condition = query_upper.split('WHERE')[1].strip()
                if 'NAME=' in condition:
                    value = condition.split('NAME=')[1].strip().strip("';")
                    self.delete_records_by_name(value)
                else:
                    st.warning("Unsupported condition. Only WHERE NAME='value' is supported.")
            else:
                st.warning("Invalid DELETE statement. Please provide a WHERE clause.")
        else:
            st.warning("Unsupported query. Please use SELECT, INSERT, or DELETE statements.")

    def filter_records_by_name(self, value):
        records = self.read_phone_book_records()
        filtered_records = [record for record in records if value.upper() in record['Name'].upper()]
        return filtered_records[:10]

    def delete_records_by_name(self, value):
        records = self.read_phone_book_records()
        updated_records = [record for record in records if value.upper() not in record['Name'].upper()]
        self.display_records_in_table(updated_records[:10])  # Display the first 10 records

    def insert_record(self, new_entry):
        records = self.read_phone_book_records()
        records.insert(0, new_entry)  # Insert at the beginning
        self.display_records_in_table(records[:10])  # Display the first 10 records

    def display_records_in_table(self, records):
        if not records:
            st.info("No records to display.")
            return

        # Convert records to Pandas DataFrame
        df = pd.DataFrame(records)

        st.table(df)

# Streamlit UI
st.title("CRUD Operations Streamlit App")

# File Uploader
file_uploaded = st.file_uploader("Upload CSV or JSON file", type=["csv", "json"])

# Execute Query Section
if file_uploaded is not None:
    file_content = file_uploaded.getvalue().decode("utf-8")
    file_name = file_uploaded.name
    phone_book_reader = PhoneBookReader(file_content, file_name)

    # Display file details
    st.subheader("File Details:")
    st.write(f"**Name:** {file_name}")
    st.write(f"**File Type:** {phone_book_reader.file_type}")
    st.write(f"**File Size:** {file_uploaded.size}")

    # User Query Section
    user_query = st.text_input("Enter SQL query:")
    if st.button("Execute Query"):
        # Execute the user query
        phone_book_reader.execute_query(user_query)
