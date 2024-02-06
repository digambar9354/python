import httpx
import os
from abc import ABC, abstractmethod
from google.cloud.translate import TranslationServiceAsyncClient
from jugalbandi.core import (
    Language,
    InternalServerException,
)
import json
import uuid
import aiohttp


class Translator(ABC):
    @abstractmethod
    async def translate_text(
        self, text: str, source_language: Language, destination_language: Language
    ) -> str:
        pass


class DhruvaTranslator(Translator):
    def __init__(self):
        self.bhashini_user_id = os.getenv('BHASHINI_USER_ID')
        self.bhashini_api_key = os.getenv('BHASHINI_API_KEY')
        self.bhashini_pipleline_id = os.getenv('BHASHINI_PIPELINE_ID')
        self.bhashini_inference_url = "https://dhruva-api.bhashini.gov.in/services/inference/pipeline"

    async def perform_bhashini_config_call(self,
                                           task: str,
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
                    "pipelineId": self.bhashini_pipleline_id
                }
            })
        headers = {
            'userID': self.bhashini_user_id,
            'ulcaApiKey': self.bhashini_api_key,
            'Content-Type': 'application/json'
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, data=payload)  # type: ignore

        return response.json()

    async def translate_text(
        self, text: str, source_language: Language, destination_language: Language
    ) -> str:
        source = source_language.name.lower()
        destination = destination_language.name.lower()

        bhashini_translation_config = await self.perform_bhashini_config_call(
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
            response = await client.post(url=self.bhashini_inference_url,
                                         headers=headers,
                                         data=payload)  # type: ignore
        if response.status_code != 200:
            raise InternalServerException(
                f"Request failed with response.text: {response.text} and "
                  f"status_code: {response.status_code}")

        indicText = response.json()['pipelineResponse'][0]['output'][0]['target']
        return indicText


class AzureTranslator(Translator):
    def __init__(self):
        self.subscription_key = os.getenv('AZURE_TRANSLATION_KEY')
        self.resource_location = os.getenv('AZURE_TRANSLATION_RESOURCE_LOCATION')
        self.endpoint = "https://api.cognitive.microsofttranslator.com"

    async def translate_text(
            self, text: str, source_language: Language, destination_language: Language
    ) -> str:
        path = '/translate'
        constructed_url = self.endpoint + path

        if source_language.name == 'ZH':
            source_language_code = 'zh-Hans'
        else:
            source_language_code = source_language.name.lower()

        if destination_language.name == 'ZH':
            destination_language_code = 'zh-Hans'
        else:
            destination_language_code = destination_language.name.lower()

        params = {
            'api-version': '3.0',
            'from': source_language_code,
            'to': destination_language_code
        }
        headers = {
            'Ocp-Apim-Subscription-Key': self.subscription_key,
            'Ocp-Apim-Subscription-Region': self.resource_location,
            'Content-type': 'application/json',
            'X-ClientTraceId': str(uuid.uuid4())
        }
        body = [{'text': text}]

        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            async with session.post(constructed_url, params=params, headers=headers, json=body) as response:
                response = await response.json()
                return response[0]['translations'][0]['text']

    async def transliterate_text(self, text: str, source_language: Language, from_script: str, to_script: str) -> str:
        path = '/transliterate'
        constructed_url = self.endpoint + path

        params = {
            'api-version': '3.0',
            'language': source_language.name.lower(),
            'fromScript': from_script,
            'toScript': to_script
        }
        headers = {
            'Ocp-Apim-Subscription-Key': self.subscription_key,
            'Ocp-Apim-Subscription-Region': self.resource_location,
            'Content-type': 'application/json',
            'X-ClientTraceId': str(uuid.uuid4())
        }
        body = [{'text': text}]

        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            async with session.post(constructed_url, params=params, headers=headers, json=body) as response:
                response = await response.json()
                print(response)
                return response[0]['text']


class GoogleTranslator(Translator):
    async def translate_text(
        self, text: str, source_language: Language, destination_language: Language
    ) -> str:
        client = TranslationServiceAsyncClient()
        location = "global"
        # TODO: make the project_id versatile
        project_id = "indian-legal-bert"
        parent = f"projects/{project_id}/locations/{location}"
        response = await client.translate_text(
            request={
                "parent": parent,
                "contents": [text],
                "mime_type": "text/plain",
                "source_language_code": source_language.name.lower(),
                "target_language_code": destination_language.name.lower(),
            }
        )
        return response.translations[0].translated_text


class CompositeTranslator(Translator):
    def __init__(self, *translators: Translator):
        self.translators = translators

    async def translate_text(
        self, text: str, source_language: Language, destination_language: Language
    ) -> str:
        if source_language.value == destination_language.value:
            return text

        excs = []
        for translator in self.translators:
            try:
                print("INSIDE THIS translator", translator)
                return await translator.translate_text(
                    text, source_language, destination_language
                )
            except Exception as exc:
                excs.append(exc)

        raise ExceptionGroup("CompositeTranslator translation failed", excs)
