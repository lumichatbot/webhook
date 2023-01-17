#!/usr/bin/env python

import os
import json
import uuid
import time

import dialogflow_v2 as dialogflow

from google.oauth2 import service_account
from google.protobuf import field_mask_pb2
from google.protobuf.json_format import MessageToDict


class Dialogflow(object):
    """ Client for Dialogflow API methods """

    def __init__(self, evaluation=False):
        raw_credentials = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
        service_account_info = json.loads(raw_credentials)
        self.credentials = service_account.Credentials.from_service_account_info(service_account_info)
        self.project_id = "lumieval-nkkjoi" if evaluation else "nira-68681"
        self.language_code = "en"

        self.entity_types_cache = []

    """
        AGENT
    """

    def get_agent(self):
        client = dialogflow.AgentsClient(credentials=self.credentials)
        parent = client.project_path(self.project_id)
        return client.get_agent(parent)

    def train_agent(self, callback):
        client = dialogflow.AgentsClient(credentials=self.credentials)
        parent = client.project_path(self.project_id)

        print('Training agent {}...'.format(self.project_id))

        begin_training = time.time()
        response = client.train_agent(parent)
        response.add_done_callback(callback)

        return begin_training

    """
        TRAINING PHRASES
    """

    def get_training_phrases(self, training_phrases_parts):
        """ Creates and returns a training phrases objects from parts """
        training_phrases = []
        for training_phrases_part in training_phrases_parts:
            part = dialogflow.types.Intent.TrainingPhrase.Part(text=training_phrases_part)
            training_phrase = dialogflow.types.Intent.TrainingPhrase(parts=[part])
            training_phrases.append(training_phrase)

        return training_phrases

    """
        INTENTS
    """

    def detect_intent(self, text, session_id=str(uuid.uuid4())):
        """Returns the result of detect intent with texts as inputs.
        Using the same `session_id` between requests allows continuation of the conversaion."""
        client = dialogflow.SessionsClient(credentials=self.credentials)

        session_path = client.session_path(self.project_id, session_id)
        print('Session path: {}\n'.format(session_path))

        text_input = dialogflow.types.TextInput(text=text, language_code=self.language_code)

        query_input = dialogflow.types.QueryInput(text=text_input)
        response = client.detect_intent(session=session_path, query_input=query_input)

        # print('=' * 20)
        # print('Query text: {}'.format(response.query_result.query_text))
        # print('Detected intent: {} \n'.format(response.query_result.intent.display_name))
        # print('Fulfillment text: {}\n'.format(response.query_result.fulfillment_text))
        # print('Fulfillment messages: {}\n'.format(response.query_result.fulfillment_messages))
        # print('Query result: {}\n'.format(response.query_result))

        return response

    def update_intent(self, display_name, training_phrases_parts):
        """Updates an intent with the given training phrases."""

        client = dialogflow.IntentsClient(credentials=self.credentials)
        intent_id = self.get_intent_id(display_name)
        intent = self.get_intent(intent_id)
        training_phrases = self.get_training_phrases(training_phrases_parts)

        intent.training_phrases.extend(training_phrases)
        update_mask = field_mask_pb2.FieldMask(paths=['training_phrases'])
        response = client.update_intent(intent, self.language_code, update_mask)

        print("Intent updated: {}".format(response))

    def get_intent_id(self, display_name):
        """ Get entity type id """

        intents = self.list_intents()
        intent_id = None
        for intent in intents:
            if intent.display_name == display_name:
                intent_id = intent.name.split("/intents/")[1]
        return intent_id

    def get_intent(self, intent_id):
        """ Get intent by id """

        client = dialogflow.IntentsClient(credentials=self.credentials)
        intent_path = client.intent_path(self.project_id, intent_id)
        return client.get_intent(intent_path, intent_view=dialogflow.enums.IntentView.INTENT_VIEW_FULL)

    def list_intents(self):
        """ List all intents from chatbot """

        client = dialogflow.IntentsClient(credentials=self.credentials)
        parent = client.project_agent_path(self.project_id)

        return list(client.list_intents(parent))

    def get_entity_type_id(self, display_name):
        """ Get entity type id """
        entity_types = self.list_entity_types()
        entity_type_id = None
        for entity_type in entity_types:
            if entity_type.display_name == display_name:
                entity_type_id = entity_type.name.split("/entityTypes/")[1]
        return entity_type_id

    def list_entity_types(self):
        """ List all entity types """
        if not self.entity_types_cache:
            client = dialogflow.EntityTypesClient(credentials=self.credentials)
            parent = client.project_agent_path(self.project_id)
            self.entity_types_cache = list(client.list_entity_types(parent))
        return self.entity_types_cache

    def get_entity_type(self, entity_type_id):
        """ Get entity type by id """
        client = dialogflow.EntityTypesClient(credentials=self.credentials)
        name = client.entity_type_path(self.project_id, entity_type_id)

        return client.get_entity_type(name)

    def create_entity_type(self, display_name, kind):
        """Create an entity type with the given display name."""
        client = dialogflow.EntityTypesClient(credentials=self.credentials)

        parent = client.project_agent_path(self.project_id)
        entity_type = dialogflow.types.EntityType(display_name=display_name, kind=kind)

        response = client.create_entity_type(parent, entity_type)

        print("Entity type created:\n{}".format(response))

    """
        ENTITIES
    """

    def create_entity(self, entity_type_id, entity_value, synonyms):
        """Create an entity of the given entity type."""
        client = dialogflow.EntityTypesClient(credentials=self.credentials)
        # Note: synonyms must be exactly [entity_value] if the
        # entity_type"s kind is KIND_LIST
        synonyms = synonyms or [entity_value]
        entity_type_path = client.entity_type_path(self.project_id, entity_type_id)

        entity = dialogflow.types.EntityType.Entity()
        entity.value = entity_value
        entity.synonyms.extend(synonyms)

        response = client.batch_create_entities(entity_type_path, [entity])
        print("Entity created: \n{}".format(response))

    def tag_entities(self, training_phrase):
        """ Receives text training phrase and returns traning phrase parts tagged with entities """

        training_phrase_parts = []
        return training_phrase_parts

    def update_intent(self, intent_id, training_phrases_parts, keep_phrases=True):
        print('Updating intents...')
        client = dialogflow.IntentsClient(credentials=self.credentials)
        intent_name = client.intent_path(self.project_id, intent_id)
        intent_view = None
        if keep_phrases:
            intent = client.get_intent(intent_name, intent_view=dialogflow.enums.IntentView.INTENT_VIEW_FULL)
        else:
            intent = client.get_intent(intent_name)
        training_phrases = []
        for phrases in training_phrases_parts:
            parts = []
            for training_phrases_part in phrases:
                part = None
                if 'entity_type' in training_phrases_part:
                    part = dialogflow.types.Intent.TrainingPhrase.Part(
                        text=training_phrases_part['text'],
                        entity_type=training_phrases_part['entity_type'],
                        alias=training_phrases_part['alias'] if 'alias' in training_phrases_part else "")
                else:
                    part = dialogflow.types.Intent.TrainingPhrase.Part(
                        text=training_phrases_part['text'])
                parts.append(part)
            training_phrase = dialogflow.types.Intent.TrainingPhrase(parts=parts)
            training_phrases.append(training_phrase)

        intent.training_phrases.extend(training_phrases)
        response = client.update_intent(intent, language_code='en',
                                        update_mask=dialogflow.types.FieldMask(paths=['training_phrases']))

        # print('Intent {} updated'.format(intent_name))

    def create_intent(self, display_name, training_phrases_parts, message_texts):
        """Create an intent of the given intent type."""
        intents_client = dialogflow.IntentsClient(credentials=self.credentials)

        parent = intents_client.project_agent_path(self.project_id)
        training_phrases = []
        parts = []
        training_phrases = []
        for phrases in training_phrases_parts:
            parts = []
            for training_phrases_part in phrases:
                part = None
                if 'entity_type' in training_phrases_part:
                    part = dialogflow.types.Intent.TrainingPhrase.Part(
                        text=training_phrases_part['text'], entity_type=training_phrases_part['entity_type'], alias=training_phrases_part['alias'])
                else:
                    part = dialogflow.types.Intent.TrainingPhrase.Part(
                        text=training_phrases_part['text'])
                parts.append(part)
            training_phrase = dialogflow.types.Intent.TrainingPhrase(parts=parts)
            training_phrases.append(training_phrase)

        text = dialogflow.types.Intent.Message.Text(text=message_texts)
        message = dialogflow.types.Intent.Message(text=text)

        intent = dialogflow.types.Intent(
            display_name=display_name,
            training_phrases=training_phrases,
            messages=[message])

        response = intents_client.create_intent(parent, intent)

        # print('Intent created: {}'.format(response))

    """
        EVALUATION
    """

    def detect_intent_texts(self, intents, session_id=str(uuid.uuid4())):
        """
            Returns the result of detect intent with texts as inputs.

            Using the same `session_id` between requests allows continuation of the conversation.
        """

        session_client = dialogflow.SessionsClient(credentials=self.credentials)

        session = session_client.session_path(self.project_id, session_id)

        result = []
        for intent in intents:
            time.sleep(10)
            text = ''.join([i['text'] for i in intent])

            text_input = dialogflow.types.TextInput(text=text, language_code=self.language_code)
            query_input = dialogflow.types.QueryInput(text=text_input)

            response = session_client.detect_intent(session=session, query_input=query_input)

            query_result = MessageToDict(response.query_result)

            correct_entities = {}
            recognized_entities = {}

            for part in intent:
                if 'alias' in part:
                    correct_entities[part['text']] = part['alias']

            for entity, values in query_result['parameters'].items():
                if values:
                    if isinstance(values, dict):
                        for tag, value in values.items():
                            recognized_entities[value] = entity
                    elif isinstance(values, list):
                        for value in values:
                            if isinstance(value, dict):
                                for tag, v in value.items():
                                    recognized_entities[v] = entity
                            else:
                                recognized_entities[value] = entity

            # print("CORRECT ENTITIES", correct_entities)
            # print("RECOGNIED ENTITIES", recognized_entities)

            true_positives = list(set(correct_entities.values()) & set(recognized_entities.values()))
            false_positives = list(set(recognized_entities.values()) - set(correct_entities.values()))
            false_negatives = list(set(correct_entities.values()) - set(recognized_entities.values()))

            # print("TRUE POSITIVES", true_positives)
            # print("FALSE POSITIVES", false_positives)
            # print("FALSE NEGATIVES", false_negatives)

            result.append({
                'text': response.query_result.query_text,
                'tp': len(true_positives),
                'fp': len(false_positives),
                'fn': len(false_negatives),
                'recognized_entities': ''.join(['@{},'.format(ent) for ent in recognized_entities.values()]),
                'expected_entities': ''.join(['@{},'.format(ent) for ent in correct_entities.values()])
            })

            # print('Query text: {}'.format(response.query_result.query_text))
            # print('Detected intent: {} (confidence: {})\n'.format)
            #     response.query_result.intent.display_name,
            #     response.query_result.intent_detection_confidence))

        return result
