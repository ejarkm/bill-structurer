import os
import shutil
from tempfile import NamedTemporaryFile

import hydra
import uvicorn
from fastapi import Depends, FastAPI, Header, HTTPException, UploadFile, File, Form, status
from omegaconf import DictConfig
from pydantic import BaseModel

from api.builders.openai_builder import bill_parser


class BillType(BaseModel):
    bill_type: str  # Simplified model for demonstration


# Dependency to extract and validate the API key from request headers
def api_key_validator(api_key: str = Header(None, alias="INVOICE_API_KEY")):
    expected_api_key = os.getenv("INVOICE_API_KEY")
    if api_key != expected_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )


hydra.core.global_hydra.GlobalHydra.instance().clear()
hydra.initialize(config_path="conf", version_base="1.3")
cfg = hydra.compose(config_name="config")

app = FastAPI()


# Dependency that provides the Hydra configuration to routes
def get_config():
    return cfg


@app.post("/parse-bill")
def parse_bill(
    bill_type: str = Form(...),
    uploaded_file: UploadFile = File(...),
    cfg: DictConfig = Depends(get_config),
    _ = Depends(api_key_validator)
):
    system_prompt = cfg.prompts[bill_type].system_prompt
    
    with NamedTemporaryFile(delete=False) as temp_file:
        shutil.copyfileobj(uploaded_file.file, temp_file)
        temp_file_path = temp_file.name  # Use this temporary file path
    
    response = bill_parser(
        api_key=cfg.openai.api_key,
        model=cfg.openai.vision_model,
        system_prompt=system_prompt,
        image_path=temp_file_path,  # Temporary file path used here
    )
    
    # Cleanup temporary file
    os.unlink(temp_file_path)
    
    return {"parsed_bill": response}


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)