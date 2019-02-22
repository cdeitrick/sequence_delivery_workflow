# coding: utf-8
from __future__ import unicode_literals

import json

from .base_object import BaseObject
from ..util.text_enum import TextEnum
from ..util.api_call_decorator import api_call


class CascadePolicyConflictResolution(TextEnum):
    PRESERVE_EXISTING = 'none'
    OVERWRITE = 'overwrite'


class MetadataCascadePolicy(BaseObject):
    """Represents a metadata cascade policy, which applies folder metadata to files in that folder."""

    _item_type = 'metadata_cascade_policy'

    def get_url(self, *args):
        """
        Base class override to account for the correct pluralization.

        :rtype:
            `unicode`
        """
        return self._session.get_url('metadata_cascade_policies', self.object_id, *args)

    @api_call
    def force_apply(self, conflict_resolution):
        """
        Applies the metadata values on the folder to all files within the folder.  The conflict resolution
        parameter determines how conflicts when the same metadata template is already applied to a file will be
        handled; either the file's existing values or the folder values can be given precendence.

        :param conflict_resolution:
            How conflicting metadata values should be reolved
        :type conflict_resolution:
            :class:`CascadePolicyConflictResolution`
        :returns:
            Whether the force application succeeded.
        :rtype:
            `bool`
        """
        url = self.get_url('apply')
        body = {
            'conflict_resolution': conflict_resolution,
        }
        response = self._session.post(url, data=json.dumps(body), expect_json_response=False)
        return response.ok
