import json
import xmltodict

def save_xml_to_json(xml_file_path, json_file_path):
    with open(xml_file_path) as xml_file:
        data_dict = xmltodict.parse(xml_file.read())
        json_data = json.dumps(data_dict)        
        with open(json_file_path, "w") as json_file:
            json_file.write(json_data)
