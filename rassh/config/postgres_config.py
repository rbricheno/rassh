from contrary import Contrary
from os import getenv


env_file_path_name = "RASSH_POSTGRES_CONFIG_FILE"
env_secrets_path_name = "RASSH_POSTGRES_SECRETS_FILE"
# Path relative to documentation build root, for sphinx build
or_default_file_path = "../rassh/config/postgres_config.yaml"
or_default_secrets_path = "../rassh/config/postgres_secrets.yaml"
if __name__ == "__main__" or __name__ == "rassh.config.postgres_config":
    # Real path
    or_default_file_path = "/etc/rassh/postgres_config.yaml"
    or_default_secrets_path = "/etc/rassh/postgres_secrets.yaml"
config_file_path = getenv(env_file_path_name, or_default_file_path)
config_secrets_path = getenv(env_secrets_path_name, or_default_secrets_path)


class PostgresConfig(Contrary):
    def __init__(self):
        super().__init__([config_file_path, config_secrets_path])
