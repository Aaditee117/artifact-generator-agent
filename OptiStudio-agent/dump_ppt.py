import sys
import json
from pptx import Presentation

def dump(file_path):
    prs = Presentation(file_path)
    res = []
    for i, slide in enumerate(prs.slides):
        sl = []
        for shape in slide.shapes:
            if shape.has_text_frame:
                sl.append(shape.text.replace('\n', ' '))
        res.append(sl)
    return res

print("POC Template:")
print(json.dumps(dump('templates/POC template.pptx'), indent=2))
print("MVP Template:")
print(json.dumps(dump('templates/MVP template.pptx'), indent=2))
