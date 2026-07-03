"""
Classes and Function to deal with interrupting the code
"""

class ServiceExitError(Exception):
    """
    Custom exception which is used to trigger the clean exit
    of all running threads and the main program.
    """

    pass


class FlagSetError(Exception):

    pass