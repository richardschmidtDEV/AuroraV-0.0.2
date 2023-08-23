import xml.etree.ElementTree as ET

def parse_cpe_dictionary(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    cpes = {}

    # Loop through the elements of the XML file, extracting the relevant data
    for item in root.findall(".//cpe-item"):
        title = item.find(".//title").text
        # Assuming 'cpe23:cpe' is the attribute containing the actual CPE identifier
        cpe23 = item.get('name')
        cpes[title] = cpe23

    return cpes

def search_cpe(cpes, user_input):
    results = [cpe for title, cpe in cpes.items() if user_input.lower() in title.lower()]
    return results

if __name__ == "__main__":
    file_path = "official-cpe-dictionary_v2.3.xml"
    cpes = parse_cpe_dictionary(file_path)
    
    user_input = input("Enter a product or keyword to search for: ")
    results = search_cpe(cpes, user_input)

    print("Results:")
    for result in results[:5]:  # Print the first 5 entries to check
        print(result)
