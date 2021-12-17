"""Wrapper for making calls to Perspective API via Google Cloud Platform

@author Utkarsh Patel <imutkarshpatel@gmail.com>
"""

from googleapiclient import discovery
import time
from copy import deepcopy

ATTRIBUTES_ALLOWED = ['TOXICITY', 'IDENTITY_ATTACK', 'INSULT', 'THREAT', 'SEXUALLY_EXPLICIT']
QPS_DEFAULT = 1
ATTRIBUTES_DEFAULT = ['TOXICITY']


class Caller:
    """Wrapper for Caller API"""

    def __init__(self,
                 api_key: str,
                 qps: int = QPS_DEFAULT,
                 attributes: list[str] = ATTRIBUTES_DEFAULT):
        """Routine to initialize Caller object
        --------------------------------------
        Input
        :param api_key: API Key from Google Cloud Platform
        :param qps: query per second allowed by Perspective API
        :param attributes: attributes for which the scores are required
        """
        self._client = discovery.build('commentanalyzer', 'v1alpha1',
                                       developerKey=api_key,
                                       discoveryServiceUrl='https://commentanalyzer.googleapis.com/$discovery/rest?version=v1alpha1',
                                       cache_discovery=False)
        self._qps = qps
        self._attributes = attributes

    def score(self, text: str) -> dict:
        """Return scores for the given text"""
        return self._parse_response(self._get_response(text))

    @property
    def qps(self) -> int:
        return self._qps

    @qps.setter
    def qps(self, qps: int):
        """Change the qps limit of the Caller"""
        self._qps = qps

    def add_attribute(self, attribute: str):
        """Routine to extend the attributes for scores
        ----------------------------------------------
        Input
        :param attribute: attribute you want to add (must exist in ATTRIBUTES_ALLOWED)

        Prints a warning message in case of any exception
        """
        if attribute in self._attributes:
            pass
        elif attribute in ATTRIBUTES_ALLOWED:
            self._attributes.append(attribute)
        else:
            print(f'Warning: Attribute {attribute} is not supported, try again.')

    @property
    def attributes(self) -> list[str]:
        return self._attributes

    @attributes.setter
    def attributes(self, attributes: list[str]):
        """Routine to change the attributes of the Caller
        -------------------------------------------------
        Prints a warning in case of any exception
        """
        if len(attributes) == 0:
            print('Warning: Expected non-empty set of attributes for Caller object')
            return
        for attribute in attributes:
            if attribute not in ATTRIBUTES_ALLOWED:
                print(f'Warning: Attribute {attribute} is not supported, try again.')
                return
        self._attributes = deepcopy(attributes)

    def _parse_response(self, response: dict) -> dict:
        """Routine to converts the response of the API to dictionary of scores
        ----------------------------------------------------------------------
        Input
        :param response: response of the Perspective API
        """
        scores = dict()
        for attribute in self._attributes:
            scores[attribute] = None
        if response is None:
            return scores
        for attribute in self._attributes:
            scores[attribute] = response['attributeScores'][attribute]['summaryScore']['value']
        return scores

    def _gen_request(self, text: str) -> dict:
        """Routine to generate request to Perspective API
        -------------------------------------------------
        Input
        :param text: text for which request has to be generated
        """
        request = dict()
        request['comment']['text'] = text
        request['languages'] = ['en']
        for attribute in self._attributes:
            request['requestedAttributes'][attribute] = dict()
        return request

    def _get_response(self, text: str) -> dict:
        """Routine to make call to Perspective API and return the response
        ------------------------------------------------------------------
        Input
        :param text: Text for which scores are to be computed

        Prints a warning message in case of any exception
        """
        time.sleep(1.001 / self._qps)
        response = None
        try:
            response = self._client.comments().analyze(body=self._gen_request(text)).execute()
        except Exception as e:
            print(f'Warning: {e}')
        return response
