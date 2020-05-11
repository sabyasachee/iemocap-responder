import re

def parse_body(text):
    lines = re.split(r"[\r\n]+", text)
    first_name = lines[2][11:].strip()
    last_name = lines[3][10:].strip()
    email = lines[4].strip()
    
    i = 6
    affiliation_lines = []
    while i < len(lines):
        if lines[i] == "Department / Group":
            i += 1
            break
        affiliation_lines.append(lines[i])
        i += 1
    affiliation = "\n".join(affiliation_lines)
    
    department_lines = []
    while i < len(lines):
        if lines[i] == "Title":
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