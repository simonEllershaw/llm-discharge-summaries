import json
from typing import Dict, List, Union

import jsonref
import pandas as pd
import pydantic

from discharge_summaries.openai_llm.chat_models import AzureOpenAIChatModel
from discharge_summaries.schemas.message import Message, Role


def _json_ref_dict_to_dict(json_ref_dict: Dict) -> Dict:
    for k, v in json_ref_dict.items():
        if v is jsonref.JsonRef:
            json_ref_dict[k] = _json_ref_dict_to_dict(dict(v))
        elif v is dict:
            json_ref_dict[k] = _json_ref_dict_to_dict(v)
    return json_ref_dict


def _remove_key_from_schema(schema: Union[Dict, List, str], remove_key: str):
    if isinstance(schema, dict):
        if remove_key in schema.keys():
            del schema[remove_key]
        for key in schema.keys():
            _remove_key_from_schema(schema[key], remove_key)
    elif isinstance(schema, list):
        for item in schema:
            _remove_key_from_schema(item, remove_key)


def pydantic_def_to_simplified_json_schema(
    pydantic_schema: pydantic.main.ModelMetaclass,
) -> Dict:
    json_schema = jsonref.loads(pydantic_schema.schema_json(), jsonschema=True)
    json_schema = _json_ref_dict_to_dict(json_schema)
    if "definitions" in json_schema.keys():
        json_schema.pop("definitions")

    _remove_key_from_schema(json_schema, "required")
    # Keep top level title
    _remove_key_from_schema(json_schema["properties"], "title")
    return json_schema


def remove_filled_fields_from_schema(schema: Dict, filled_schema: Dict) -> Dict:
    for key, value in filled_schema.items():
        if isinstance(value, dict):
            schema[key]["properties"] = {
                property_key: property_value
                for property_key, property_value in remove_filled_fields_from_schema(
                    schema[key]["properties"], value
                ).items()
                if property_value
            }
        else:
            if value:
                del schema[key]
    return schema


def query_llm_to_fill_json_schema(
    physician_notes: pd.DataFrame, schema: Dict, llm: AzureOpenAIChatModel
) -> Dict:
    system_message = Message(
        role=Role.SYSTEM,
        content="""You are a consultant doctor tasked with completing a section of a patients discharge summary according to a json schema.
The output must be in json.
The output json must follow the schema provided by the user.
Only the information in the physician notes provided by the user can be used for this task.
If the information is not present to fill in a field, answer it with an empty list or string.
""",
    )

    notes_string = "\n\n".join(
        [
            f"Physician Note {idx+1}: {note['CHARTTIME']}\n{note['TEXT']}"
            for idx, note in physician_notes.iterrows()
        ]
    )
    user_message = Message(
        role=Role.USER,
        content=f"""Complete a section of a discharge summary according to the following json schema {json.dumps(schema)}

Use only information from the following notes\n\n{notes_string}""",
    )
    print(system_message)
    print(user_message)
    response = llm.query([system_message, user_message])
    print(response.content)
    return json.loads(response.content)
