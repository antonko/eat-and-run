import base64
import json
import logging
from typing import Any, Dict

from langchain.schema import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.config import settings

# Configure logging
logger = logging.getLogger(__name__)


class FoodAnalyzer:
    """Food image analyzer using LangChain and OpenAI's vision capabilities."""

    def __init__(self, proxy=None):
        # Используем переданный прокси или значение из настроек
        proxy_url = proxy or settings.PROXY_URL

        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            api_key=settings.OPENAI_API_KEY,
            max_tokens=1000,
            temperature=0,
            openai_proxy=proxy_url if proxy_url else None,
        )
        self.system_prompt = """
        You are a nutrition expert who can analyze food images. When presented with an image, you should:
        1. First determine if the image contains REAL food (not drawings, paintings, illustrations, cartoons, or computer-generated images).
           - If the image contains non-real food (drawings, illustrations, 3D renders, cartoons), respond with: {"is_food": false, "message": "Обнаружено нереалистичное изображение еды (рисунок, иллюстрация или графика). Пожалуйста, загрузите реальную фотографию блюда."}
           - If the image does not contain food at all, respond with: {"is_food": false, "message": "Еда на изображении не обнаружена."}
        
        2. Next check if the food portion is realistic for individual consumption:
           - If the image shows unrealistically large quantities (e.g., industrial quantities, a wagon of pasta, etc.), respond with: {"is_food": false, "message": "Обнаружено нереалистично большое количество еды. Пожалуйста, загрузите фото отдельной порции."}
        
        3. Check if the food is safe and generally accepted for human consumption:
           - If the image shows potentially dangerous, spoiled, or culturally inappropriate food (e.g., raw chicken, inedible objects, questionable meats like rats, insects not commonly eaten in mainstream cuisine), respond with: {"is_food": false, "message": "Обнаружена потенциально опасная или несъедобная пища. Пожалуйста, загрузите фото обычного блюда."}
        
        4. If and ONLY if real, safe, individual portion food is present in a photograph, identify the dish and estimate:
           - Name of the dish (in Russian language)
           - Approximate weight in grams
           - Calories
           - Macronutrients (protein, fat, carbs) in grams
        
        Respond with structured JSON in this format:
        {
            "is_food": true,
            "name": "Название блюда на русском языке",
            "weight_g": 250,
            "calories": 350,
            "macros": {
                "protein_g": 20,
                "fat_g": 12,
                "carbs_g": 35
            }
        }
        
        Always provide dish names in Russian language regardless of the origin of the dish.
        Provide your best estimate based on visual analysis. Be precise and detailed in your analysis.
        Your response MUST be valid JSON. Do not include any explanation or text outside the JSON.
        """

    async def analyze_image(self, image_data: bytes) -> Dict[str, Any]:
        """
        Analyze a food image and return nutritional information.

        Args:
            image_data: Raw image bytes

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
                ]
            )

            # Get response from OpenAI
            messages = [SystemMessage(content=self.system_prompt), human_message]

            logger.info("Sending image to OpenAI for analysis...")
            response = await self.llm.ainvoke(messages)

            if hasattr(response, "content"):
                response_text = response.content
            else:
                # Для совместимости с разными версиями LangChain
                response_text = str(response)

            logger.info(f"Received response from OpenAI: {response_text[:100]}...")

            # Удаляем маркеры Markdown, если они присутствуют
            cleaned_text = response_text.strip()
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text.replace("```json", "", 1)
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3]
            cleaned_text = cleaned_text.strip()

            # Parse the response content as JSON
            try:
                result = json.loads(cleaned_text)
                return result
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing error: {e}")
                logger.error(f"Raw response: {response_text}")

                # Пробуем извлечь JSON из текста, если он окружен другим текстом
                import re

                json_match = re.search(r"({.*})", response_text, re.DOTALL)
                if json_match:
                    try:
                        result = json.loads(json_match.group(1))
                        return result
                    except:  # noqa: E722
                        logger.error(f"Failed to parse JSON: {response_text}")

                return {
                    "is_food": False,
                    "message": "Не удалось разобрать ответ API. Пожалуйста, попробуйте еще раз.",
                }
        except Exception as e:
            logger.error(f"Error analyzing image: {e}")
            return {
                "is_food": False,
                "message": f"Ошибка при анализе изображения: {str(e)}",
            }
