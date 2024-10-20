import os

from pyppeteer import executablePath
from pydantic import BaseSettings, Field
from typing import Literal, Union


class BaseConfig(BaseSettings):
    environment: Literal["production", "staging", "localhost"]
    app_version: str = "0.1.0"
    v1_url_prefix: str = "/api/v1"

    host_address: str = "0.0.0.0"
    host_port: int = 8000
    workers_count: int = 7
    default_timeout: int = 15

    root_folder: str = os.path.dirname(__file__)
    logfile_store: str = root_folder
    temp_file_archive: str = f"{root_folder}/temp_archive"

    browser_path: str = Field(default_factory=executablePath)
    user_data_dir_path: str
    whatsapp_web_url: str = Field(default="https://web.whatsapp.com")
    whatsapp_web_send_button_selector: str = Field(
        default="#main > footer > div.x1n2onr6.xhtitgo.x9f619.x78zum5.x1q0g3np.xuk3077.x193iq5w.x122xwht.x1bmpntp.xs9asl8.x1swvt13.x1pi30zi.xnpuxes.copyable-area > div > span > div > div._ak1r > div.x123j3cw.xs9asl8.x9f619.x78zum5.x6s0dn4.xl56j7k.x1ofbdpd.x100vrsf.x1fns5xo > button"
    )
    max_cached: float = Field(default=100)  # max cached items in store
    cache_ttl: float = Field(default=18_000)  # 5 hours in seconds

    class Config:
        case_sensitive = False
        env_file = ".env"
        extra = "allow"


class ProdConfig(BaseConfig):
    environment: Literal["production"]
    log_level: Literal["INFO", "WARNING", "ERROR", "CRITICAL"] = Field(default="INFO")
    debug: bool = False
    reload_app: bool = False


class DevConfig(BaseConfig):
    environment: Literal["staging", "localhost"]
    log_level: Literal["DEBUG"] = "DEBUG"
    workers_count: int = 1
    debug: bool = True
    reload_app: bool = True


def get_configuration() -> Union[DevConfig, ProdConfig]:
    environment_name = BaseConfig().environment
    config = {"staging": DevConfig, "production": ProdConfig}
    configuration_class = config.get(environment_name, DevConfig)
    return configuration_class()


config = get_configuration()
