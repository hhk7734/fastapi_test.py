from pydantic_settings import BaseSettings, SettingsConfigDict


class K8sConfig(BaseSettings):
    pod_name: str
    pod_namespace: str

    model_config = SettingsConfigDict(env_file=".env")


class Config(BaseSettings):
    debug: bool = False
    k8s = K8sConfig()

    model_config = SettingsConfigDict(env_file=".env")


config = Config()
