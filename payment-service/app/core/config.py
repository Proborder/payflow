from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    PROVIDER_HOST: str
    PROVIDER_PORT: int

    KAFKA_BOOTSTRAP_SERVERS_HOST: str
    KAFKA_BOOTSTRAP_SERVERS_PORT: int

    @property
    def DB_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def PROVIDER_URL(self):
        return f"http://{self.PROVIDER_HOST}:{self.PROVIDER_PORT}"

    @property
    def KAFKA_BOOTSTRAP_URL(self):
        return f"{self.KAFKA_BOOTSTRAP_SERVERS_HOST}:{self.KAFKA_BOOTSTRAP_SERVERS_PORT}"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
