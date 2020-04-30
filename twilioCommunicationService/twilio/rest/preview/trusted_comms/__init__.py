# coding=utf-8
r"""
This code was generated by
\ / _    _  _|   _  _
 | (_)\/(_)(_|\/| |(/_  v1.0.0
      /       /
"""

from twilio.base.version import Version
from twilio.rest.preview.trusted_comms.branded_call import BrandedCallList
from twilio.rest.preview.trusted_comms.business import BusinessList
from twilio.rest.preview.trusted_comms.cps import CpsList
from twilio.rest.preview.trusted_comms.current_call import CurrentCallList
from twilio.rest.preview.trusted_comms.phone_call import PhoneCallList


class TrustedComms(Version):

    def __init__(self, domain):
        """
        Initialize the TrustedComms version of Preview

        :returns: TrustedComms version of Preview
        :rtype: twilio.rest.preview.trusted_comms.TrustedComms.TrustedComms
        """
        super(TrustedComms, self).__init__(domain)
        self.version = 'TrustedComms'
        self._branded_calls = None
        self._businesses = None
        self._cps = None
        self._current_calls = None
        self._phone_calls = None

    @property
    def branded_calls(self):
        """
        :rtype: twilio.rest.preview.trusted_comms.branded_call.BrandedCallList
        """
        if self._branded_calls is None:
            self._branded_calls = BrandedCallList(self)
        return self._branded_calls

    @property
    def businesses(self):
        """
        :rtype: twilio.rest.preview.trusted_comms.business.BusinessList
        """
        if self._businesses is None:
            self._businesses = BusinessList(self)
        return self._businesses

    @property
    def cps(self):
        """
        :rtype: twilio.rest.preview.trusted_comms.cps.CpsList
        """
        if self._cps is None:
            self._cps = CpsList(self)
        return self._cps

    @property
    def current_calls(self):
        """
        :rtype: twilio.rest.preview.trusted_comms.current_call.CurrentCallList
        """
        if self._current_calls is None:
            self._current_calls = CurrentCallList(self)
        return self._current_calls

    @property
    def phone_calls(self):
        """
        :rtype: twilio.rest.preview.trusted_comms.phone_call.PhoneCallList
        """
        if self._phone_calls is None:
            self._phone_calls = PhoneCallList(self)
        return self._phone_calls

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        return '<Twilio.Preview.TrustedComms>'
