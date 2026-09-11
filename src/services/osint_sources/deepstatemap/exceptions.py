class DeepStateMapError(Exception):
    """Base exception for DeepStateMap errors."""


class DeepStateMapNotFound(DeepStateMapError):
    """Snapshot was not found for the requested date."""


class DeepStateMapClientError(DeepStateMapError):
    """Error while fetching data from DeepStateMap source."""


class DeepStateMapParseError(DeepStateMapError):
    """Error while parsing DeepStateMap data."""