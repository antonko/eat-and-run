import gel

from common.configuration import configuration

gel_client = gel.create_async_client(
    host=configuration.gel_host,
    port=configuration.gel_port,
    user=configuration.gel_user,
    password=configuration.gel_password,
    branch=configuration.gel_branch,
    tls_security=configuration.gel_tls_security,
)
