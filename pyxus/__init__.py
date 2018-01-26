import os

from pyxus.config import ENV_VAR_NEXUS_PREFIX, ENV_VAR_NEXUS_NAMESPACE, ENV_VAR_NEXUS_ENDPOINT, ENV_VAR_BLAZEGRAPH


def _check_env_variable(key):
    if key not in os.environ:
        raise ValueError("The environment variable {} is not set!".format(key))


_check_env_variable(ENV_VAR_NEXUS_ENDPOINT)
_check_env_variable(ENV_VAR_NEXUS_PREFIX)
_check_env_variable(ENV_VAR_NEXUS_NAMESPACE)
_check_env_variable(ENV_VAR_BLAZEGRAPH)

pass
