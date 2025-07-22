import datetime
import json
import requests
import pandas as pd
from src.util import settings, logger
from bs4 import BeautifulSoup
import urllib.request
import urllib.parse
import urllib.error
import io
import re


class engine(object):

    def __init__(self):
        self.logger = logger.RotatingLogger(__name__).getLogger()

    """description of class"""

    def get_data_from_url(self, url, return_type="text"):
        r = requests.get(url)
        if return_type == "json":
            data = r.json()
        else:
            data = r.text
        return data

    def get_csv_data_from_url(self, url, header_location_regex=None):
        """
            byte: header_location_regex: if the first row is not the header
            provide "col1,col2" string to skip the no header rows

            from src.services import webcrawler
            e = webcrawler.engine()
        """
        user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        headers={'User-Agent':user_agent,}
        request=urllib.request.Request(url,None,headers) #The assembled request
        csv = urllib.request.urlopen(request).read()
        if header_location_regex:
            csv = csv[csv.index(header_location_regex):]
        data = pd.read_csv(io.BytesIO(csv))
        return data

    def get_data_from_table(self, url, table_selector={"id": "hist"}):
        r = requests.get(url)
        data = r.text
        soup = BeautifulSoup(data, 'html.parser')
        table = soup.find("table", table_selector)
        table_body = table.find('tbody')
        table_header = table.find('thead')
        if table_header:
            header_row = table_header.find('tr')
            headers = [ele.text.strip() for ele in header_row.find_all('th')]
        else:
            self.logger.info("Table header not found")
            header_row = headers = None
        rows = table_body.find_all(
            'tr') if table_body else table.find_all('tr')
        data_rows = []
        for row in rows:
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            # Get rid of empty values        print
            data_rows.append([ele for ele in cols if ele])
        data = headers + data_rows if table_header else data_rows
        return data

    def get_data_from_tables(self, url, table_selector={"id": "hist"}):
        r = requests.get(url)
        data = r.text
        soup = BeautifulSoup(data, 'html.parser')
        tables = soup.findAll("table", table_selector)
        all_rows = []
        for table in tables:
            table_body = table.find('tbody')
            table_header = table.find('thead')
            if table_header:
                header_row = table_header.find('tr')
                headers = [ele.text.strip()
                           for ele in header_row.find_all('th')]
            else:
                header_row = headers = None
            rows = table_body.find_all(
                'tr') if table_body else table.find_all('tr')
            data_rows = []
            for row in rows:
                cols = row.find_all('td')
                cols = [ele.text.strip() for ele in cols]
                # Get rid of empty values        print
                data_rows.append([ele for ele in cols if ele])
            rows = headers + data_rows if table_header else data_rows
            all_rows = all_rows + rows
        return all_rows

    def get_html_tables(self, html_data, url=None, table_class=None, table_attrs=None):
        if not html_data and url:
            html_data = requests.get(url).text
        soup = BeautifulSoup(html_data, 'html.parser')
        tables = []
        if table_class:
            tables = soup.findAll("table", {"class": table_class})
        elif table_attrs:
            tables = soup.findAll("table", table_attrs)
        else:
            return soup.findAll("table")
        return tables

    def get_data_from_html_table(self, html_data, table_class, url=None, table_attrs=None,
    header_lambda=None, column_lambda=None, header_extractor={},
    column_extractor={}):
        '''
            column_lambda: Use column lambda to transform a value in text field of td
            column_extractor: dictionary: defines a function to extract value from td, either a class, style etc
        '''
        if not html_data and url:
            html_data = requests.get(url).text
        data = []
        for table in self.get_html_tables(html_data, table_class=table_class, table_attrs=table_attrs):
            table_body = table.find('tbody')
            table_header = table.find('thead')
            header_row = table_header.find('tr')
            headers = [ele.text.strip().replace(' ', '')
                       for ele in header_row.find_all('th')]
            if header_lambda:
                headers = [header_lambda(x) for x in headers]
            for key, value in header_extractor.items():
                headers[key] = value(headers)
            rows = table_body.find_all('tr')
            data_rows = []
            for row in rows:
                cols = row.find_all(['td', 'th'])
                cols = [ele.text.strip() for ele in cols]
                for key, value in column_extractor.items():
                    cols[key] = value(row)
                if column_lambda:
                    cols = [column_lambda(x) for x in cols]
                # Get rid of empty values        print
                data_rows.append([ele for ele in cols])
            for row in data_rows:
                data.append(dict(list(zip(headers, row))))
            data_without_empty_keys = []
            for row in data:
                data_without_empty_keys.append(
                    dict((k, v) for k, v in row.items() if k))
            data = data_without_empty_keys
        return data

    def get_data_from_html_table_ignore_missing_tags(self, table, header_lambda=None, column_lambda=None, header_extractor={}, column_extractor={},
                                                     first_row_is_header_row=False,
                                                     th_is_present_thead_absent=False):
        '''
            Provide soup html table
            column_lambda: Use column lambda to transform a value in text field of td
            column_extractor: dictionary: defines a function to extract value from td, either a class, style etc
        '''
        headers = self.get_table_headers(table, header_lambda=header_lambda, column_lambda=column_lambda,
                                         header_extractor=header_extractor, th_is_present_thead_absent=th_is_present_thead_absent)
        # Rows
        table_body = table.find('tbody')
        rows = table_body.find_all(
            'tr') if table_body else table.find_all('tr')
        data_rows = []
        for row in rows:
            cols = row.find_all(['td', 'th'])
            cols = [ele.text.strip() for ele in cols]
            for key, value in column_extractor.items():
                cols[key] = value(row)
            if column_lambda:
                cols = [column_lambda(x) for x in cols]
            # Get rid of empty values        print
            data_rows.append([ele for ele in cols])
        # If no thead use first row as header
        if not headers and first_row_is_header_row:
            headers = data_rows[0]
            data_rows = data_rows[1:]
        # If headers present, use headers to create dictionaries of key value pairs.
        if headers:
            return self.join_headers_and_data(headers, data_rows)
        else:
            # Return list of rows
            return data_rows

    def get_table_headers(self, table, header_lambda=None, column_lambda=None,
                          header_extractor={}, th_is_present_thead_absent=False):
        # Get headers from table
        # Headers
        table_header = table.find('thead')
        headers = []
        if table_header:
            header_row = table_header.find('tr')
            headers = [ele.text.strip().replace(' ', '')
                       for ele in header_row.find_all('th')]
            if header_lambda:
                headers = [header_lambda(x) for x in headers]
            for key, value in header_extractor.items():
                headers[key] = value(headers)
        elif th_is_present_thead_absent:
            headers = [ele.text.strip().replace(' ', '')
                       for ele in table.find_all('th')]
        return headers

    def join_headers_and_data(self, headers, data_rows):
        # Joins headers and data rows to return dictonary of header + column mapped
        # If there is no data but only headers returns headers
        if any([any(item) for item in data_rows]):
            data = []
            for row in data_rows:
                data.append(dict(list(zip(headers, row))))
            data_without_empty_keys = []
            # If there is no header, ignore the column
            for row in data:
                data_without_empty_keys.append(
                    dict((k, v) for k, v in row.items() if k))
            return data_without_empty_keys
        else:
            return headers

    def sanitize(self, value):
        try:
            return re.sub(r'[^\x00-\x7F]+', '', value.replace('\n', '').replace('\r', '').replace('\t', '').replace(' ', '').replace('\\u', ''))
        except:
            self.logger.error('Failed to process quote', exc_info=True)
        return None

    def get_data_from_table_of_elements(self, url, root_element, parent_element, child_element_key, child_element_value, parent_div_class=None, row_div_class=None, col_div_class_key=None, col_div_class_value=None):
        '''
            Provide soup html table
            root_element: eg: div/ul
            parent_element: eg: div/li
            child_element: eg:div/span
            parent_div_class: parent div that contains row divs
            row_div_class: row div that contains column divs
            col_div_class_key: column div that contains key
            col_div_class_value: column div that contains values
        '''
        data = self.get_data_from_url(url)
        soup = BeautifulSoup(data, 'html.parser')

        def get_key_value(data):
            if col_div_class_key == col_div_class_value:
                value = None
                if len(data.findAll(child_element_value, {"class": col_div_class_value})) == 2:
                    value = self.sanitize(data.findAll(child_element_value, {
                                          "class": col_div_class_value})[1].text)
                return {self.sanitize(data.findAll(child_element_key, {"class": col_div_class_key})[0].text): value}
            else:
                value = None
                if data.find(child_element_value, {"class": col_div_class_value}):
                    value = self.sanitize(data.find(child_element_value, {
                                          "class": col_div_class_value}).text)
                return {self.sanitize(data.find(child_element_key, {"class": col_div_class_key}).text): value}

        return [get_key_value(x) for x in soup.find(root_element, {"class": parent_div_class}).findAll(parent_element, {"class": row_div_class})]
