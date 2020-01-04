#!/usr/bin/env python

import json
import uuid
import time

import dialogflow_v2 as dialogflow

from google.protobuf import field_mask_pb2
from google.protobuf.json_format import MessageToDict


class Dialogflow(object):
    """ Client for Dialogflow API methods """

    def __init__(self, session_id=None):
        self.project_id = "nira-68681"
        self.language_code = "en"

        self.session_id = session_id
        self.entity_types_cache = []

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
        clietn = dialogflow.SessionsClient()

        session_path = clietn.session_path(self.project_id, session_id)
        print('Session path: {}\n'.format(session_path))

        text_input = dialogflow.types.TextInput(text=text, language_code=self.language_code)

        query_input = dialogflow.types.QueryInput(text=text_input)
        response = clietn.detect_intent(session=session_path, query_input=query_input)

        print('=' * 20)
        print('Query text: {}'.format(response.query_result.query_text))
        print('Detected intent: {} \n'.format(response.query_result.intent.display_name))
        print('Fulfillment text: {}\n'.format(response.query_result.fulfillment_text))
        print('Query result: {}\n'.format(response.query_result))

    def update_intent(self, display_name, training_phrases_parts):
        """Updates an intent with the given training phrases."""

        client = dialogflow.IntentsClient()
        intent_id = self.get_intent_id(display_name)
        intent = self.get_intent(intent_id)
        training_phrases = self.get_training_phrases(training_phrases_parts)

        print("intent", intent, training_phrases)

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

        client = dialogflow.IntentsClient()
        intent_path = client.intent_path(self.project_id, intent_id)
        return client.get_intent(intent_path, intent_view=dialogflow.enums.IntentView.INTENT_VIEW_FULL)

    def list_intents(self):
        """ List all intents from chatbot """

        client = dialogflow.IntentsClient()
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
            client = dialogflow.EntityTypesClient()
            parent = client.project_agent_path(self.project_id)
            self.entity_types_cache = list(client.list_entity_types(parent))
        return self.entity_types_cache

    def get_entity_type(self, entity_type_id):
        """ Get entity type by id """
        client = dialogflow.EntityTypesClient()
        name = client.entity_type_path(self.project_id, entity_type_id)

        return client.get_entity_type(name)

    def create_entity_type(self, display_name, kind):
        """Create an entity type with the given display name."""
        client = dialogflow.EntityTypesClient()

        parent = client.project_agent_path(self.project_id)
        entity_type = dialogflow.types.EntityType(display_name=display_name, kind=kind)

        response = client.create_entity_type(parent, entity_type)

        print("Entity type created:\n{}".format(response))

    """
        ENTITIES
    """

    def create_entity(self, entity_type_id, entity_value, synonyms):
        """Create an entity of the given entity type."""
        client = dialogflow.EntityTypesClient()
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
        client = dialogflow.IntentsClient()
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
                        text=training_phrases_part['text'], entity_type=training_phrases_part['entity_type'], alias=training_phrases_part['alias'])
                else:
                    part = dialogflow.types.Intent.TrainingPhrase.Part(
                        text=training_phrases_part['text'])
                parts.append(part)
            training_phrase = dialogflow.types.Intent.TrainingPhrase(parts=parts)
            training_phrases.append(training_phrase)

        intent.training_phrases.extend(training_phrases)
        response = client.update_intent(intent, language_code='en',
                                        update_mask=dialogflow.types.FieldMask(paths=['training_phrases']))

        print('Intent {} updated'.format(intent_name))

    def create_intent(self, display_name, training_phrases_parts, message_texts):
        """Create an intent of the given intent type."""
        intents_client = dialogflow.IntentsClient()

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

        print('Intent created: {}'.format(response))

    def train_agent(self, callback):
        intents_client = dialogflow.AgentsClient()
        parent = intents_client.project_path(self.project_id)

        print('Training agent {}...'.format(self.project_id))

        begin_training = time.time()
        response = intents_client.train_agent(parent)
        response.add_done_callback(callback)

        return begin_training

    def create_set(self, entity):
        result_set = set([])
        if isinstance(entity, dict):
            result_set = set(entity.values())
        elif isinstance(entity, str) or isinstance(entity, unicode):
            result_set = set([entity])
        elif isinstance(entity, list):
            result_set = set([])
            for l in entity:
                if isinstance(l, dict):
                    result_set.union(set(l.values()))
        return result_set

    def get_diff_set(self, entity_a, entity_b):
        diff_set = {}
        for c in entity_a:
            if c not in entity_b:
                diff_set[c] = entity_a[c]
            else:
                t1 = self.create_set(entity_a[c])
                t2 = self.create_set(entity_b[c])

                diff = list(t1.difference(t2))
                if c in diff_set:
                    diff_set[c].append(diff)
                else:
                    diff_set[c] = diff
        return diff_set

    def get_diff_len(self, diff_set):
        return sum([len(x) for x in diff_set.values()])

    def detect_intent_texts(self, intents):
        """
            Returns the result of detect intent with texts as inputs.

            Using the same `session_id` between requests allows continuation of the conversation.
        """

        session_client = dialogflow.SessionsClient()

        session = session_client.session_path(self.project_id, self.session_id)

        result = []

        for intent in intents:
            text = ''.join([i['text'] for i in intent])

            text_input = dialogflow.types.TextInput(text=text, language_code=self.language_code)
            query_input = dialogflow.types.QueryInput(text=text_input)

            response = session_client.detect_intent(session=session, query_input=query_input)

            query_result = MessageToDict(response.query_result)

            correct_entities = {}
            recognized_entities = {}

            for part in intent:
                if 'entity_type' in part:
                    correct_entities[part['alias']] = part['text'].split()

            for part in query_result['parameters']:
                if query_result['parameters'][part]:
                    recognized_entities[part] = query_result['parameters'][part]

            false_negative = self.get_diff_set(correct_entities, recognized_entities)
            false_positive = self.get_diff_set(recognized_entities, correct_entities)

            result.append({
                'text': response.query_result.query_text,
                'tp': self.get_diff_len(recognized_entities) - self.get_diff_len(false_positive),
                'fp': self.get_diff_len(false_positive),
                'tn': self.get_diff_len(query_result['parameters']) - self.get_diff_len(recognized_entities) - self.get_diff_len(false_negative),
                'fn': self.get_diff_len(false_negative),
                'recognized_entities': ''.join(['@{},'.format(ent) for ent in recognized_entities.keys()])
            })

            # print('Query text: {}'.format(response.query_result.query_text))
            # print('Detected intent: {} (confidence: {})\n'.format)
            #     response.query_result.intent.display_name,
            #     response.query_result.intent_detection_confidence))

        return result
