import os

import hydra
import uvicorn
from fastapi import Depends, FastAPI, Header, HTTPException, status
from omegaconf import DictConfig
from pydantic import BaseModel

from api.builders.openai_builder import bill_parser


class BillRequest(BaseModel):
    image_url: str
    bill_type: str


# Dependency to extract and validate the API key from request headers
def api_key_validator(api_key: str = Header(None, alias="INVOICE_API_KEY")):
    expected_api_key = os.getenv("INVOICE_API_KEY")
    if api_key != expected_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )


# Since Hydra is designed primarily for command-line applications, we'll adapt it for use with FastAPI by manually initializing it
hydra.core.global_hydra.GlobalHydra.instance().clear()
hydra.initialize(config_path="conf", version_base="1.3")
cfg = hydra.compose(config_name="config")

app = FastAPI()


# Dependency that provides the Hydra configuration to routes
def get_config():
    return cfg


@app.post("/parse-bill", dependencies=[Depends(api_key_validator)])
def parse_bill(request: BillRequest, cfg: DictConfig = Depends(get_config)):
    system_prompt = cfg.prompts[request.bill_type].system_prompt
    response = bill_parser(
        api_key=cfg.openai.api_key,
        model=cfg.openai.vision_model,
        system_prompt=system_prompt,
        image_url=request.image_url,
    )
    return {"parsed_bill": response}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
