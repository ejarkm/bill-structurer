import os
import shutil
from tempfile import NamedTemporaryFile

from fastapi.responses import JSONResponse
import hydra
import uvicorn
from fastapi import Depends, FastAPI, Header, HTTPException, UploadFile, File, Form, status
from omegaconf import DictConfig
from pydantic import BaseModel

from api.builders.openai_builder import bill_parser
from api.handlers.file_handler import concatenate_images_vertically, convert_pdf_to_images
from PIL import Image
import io


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
        temp_file_path = temp_file.name
    
    response = bill_parser(
        api_key=cfg.openai.api_key,
        model=cfg.openai.vision_model,
        system_prompt=system_prompt,
        image_path=temp_file_path,
    )
    
    # Cleanup temporary file
    os.unlink(temp_file_path)
    
    return {"parsed_bill": response}

@app.post("/upload-and-parse-bill")
def upload_and_parse_bill(
    bill_type: str = Form(...),
    uploaded_file: UploadFile = File(...),
    cfg: DictConfig = Depends(get_config),
    _ = Depends(api_key_validator)
):
    file_extension = uploaded_file.filename.split(".")[-1].lower()
    if file_extension not in ["pdf", "jpg", "png", "jpeg"]:
        return JSONResponse(
            content={"error": "Unsupported file type"},
            status_code=status.HTTP_400_BAD_REQUEST
        )

    # Maneja la conversión de PDF a imágenes y la concatenación si es necesario
    if file_extension == "pdf":
        # Convertir PDF a imágenes
        images = convert_pdf_to_images(uploaded_file.file)
        # Concatenar imágenes verticalmente si hay más de una página
        image = concatenate_images_vertically(images) if len(images) > 1 else images[0]
    else:
        # Para archivos de imagen, directamente crea un objeto Image
        image = Image.open(io.BytesIO(uploaded_file.file.read()))

    # Guarda la imagen en un archivo temporal
    with NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
        image.save(temp_file, format="JPEG")
        temp_file_path = temp_file.name

    # Usa la lógica para analizar la factura
    try:
        # Aquí debes llamar a la función que efectivamente parsea la factura.
        # Asegúrate de que esta función esté disponible y correctamente implementada.
        parsed_bill = bill_parser(
            image_path=temp_file_path,
            api_key=cfg.openai.api_key,
            model=cfg.openai.vision_model,
            system_prompt=cfg.prompts[bill_type].system_prompt,
        )
    finally:
        # Eliminar el archivo temporal
        os.unlink(temp_file_path)

    return {"parsed_bill": parsed_bill}


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    print("Starting server on port", port)
    print(os.getenv("INVOICE_API_KEY"))
    uvicorn.run(app, host="0.0.0.0", port=port)