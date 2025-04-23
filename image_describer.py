import base64
import json
import re
import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
import cv2

class ProductImageDescriber:
    def __init__(self, image_bytes: bytes, openai_api_key: str, model_name: str = "gpt-4o", temperature: float = 0.3):
        os.environ["OPENAI_API_KEY"] = openai_api_key
        self.image_bytes = image_bytes
        self.llm = ChatOpenAI(model=model_name, temperature=temperature)

    def extract_key_frames(self, video_path, interval_seconds=3):
        cap = cv2.VideoCapture(video_path)
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        frame_count = 0
        images = []

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            if frame_count % (fps * interval_seconds) == 0:
                _, buffer = cv2.imencode('.jpg', frame)
                image_base64 = base64.b64encode(buffer).decode('utf-8')
                images.append(image_base64)
            frame_count += 1

        cap.release()
        return images

    def _encode_image_to_base64(self) -> str:
        return base64.b64encode(self.image_bytes).decode("utf-8")

    def generate_product_description(self) -> dict:
        image_base64 = self._encode_image_to_base64()
        prompt = (
            "You are an AI product description generator. Given the image, generate a response in JSON with three fields:\n"
            "1. 'title': A one-line catchy product title\n"
            "2. 'description': A 2–3 line short product description\n"
            "3. 'features': A list of 3–5 bullet point features\n\n"
            "Return response only as a JSON object."
        )

        message = HumanMessage(content=[
            {"type": "text", "text": prompt},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image_base64}"
                }
            }
        ])

        response = self.llm.invoke([message])
        return self.extract_useful_json(response.content)

    def extract_useful_json(self, text: str) -> dict:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r"\{.*?\}", text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            raise ValueError("No valid JSON found in the model response.")
