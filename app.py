# app.py
import streamlit as st
import pandas as pd
import json

class PhoneBookReader:
    def __init__(self, data):
        self.data = data

    def read_phone_book_records(self):
        """
        Read phone book records based on the provided data.

        Returns:
            list: A list of dictionaries representing phone book records.
        """
        try:
            if isinstance(self.data, pd.DataFrame):
                phone_book_records = self._read_dataframe()
            elif isinstance(self.data, list):
                phone_book_records = self._read_list()
            else:
                raise ValueError("Unsupported data format. Please provide a DataFrame or a list of dictionaries.")
        except Exception as e:
            st.error(f"Error reading phone book records: {e}")
            phone_book_records = []

        return phone_book_records

    def _read_dataframe(self):
        """
        Read phone book records from a DataFrame.

        Returns:
            list: A list of dictionaries representing phone book records.
        """
        phone_book_records = self.data[['name', 'email', 'phone1', 'phone2']].to_dict(orient='records')
        return phone_book_records

    def _read_list(self):
        """
        Read phone book records from a list.

        Returns:
            list: A list of dictionaries representing phone book records.
        """
        phone_book_records = self.data
        return phone_book_records

def main():
    st.title("Phone Book Reader Web App")
    uploaded_file = st.file_uploader("Upload CSV or JSON file", type=["csv", "json"])

    if uploaded_file is not None:
        try:
            # Determine file type based on extension
            file_extension = uploaded_file.name.split(".")[-1].lower()

            if file_extension == "json":
                data = json.load(uploaded_file)
                # Convert JSON to DataFrame and select desired columns
                data = pd.DataFrame(data)[['name', 'email', 'phone1', 'phone2']]
            elif file_extension == "csv":
                data = pd.read_csv(uploaded_file)
            else:
                st.warning("Unsupported file format. Please upload a CSV or JSON file.")
                return

            phone_book_reader = PhoneBookReader(data)
            records = phone_book_reader.read_phone_book_records()

            st.subheader("Phone Book Records:")
            if records:
                st.write(pd.DataFrame(records))
            else:
                st.warning("No records found or an error occurred.")
        except json.JSONDecodeError as e:
            st.error(f"Error decoding JSON: {e}")
        except pd.errors.EmptyDataError:
            st.warning("The uploaded CSV file is empty.")
        except pd.errors.ParserError as e:
            st.error(f"Error parsing CSV file: {e}")
        except Exception as e:
            st.error(f"Error processing file: {e}")

if __name__ == "__main__":
    main()
