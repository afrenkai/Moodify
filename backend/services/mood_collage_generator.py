import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import io
import base64
from typing import List, Dict, Any, Tuple
import logging
import colorsys

#TODO: this sucks, improve it later
logger = logging.getLogger(__name__)


class MoodCollageGenerator:    
    def __init__(self, width: int = 800, height: int = 600):
        self.width = width
        self.height = height
        logger.info(f"Mood collage generator initialized ({width}x{height})")
    
    def generate_collage(
        self,
        embedding: np.ndarray,
        emotion: str = None
    ) -> Tuple[str, List[str], Dict[str, Any]]:
        visual_params = self._embedding_to_visual_params(embedding, emotion)

        image = self._create_collage_image(visual_params)

        dominant_colors = self._extract_dominant_colors(image)

        image_base64 = self._image_to_base64(image)
        
        logger.info(f"Generated mood collage with {len(dominant_colors)} dominant colors")
        
        return image_base64, dominant_colors, visual_params
    
    def _embedding_to_visual_params(
        self,
        embedding: np.ndarray,
        emotion: str = None
    ) -> Dict[str, Any]:
       
        emb_normalized = (embedding - embedding.min()) / (embedding.max() - embedding.min() + 1e-8)
        
        dim = len(emb_normalized)
        
        hue = float(np.mean(emb_normalized[:min(dim, 10)])) * 360  # 0-360
        saturation = float(np.mean(emb_normalized[min(dim, 10):min(dim, 20)])) * 0.7 + 0.3  # 0.3-1.0
        value = float(np.mean(emb_normalized[min(dim, 20):min(dim, 30)])) * 0.5 + 0.5  # 0.5-1.0
        
        complexity = float(np.std(emb_normalized))  # 0-1
        symmetry = float(1 - np.mean(np.abs(emb_normalized - 0.5)))  # 0-1
        
        blur_amount = float(np.mean(emb_normalized[min(dim, 30):min(dim, 40)])) * 5  # 0-5
        num_shapes = int(10 + complexity * 40)
        
        visual_params = {
            "primary_hue": hue,
            "saturation": saturation,
            "value": value,
            "complexity": complexity,
            "symmetry": symmetry,
            "blur_amount": blur_amount,
            "num_shapes": num_shapes,
            "emotion": emotion
        }
        
        if emotion:
            visual_params = self._adjust_for_emotion(visual_params, emotion)
        
        return visual_params
    
    def _adjust_for_emotion(
        self,
        visual_params: Dict[str, Any],
        emotion: str
    ) -> Dict[str, Any]:
        
        emotion_lower = emotion.lower()
        
        if "happy" in emotion_lower or "joy" in emotion_lower:
            visual_params["saturation"] = max(visual_params["saturation"], 0.7)
            visual_params["value"] = max(visual_params["value"], 0.8)
            visual_params["primary_hue"] = (visual_params["primary_hue"] + 45) % 360  # Shift to warmer
        
        elif "sad" in emotion_lower or "melanchol" in emotion_lower:
            visual_params["saturation"] = min(visual_params["saturation"], 0.5)
            visual_params["value"] = min(visual_params["value"], 0.6)
            visual_params["primary_hue"] = 210 
        elif "energetic" in emotion_lower or "hyper" in emotion_lower:
            visual_params["complexity"] = max(visual_params["complexity"], 0.7)
            visual_params["num_shapes"] = max(visual_params["num_shapes"], 40)
            visual_params["saturation"] = max(visual_params["saturation"], 0.8)
        
        elif "calm" in emotion_lower or "peaceful" in emotion_lower:
            visual_params["complexity"] = min(visual_params["complexity"], 0.4)
            visual_params["saturation"] = min(visual_params["saturation"], 0.6)
            visual_params["blur_amount"] = max(visual_params["blur_amount"], 3)
        
        elif "angry" in emotion_lower or "rage" in emotion_lower:
            visual_params["primary_hue"] = 0  
            visual_params["saturation"] = max(visual_params["saturation"], 0.8)
            visual_params["complexity"] = max(visual_params["complexity"], 0.6)
        
        return visual_params
    
    def _create_collage_image(self, visual_params: Dict[str, Any]) -> Image.Image:
        image = Image.new('RGB', (self.width, self.height), color='white')
        draw = ImageDraw.Draw(image, 'RGBA')
        
        colors = self._generate_color_palette(
            visual_params["primary_hue"],
            visual_params["saturation"],
            visual_params["value"]
        )
        
        self._draw_gradient(image, colors[0], colors[1])
        draw = ImageDraw.Draw(image, 'RGBA')
        
        num_shapes = visual_params["num_shapes"]
        complexity = visual_params["complexity"]
        symmetry = visual_params["symmetry"]
        
        for i in range(num_shapes):
            x = np.random.randint(0, self.width)
            y = np.random.randint(0, self.height)
            
            size = int(20 + complexity * 100)
            
            color = colors[i % len(colors)]
            
            opacity = int(50 + complexity * 150)
            color_with_alpha = (*color, opacity)
            
            shape_type = i % 4
            if shape_type == 0:  
                draw.ellipse([x, y, x + size, y + size], fill=color_with_alpha)
            elif shape_type == 1:  
                draw.rectangle([x, y, x + size, y + size], fill=color_with_alpha)
            elif shape_type == 2: 
                points = [(x, y + size), (x + size, y + size), (x + size // 2, y)]
                draw.polygon(points, fill=color_with_alpha)
            else:  
                draw.line([x, y, x + size, y + size], fill=color_with_alpha, width=3)
            
            if symmetry > 0.6:
                mirror_x = self.width - x - size
                if shape_type == 0:
                    draw.ellipse([mirror_x, y, mirror_x + size, y + size], fill=color_with_alpha)
                elif shape_type == 1:
                    draw.rectangle([mirror_x, y, mirror_x + size, y + size], fill=color_with_alpha)
        

        if visual_params["blur_amount"] > 0:
            image = image.filter(ImageFilter.GaussianBlur(visual_params["blur_amount"]))
        
        return image
    
    def _generate_color_palette(
        self,
        base_hue: float,
        saturation: float,
        value: float,
        num_colors: int = 5
    ) -> List[Tuple[int, int, int]]:
        
        colors = []
        
        for i in range(num_colors):
            hue = (base_hue + (i * 60)) % 360 / 360.0
            sat = max(0.0, min(1.0, saturation + (i - num_colors // 2) * 0.1))
            val = max(0.0, min(1.0, value + (i - num_colors // 2) * 0.05))
            
            rgb = colorsys.hsv_to_rgb(hue, sat, val)
            rgb_int = tuple(int(c * 255) for c in rgb)
            colors.append(rgb_int)
        
        return colors
    
    def _draw_gradient(
        self,
        image: Image.Image,
        color1: Tuple[int, int, int],
        color2: Tuple[int, int, int]
    ):
        
        draw = ImageDraw.Draw(image)
        for y in range(self.height):
            ratio = y / self.height
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            
            draw.line([(0, y), (self.width, y)], fill=(r, g, b))
    
    def _extract_dominant_colors(
        self,
        image: Image.Image,
        num_colors: int = 5
    ) -> List[str]:
        small_image = image.resize((100, 100))
        img_array = np.array(small_image)
        pixels = img_array.reshape(-1, 3)        
        unique_colors = []
        for i in range(num_colors):
            idx = np.random.randint(0, len(pixels), min(1000, len(pixels)))
            sample = pixels[idx]
            mean_color = np.mean(sample, axis=0).astype(int)
            hex_color = '#{:02x}{:02x}{:02x}'.format(*mean_color)
            unique_colors.append(hex_color)
        
        return unique_colors
    
    def _image_to_base64(self, image: Image.Image) -> str:
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        buffer.seek(0)
        
        img_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        return img_base64
