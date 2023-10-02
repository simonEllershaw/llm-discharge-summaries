import re
from typing import Dict, List

from pydantic import BaseModel
from unidecode import unidecode


def to_camel_case(text: str) -> str:
    return re.sub(r"\W+", "_", text.strip().lower())


def clean_text(text: str) -> str:
    return unidecode(text).strip()


class Row(BaseModel):
    name: str
    description: str
    cardinality: str
    data_type: str
    values: str
    do_not_use: bool

    def from_record(row: List[str]) -> "Row":
        cleaned_values = [clean_text(value) if value else "" for value in row]
        cleaned_values[0] = to_camel_case(cleaned_values[0])
        return Row(
            name=cleaned_values[0],
            description=cleaned_values[1],
            cardinality=cleaned_values[2],
            data_type=cleaned_values[3],
            values=cleaned_values[4],
            do_not_use=(cleaned_values[5] == "Y"),
        )


class Element(BaseModel):
    name: str
    description: str

    def to_json_schema_dict(self) -> Dict:
        return {
            self.name: {
                "description": self.description,
                "type": "string",
            }
        }


class ArrayElement(Element):
    def to_json_schema_dict(self) -> Dict:
        return {
            self.name: {
                "description": self.description,
                "type": "array",
                "items": {
                    "type": "string",
                },
            }
        }


class RecordElement(Element):
    items: List[Element]

    def to_json_schema_dict(self) -> Dict:
        return {
            self.name: {
                "description": self.description,
                "type": "array",
                "items": (
                    {"description": self.items[0].description, "type": "string"}
                    if len(self.items) == 1
                    else {
                        "type": "object",
                        "properties": {
                            k: v
                            for element in self.items
                            for k, v in element.to_json_schema_dict().items()
                        },
                    }
                ),
            }
        }


class ClusterElement(Element):
    elements: List[Element]

    def to_json_schema_dict(self) -> Dict:
        return {
            self.name: {
                "description": self.description,
                "type": "object",
                "properties": {
                    k: v
                    for element in self.elements
                    for k, v in element.to_json_schema_dict().items()
                },
            }
        }


class Section(BaseModel):
    name: str
    description: str
    elements: List[Element]

    def to_json_schema_dict(self) -> Dict:
        if len(self.elements) == 1 and self.elements[0].name == self.name:
            section_json_dict = self.elements[0].to_json_schema_dict()
            section_json_dict[self.name]["description"] = (
                self.description + " " + section_json_dict[self.name]["description"]
            )
        else:
            section_json_dict = {
                self.name: {
                    "description": self.description,
                    "type": "object",
                    "properties": {
                        k: v
                        for element in self.elements
                        for k, v in element.to_json_schema_dict().items()
                    },
                }
            }
        return section_json_dict
