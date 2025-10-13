import os
import zipfile
from xml.etree.ElementTree import Element, SubElement, ElementTree

problems = [
    {
        "question": "What is the capital of France?",
        "type": "multiple_choice",
        "options": ["Paris", "London", "Berlin", "Madrid"],
        "answer": ["Paris"]
    },
    {
        "question": "Select all the vowels.",
        "type": "multiple_answer",
        "options": ["a", "e", "k", "o", "u"],
        "answer": ["a", "e", "o", "u"]
    },
    {
        "question": "What is the capital of Italy?",
        "type": "short_answer",
        "answer": ["Rome", "rome"]
    }
]

# Sets a working folder to collect all generated XML files before zipping.
# exist_ok=True prevents crashes if the folder already exists 
base_dir = "downloads/qti2.1"
os.makedirs(base_dir, exist_ok=True)

# Set the namespace for the XML files so tools (like Canvas) recognize the schema.
ns = "http://www.imsglobal.org/xsd/imsqti_v2p1"

# Create a test container
assessment = Element("assessmentTest", {
    "xmlns": ns,
    "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
    "xsi:schemaLocation": f"{ns} imsqti_v2p1.xsd",
    "identifier": "assessment",
    "title": "Assessment"
})

test_part = SubElement(assessment, "testPart", {
    "identifier": "part1",
    "navigationMode": "Linear",
    "submissionMode": "Individual"
})

assessment_section = SubElement(test_part, "assessmentSection", {
    "identifier": "section1",
    "title": "Section 1"
    "visible": "true"
})

# Create question files
for i, problem in enumerate(problems, start=1):
    
    # Structure the question file
    item_filename = f"q{i}.xml"
    SubElement(assessment_section, "assessmentItemRef", {
        "identifier": f"q{i}",
        "href": item_filename,
        "required": "true"
    })

    item = Element("assessmentItem", {
        "xmlns": ns,
        "identifier": f"q{i}",
        "title": "",
        "adaptive": "false",
        "timeDependent": "false"
    })
 
    # Response declarations
    qtype = problem["type"]
    baseType = "identifier"
    cardinality = "single"

    if qtype == "multiple_answer":
        cardinality = "multiple"
    elif qtype == "short_answer":
        baseType = "string"
    
    response_declaration = SubElement(item, "responseDeclaration", {
        "identifier": "RESPONSE",
        "cardinality": cardinality,
        "baseType": baseType
        })
    

if __name__ == "__main__":
    convert_to_qti_2_1()