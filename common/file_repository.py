import uuid

import aiofiles

file_path = "images"


async def save_image(image_data: bytes) -> str:
    """Сохраняет изображение в файл и возвращает его guid.

    Args:
        image_data: image data

    Returns:
        str: guid of saved image

    """
    # Сохраняем изображение в файл
    image_guid = str(uuid.uuid4())
    async with aiofiles.open(f"{file_path}/{image_guid}", "wb") as f:
        await f.write(image_data)

    return image_guid


async def get_image(image_guid: str) -> bytes:
    """Получает изображение.

    Args:
        image_guid: guid of saved image

    Returns:
        bytes: image data

    """
    async with aiofiles.open(f"{file_path}/{image_guid}", "rb") as image_file:
        return await image_file.read()
