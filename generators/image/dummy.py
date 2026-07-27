from core.base import ImageGenerator

class DummyImageGenerator(ImageGenerator):
    def generate(self, prompt: str, **kwargs) -> str:
        return "https://via.placeholder.com/1024x1024?text=Dummy+Image"