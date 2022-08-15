LIST_PATTERN = {"get": "list"}
CREATE_PATTERN = {"post": "create"}

RETRIEVE_PATTERN = {"get": "retrieve"}
UPDATE_PATTERN = {"put": "update"}
PARTIAL_UPDATE_PATTERN = {"patch": "partial_update"}
DESTROY_PATTERN = {"delete": "destroy"}

STANDARD_PATTERN = {**LIST_PATTERN, **CREATE_PATTERN}
STANDARD_DETAIL_PATTERN = {
    **RETRIEVE_PATTERN,
    **UPDATE_PATTERN,
    **PARTIAL_UPDATE_PATTERN,
    **DESTROY_PATTERN,
}

RETRIEVE_UPDATE_PATTERN = {
    **RETRIEVE_PATTERN,
    **UPDATE_PATTERN,
    **PARTIAL_UPDATE_PATTERN,
}
RETRIEVE_DESTROY_PATTERN = {**RETRIEVE_PATTERN, **DESTROY_PATTERN}
UPDATE_DESTROY_PATTERN = {**UPDATE_PATTERN, **DESTROY_PATTERN}