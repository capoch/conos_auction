class AgentNotAuthorized(Exception):
    #Philipp: Added location to __init__
    def __init__(self, action, location):
        Exception.__init__(
            self,
            "Agent not authorized to perform action %s on %s." %
            (action, location))


class ContractorNotEligible(Exception):
    def __init__(self, reason='Account disabled.'):
        Exception.__init__(
            self,
            'Contractor not eligible to place bid. Reason: %s' % (reason)
        )
