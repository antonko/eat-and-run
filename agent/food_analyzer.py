import base64
import logging

from langchain.schema import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

# Configure logging
logger = logging.getLogger(__name__)


# Определяем модели данных
class Macros(BaseModel):
    """Macros model."""

    protein_g: float = Field(description="Protein in grams")
    fat_g: float = Field(description="Fat in grams")
    carbs_g: float = Field(description="Carbs in grams")


class FoodAnalysis(BaseModel):
    """Food analysis model."""

    is_food: bool = Field(description="Whether the image contains food")
    is_real: bool = Field(description="Whether the food is real")
    name: str | None = Field(default=None, description="Name of the dish in Russian language")
    weight_g: int | None = Field(default=None, description="Approximate weight in grams")
    calories: int | None = Field(default=None, description="Calories")
    macros: Macros | None = Field(default=None, description="Macronutrients in grams")
    confidence: int | None = Field(
        default=None,
        description="Confidence level of the analysis (0-100%)",
    )


class FoodAnalyzer:
    """Food image analyzer using LangChain and OpenAI's vision capabilities."""

    def __init__(self, llm: ChatOpenAI) -> None:
        # Используем переданный прокси или значение из настроек
        self.llm = llm
        self.system_prompt = """
        Вы - эксперт по анализу изображений еды. Ваша задача - определить, что изображено на фотографии, и предоставить детальную информацию о блюде.

        При анализе изображения следуйте этим правилам:

        1. Определите, содержит ли изображение еду:
           - Если еды нет: установите is_food = false, is_real = false
           - Если еда есть: установите is_food = true

        2. Проверьте, является ли еда реальной:
           - Если это рисунок, иллюстрация, 3D-модель: установите is_real = false
           - Если это фотография реальной еды: установите is_real = true

        3. Для реальной еды оцените:
           - Название блюда (на русском языке)
           - Примерный вес в граммах
           - Калорийность
           - Содержание белков, жиров и углеводов
           - Уровень уверенности в анализе (0-100%)

        4. Если еда нереальная или её нет:
           - Укажите причину в поле message
           - Остальные поля оставьте пустыми

        Будьте точны и объективны в оценках. Если не уверены в каких-то параметрах, укажите это в поле confidence.
        """

    async def analyze_image(self, image_data: bytes) -> FoodAnalysis:
        """Analyze a food image and return nutritional information.

        Args:
            image_data: bytes of image

        Returns:
            Dict containing food analysis results

        """
        try:
            # Encode image as base64
            base64_image = base64.b64encode(image_data).decode("utf-8")

            # Create the message with the image
            human_message = HumanMessage(
                content=[
                    {
                        "type": "text",
                        "text": "Analyze this image and determine if it contains REAL food (not drawings or illustrations). Check if it's a realistic individual portion and safe for consumption. If it passes all checks, identify the dish and estimate nutritional information. Provide the dish name in Russian language.",
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            )

            # Get response from OpenAI
            messages = [SystemMessage(content=self.system_prompt), human_message]

            logger.info("Sending image to OpenAI for analysis...")
            return await self.llm.with_structured_output(FoodAnalysis).ainvoke(messages)
        except Exception:
            logger.exception("Error analyzing image")
            return {
                "is_food": False,
                "message": "Ошибка при анализе изображения",
            }
