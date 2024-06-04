import pydantic as pyd
import os

from web_renderer.logger import logger


@pyd.validate_arguments
async def save_file(
    output_path: str,
    filename: str,
    data: str,
    format_: str,
) -> str | None:
    if await validate_output_location(output_path):
        file_path = f"{output_path}{filename}.{format_}"
        with open(file_path, "w") as fin:
            fin.write(data)
        return file_path
    return None


@pyd.validate_arguments
async def validate_output_location(path: str) -> bool:
    """
    Use:
        Validates that a given location does exist, if not - creates it.

    Returns:
        Returns the location's path.
    """
    try:
        os.makedirs(path, exist_ok=True)
        os.system(f"chmod 777 {path}")
        return True
    except Exception as e:
        logger.error(e)
        return False
