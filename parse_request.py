# author - Sabyasachee Baruah
import re

def parse_body(text):
    '''
    parse_body parses the IEMOCAP request email body.

    Input
    =====

    text - Email body text

    Output
    ====

    A dictionary is returned. Its keys are -

        1. name
        2. affiliation
        3. email
        4. department
        5. title
        6. address

    All keys have string values
    '''

    lines = re.split(r"[\r\n]+", text)
    first_name = lines[2][11:].strip()
    last_name = lines[3][10:].strip()
    email = lines[4].strip()
    
    i = 6
    affiliation_lines = []
    while i < len(lines):
        if lines[i].startswith("Department / Group"):
            i += 1
            break
        affiliation_lines.append(lines[i])
        i += 1
    affiliation = "\n".join(affiliation_lines)
    
    department_lines = []
    while i < len(lines):
        if lines[i].startswith("Title"):
            i += 1
            break
        department_lines.append(lines[i])
        i += 1
    department = "\n".join(department_lines)
    
    title_lines = []
    while i < len(lines):
        if lines[i] == "Address":
            i += 1
            break
        title_lines.append(lines[i])
        i += 1
    title = "\n".join(title_lines)
    
    address_lines = []
    while i < len(lines):
        if lines[i] == "I agree to the release license.":
            break
        address_lines.append(lines[i])
        i += 1
    address = "\n".join(address_lines)
    
    parsed_output = dict(name=first_name + " " + last_name, email=email, affiliation=affiliation, department=department, title=title, address=address)
    
    return parsed_output