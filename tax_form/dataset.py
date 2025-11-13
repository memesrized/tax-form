# TODO: move to a script
import base64
from dataclasses import dataclass
from typing import Literal
from PIL import Image
import json
from pathlib import Path


# just to make autocomplete happy
@dataclass
class Page:
    image: str | Image.Image
    text: str


@dataclass
class Sample:
    pages: list[Page]
    sample_name: str


class Dataset:
    def __init__(self, data_dir: str, img_mode: Literal["base64", "pil"] = "base64"):
        self.data_dir = data_dir
        self.img_mode = img_mode
        self.samples: list[Sample] = []

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx: int) -> Sample:
        return self.samples[idx]

    def _load_img(self, img_path: str) -> str | Image.Image:
        with open(img_path, "rb") as f:
            img_data = f.read()
        if self.img_mode == "base64":
            return base64.b64encode(img_data).decode("utf-8")
        elif self.img_mode == "pil":
            return Image.open(img_path)
        else:
            raise ValueError(f"Unsupported img_mode: {self.img_mode}")

    def _load_json(self, json_path: str):
        with open(json_path, "r") as f:
            return json.load(f)

    def _load_sample(self, sample_name: str) -> Sample:
        img_folder = Path(self.data_dir) / sample_name / "images"
        json_path = Path(self.data_dir) / sample_name / "text.json"

        # stupid, but to force the order
        num_of_images = len(list(img_folder.iterdir()))
        # ofc it needs to support multiple extensions but for demo purposes it's ok
        img_data = [
            self._load_img(img_folder / f"{i}.png") for i in range(num_of_images)
        ]

        json_data: list[str] = self._load_json(json_path)

        return Sample(
            pages=[
                Page(image=img, text=json_data[i]) for i, img in enumerate(img_data)
            ],
            sample_name=sample_name,
        )

    def load(self) -> "Dataset":
        # TODO: rework as for num_of_images for proper sorting
        # now sorted is enough since there are less than 10 samples
        for sample_dir in sorted(Path(self.data_dir).iterdir()):
            if sample_dir.is_dir():
                sample = self._load_sample(sample_dir.name)
                self.samples.append(sample)
        return self
