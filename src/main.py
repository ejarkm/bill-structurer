import hydra
from omegaconf import DictConfig
from api.builders.openai_builder import bill_parser


@hydra.main(config_path="conf", config_name="config", version_base="1.3")
def my_app(cfg: DictConfig) -> None:
    system_prompt = cfg.prompts[cfg.bill_type].system_prompt

    image_path = "/workspaces/bill-structurer/data/output.jpg"

    response = bill_parser(
        api_key=cfg.openai.api_key,
        model=cfg.openai.vision_model,
        system_prompt=system_prompt,
        image_path=image_path,
    )

    print(response)


if __name__ == "__main__":
    my_app()
