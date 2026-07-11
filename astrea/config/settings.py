"""Application configuration using Pydantic Settings."""
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR = Path(__file__).parent.parent.absolute()


class LLMSettings(BaseModel):
    allowed_providers: List[str] = ["google-vertex", "azure"]
    service_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    main_url: Optional[str] = None
    scenario_url: Optional[str] = None
    main_model: Optional[str] = None
    scenario_model: Optional[str] = None
    coder_model: Optional[str] = None
    service_url: Optional[str] = None
    service_cc_url: Optional[str] = None
    vision_url: Optional[str] = None
    summary_url: Optional[str] = None
    marker_model: Optional[str] = None


class ServicesSettings(BaseModel):
    tavily_api_key: Optional[str] = None
    openalex_api_key: Optional[str] = None
    openalex_email: Optional[str] = None


class StorageSettings(BaseModel):
    root_dir: Path = ROOT_DIR
    parse_results: Optional[str] = None
    chroma_storage: Optional[str] = None
    papers_storage: Optional[str] = None
    my_papers: Optional[str] = None
    logging_path: Optional[str] = "logs/"
    uploaded_papers: Optional[str] = None


class S3Settings(BaseModel):
    use_s3: bool = False
    endpoint_url: Optional[str] = None
    access_key: Optional[str] = None
    secret_key: Optional[str] = None
    bucket_name: Optional[str] = None


class OpikSettings(BaseModel):
    api_key: Optional[str] = None
    url_override: Optional[str] = None
    opik_project_name: Optional[str] = None


class MCPSettings(BaseModel):
    paper_analysis_url: Optional[str] = None
    papers_search_url: Optional[str] = None


class HITLSettings(BaseModel):
    enabled: bool = True


class OrchestratorSettings(BaseModel):
    use_planner: bool = True


class Settings(BaseSettings):
    """Main application settings."""

    llm: LLMSettings = LLMSettings()
    services: ServicesSettings = ServicesSettings()
    storage: StorageSettings = StorageSettings()
    s3: S3Settings = S3Settings()
    opik: OpikSettings = OpikSettings()
    hitl: HITLSettings = HITLSettings()
    orchestrator: OrchestratorSettings = OrchestratorSettings()
    mcp: MCPSettings = MCPSettings()

    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__",
        extra="ignore",
    )


settings = Settings()


def get_settings() -> Settings:
    return settings
