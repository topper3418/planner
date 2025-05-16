class PlannerError(Exception):
    """Base class for all planner-related exceptions."""

    pass


###########################################################################
#                                DB ERRORS                                #
###########################################################################


class DatabaseError(PlannerError):
    """Base class for all database-related exceptions."""

    pass


class MigrationError(DatabaseError):
    """Exception raised for errors during migration."""

    pass


class CreateDBObjectError(DatabaseError):
    """Exception raised for errors during object creation."""

    pass


class SaveDBObjectError(DatabaseError):
    """Exception raised for errors during saving an object."""

    pass


###########################################################################
#                             PROCESSOR ERRORS                            #
###########################################################################


class ProcessorError(PlannerError):
    """Base class for all processor-related exceptions."""

    pass


class ProcessCreateError(ProcessorError):
    """Exception raised for errors during the creation process."""

    pass


class ProcessUpdateError(ProcessorError):
    """Exception raised for errors during the update process."""

    pass
