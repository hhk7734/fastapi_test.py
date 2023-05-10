from dotenv import load_dotenv
from pydantic import BaseSettings

load_dotenv()


class K8sConfig(BaseSettings):
    pod_name: str
    pod_namespace: str

    class Config:
        env_prefix = "k8s_"


class Config(BaseSettings):
    debug: bool = False
    k8s = K8sConfig()


config = Config()
