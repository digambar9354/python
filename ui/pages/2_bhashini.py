import streamlit as st
import os
import asyncio

import httpx
import os
from jugalbandi.core import (
    Language,
    InternalServerException,
)
import json

bhashini_user_id = os.getenv('BHASHINI_USER_ID')
bhashini_api_key = os.getenv('BHASHINI_API_KEY')
bhashini_pipleline_id = os.getenv('BHASHINI_PIPELINE_ID')

bhashini_inference_url = "https://dhruva-api.bhashini.gov.in/services/inference/pipeline"

def on_btn_click(document_title, from_lang, to_lang):
    if (document_title and from_lang and to_lang):
        output = asyncio.run(translate_text(document_title, from_lang, to_lang))
        st.write(output)
    else:
        st.write(output)

def main():
    st.markdown("# Bhashini text translation")
    st.sidebar.markdown("# Bhashini")

    searched_text = st.text_input("Enter text to convert:")
    
    from_lang = st.selectbox(
    "Convert from",
        ("EN", "MR"),
        index=None,
        placeholder="Select Language...",
    )

    st.write('You selected:', from_lang)

    to_lang = st.selectbox(
    "Convert to",
        ("EN", "MR"),
        index=None,
        placeholder="Select Language...",
    )

    st.write('You selected:', to_lang)

    st.button("Convert", on_click=on_btn_click(searched_text, from_lang ,to_lang ))


async def perform_bhashini_config_call( task: str,
    source_language: str,
    target_language: str | None = None):
    url = "https://meity-auth.ulcacontrib.org/ulca/apis/v0/model/getModelsPipeline"
    if task in ['asr', 'tts']:
        payload = json.dumps({
            "pipelineTasks": [
                {
                    "taskType": task,
                    "config": {
                        "language": {
                            "sourceLanguage": source_language
                        }
                    }
                }
            ],
            "pipelineRequestConfig": {
                "pipelineId": "64392f96daac500b55c543cd"
            }
        })
    else:
        payload = json.dumps({
            "pipelineTasks": [
                {
                    "taskType": "translation",
                    "config": {
                        "language": {
                            "sourceLanguage": source_language,
                            "targetLanguage": target_language
                        }
                    }
                }
            ],
            "pipelineRequestConfig": {
                "pipelineId": bhashini_pipleline_id
            }
        })
    headers = {
        'userID': bhashini_user_id,
        'ulcaApiKey': bhashini_api_key,
        'Content-Type': 'application/json'
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, data=payload)  # type: ignore

    return response.json()

async def translate_text(
    text: str, source_language: Language, destination_language: Language
) -> str:
    source = source_language.lower()
    destination = destination_language.lower()

    bhashini_translation_config = await perform_bhashini_config_call(
        task='translation', source_language=source, target_language=destination)

    payload = json.dumps({
        "pipelineTasks": [
            {
                "taskType": "translation",
                "config": {
                    "language": {
                        "sourceLanguage": bhashini_translation_config['languages'][0]['sourceLanguage'],
                        "targetLanguage": bhashini_translation_config['languages'][0]['targetLanguageList'][
                            0]
                    },
                    "serviceId": bhashini_translation_config['pipelineResponseConfig'][0]['config'][0][
                        'serviceId']
                }
            }
        ],
        "inputData": {
            "input": [
                {
                    "source": text
                }
            ]
        }
    })
    headers = {
        'Accept': '*/*',
        'User-Agent': 'Thunder Client (https://www.thunderclient.com)',
        bhashini_translation_config['pipelineInferenceAPIEndPoint']['inferenceApiKey']['name']:
            bhashini_translation_config['pipelineInferenceAPIEndPoint']['inferenceApiKey']['value'],
        'Content-Type': 'application/json'
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url=bhashini_inference_url,
    headers=headers,
    data=payload)  # type: ignore
    if response.status_code != 200:
        raise InternalServerException(
            f"Request failed with response.text: {response.text} and "
                f"status_code: {response.status_code}")
    
    indicText = response.json()['pipelineResponse'][0]['output'][0]['target']

    return indicText


if __name__ == "__main__":
    main()