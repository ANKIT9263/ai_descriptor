import base64
import json
import re
import os
import cv2
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

class ProductVideoDescriber:
    def __init__(self, video_path: str, openai_api_key: str, model_name: str = "gpt-4o", temperature: float = 0.3):
        os.environ["OPENAI_API_KEY"] = openai_api_key
        self.video_path = video_path
        self.llm = ChatOpenAI(model=model_name, temperature=temperature)

    def extract_key_frames(self, interval_seconds=3):
        cap = cv2.VideoCapture(self.video_path)
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

    def generate_product_description(self) -> dict:
        frames = self.extract_key_frames(interval_seconds=3)
        if not frames:
            raise ValueError("No frames extracted from video.")

        prompt = (
            "You are an AI product description generator. Given the image frames from a product video, "
            "generate a response in JSON with three fields:\n"
            "1. 'title': A one-line catchy product title\n"
            "2. 'description': A 2–3 line short product description\n"
            "3. 'features': A list of 3–5 bullet point features\n\n"
            "Return the response only as a JSON object."
        )

        content = [{"type": "text", "text": prompt}]
        for frame_b64 in frames[:3]:  # Limit to 3 frames to keep token usage reasonable
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{frame_b64}"}
            })

        message = HumanMessage(content=content)
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
