import sys
import re
import json

def parse_line(line):

    m = re.match("^\\[[^ ]*\\]", line)
    if m:
        return ("id", line)

    m = re.match("^\\{(.*)\\}", line)
    if m:
        return ("directive", m.group(1))

    m = re.match("^#+ *(.*)$", line)
    if m:
        return ("heading", m.group(1))

    m = re.match("^-(.*)-$", line)
    if m:
        return ("speaker", m.group(1))

    m = re.match("^\\((.*)\\)", line)
    if m:
        return ("mood", m.group(1))

    m = re.match("^(INT\\.|EXT\\.)", line)
    if m:
        return ("location", line)

    m = re.match("^MUSIC: *(.*)$", line)
    if m:
        return ("music", m.group(1))

    m = re.match("^> *(.*) *<$", line)
    if m:
        return ("end", m.group(1).strip())

    return ("text", line)

lines = [line.strip() for line in sys.stdin.readlines()]
lines = [line.replace("\u00e2\u20ac\u2122", "'") for line in lines]
lines = [parse_line(line) for line in lines if line != ""]

doc = {}

m = re.search('^(Episode|EPISODE) (\\d+): (.*)', lines[0][1])
if m:
    doc["episodeNumber"] = m.group(2)
    doc["title"] = m.group(3)
doc["locations"] = []
current_location = None
current_shot = None
current_dialog = None


in_body = False
for line in lines:

    if line[0] == "location":
        if current_dialog:
            current_shot['dialog'].append(current_dialog)
            current_dialog = None
        if current_shot:
            current_location['shots'].append(current_shot)
            current_shot = None
        if current_location:
            doc["locations"].append(current_location)
        in_body = True
        current_location = {
                'location': line[1],
                'intro': [],
                'shots': []
                }

    elif line[0] == "end":
        break

    if line[0] == "music" or line[0] == "directive":
        pass

    elif line[0] == "id":
        if current_dialog:
            current_shot['dialog'].append(current_dialog)
            current_dialog = None
        if current_shot:
            current_location['shots'].append(current_shot)
        m = re.search("^\\[([^]]*)\\] *(.*)$", line[1])
        current_shot = m.group(1)
        action_text = m.group(2)
        current_shot = {
                'id': current_shot,
                'actions': [{'para': action_text}],
                'dialog': []
                }
        in_dialog = False

    elif line[0] == "speaker":
        current_dialog = {'speaker': line[1], 'lines': []}

    elif line[0] == "mood":
        if current_dialog:
            current_dialog['mood'] = line[1]

    elif line[0] == "text":
        if current_dialog:
            current_dialog["lines"].append({'line': line[1]})
        elif current_shot:
            current_shot['actions'].append({'text': line[1]})

if current_shot:
    current_location['shots'].append(current_shot)

if current_location:
    doc["locations"].append(current_location)

print(json.dumps(doc, indent=2))
