class PlannerError(Exception):
    """Base class for all planner-related exceptions."""

    pass


class MigrationError(PlannerError):
    """Exception raised for errors during migration."""

    pass
