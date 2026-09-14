import os
import random
import textwrap
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

FONT_URL = "https://raw.githubusercontent.com/JulietaUla/Montserrat/master/fonts/ttf/Montserrat-Black.ttf"
LOCAL_FONT_PATH = "Montserrat-Black.ttf"

# Dynamic arrays to ensure 100% unique DALL-E images on every generation
CAR_COLORS = [
    "metallic candy apple red",
    "gloss obsidian black",
    "liquid reflex silver",
    "pearl white metallic",
    "midnight sapphire blue",
    "matte gunmetal gray",
    "emerald green metallic",
    "champagne gold metallic"
]

CAR_TYPES = [
    "luxury SUV",
    "executive sports sedan",
    "modern high-performance electric vehicle",
    "grand touring coupe",
    "premium crossover utility vehicle",
    "compact luxury sedan"
]

WORKSHOP_SETTINGS = [
    "inside a modern high-tech collision repair center with laser frame alignment racks",
    "inside a state-of-the-art downdraft heated paint spray booth with bright ambient LED lights",
    "in a spotless automotive body workshop next to computerized diagnostic calibration tools",
    "in an advanced certified collision repair bay with vehicle hydraulic lifts and pristine epoxy floor",
    "inside a professional auto paint curing and detailing station with mirror-like floor reflections"
]

CAMERA_ANGLES = [
    "captured from a cinematic 3/4 front angle view",
    "captured from a dramatic low-angle hero perspective",
    "captured from a sharp 3/4 rear quarter angle showcasing immaculate body panels",
    "captured from a sleek side profile with crisp studio automotive lighting",
    "captured from an eye-level three-quarter perspective highlighting high-gloss paint reflection"
]

# Client-approved local fallback templates
TEMPLATE_FILES = [
    "blog.post--2026.jpeg",
    "blog.post--variant1.jpeg",
    "blog.post--variant2.jpeg"
]


def ensure_font_exists():
    """
    Ensures Montserrat-Black bold font exists locally.
    """
    if os.path.exists(LOCAL_FONT_PATH):
        return LOCAL_FONT_PATH

    print(f"Downloading bold typography font ({LOCAL_FONT_PATH})...")
    try:
        response = requests.get(FONT_URL, timeout=10)
        if response.status_code == 200:
            with open(LOCAL_FONT_PATH, "wb") as f:
                f.write(response.content)
            print("Font downloaded successfully.")
            return LOCAL_FONT_PATH
    except Exception as e:
        print(f"Notice: Could not download font ({e}). Using system fallback.")

    return None


def get_font(size=36):
    """
    Loads ImageFont with system fallbacks.
    """
    font_file = ensure_font_exists()
    if font_file and os.path.exists(font_file):
        try:
            return ImageFont.truetype(font_file, size)
        except Exception:
            pass

    system_font_candidates = [
        "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "arial.ttf"
    ]
    for candidate in system_font_candidates:
        if os.path.exists(candidate):
            try:
                return ImageFont.truetype(candidate, size)
            except Exception:
                continue

    return ImageFont.load_default()


def generate_dalle_images(topic_title: str, count: int = 3) -> list:
    """
    Generates unique, high-resolution automotive images using OpenAI DALL-E 3.
    Uses randomized car colors, body styles, workshop settings, and camera angles.
    """
    generated_paths = []
    available_colors = random.sample(CAR_COLORS, min(count, len(CAR_COLORS)))
    available_types = random.sample(CAR_TYPES, min(count, len(CAR_TYPES)))
    available_settings = random.sample(WORKSHOP_SETTINGS, min(count, len(WORKSHOP_SETTINGS)))
    available_angles = random.sample(CAMERA_ANGLES, min(count, len(CAMERA_ANGLES)))

    print(f"\n[Image Engine] Generating {count} unique DALL-E images for '{topic_title}'...")

    for i in range(count):
        color = available_colors[i % len(available_colors)]
        car_type = available_types[i % len(available_types)]
        setting = available_settings[i % len(available_settings)]
        angle = available_angles[i % len(available_angles)]

        dalle_prompt = (
            f"A photorealistic, 8k ultra-detailed commercial photograph of a flawless {color} {car_type} "
            f"{setting}, {angle}. Professional automotive commercial lighting, clean workshop background, "
            f"sharp focus on bodywork and reflection. No text, no watermarks, no distorted logos."
        )

        try:
            response = client.images.generate(
                model="dall-e-3",
                prompt=dalle_prompt,
                size="1024x1024",
                quality="standard",
                n=1
            )
            image_url = response.data[0].url
            img_res = requests.get(image_url, timeout=30)
            
            if img_res.status_code == 200:
                img = Image.open(BytesIO(img_res.content)).convert("RGB")
                filename = f"generated_image_{i + 1}.jpg"
                img.save(filename, "JPEG", quality=95)
                generated_paths.append(filename)
                print(f" -> Generated unique DALL-E image: {filename} ({color} {car_type})")
            else:
                print(f"Notice: Failed to download DALL-E image {i+1}, using template fallback.")
        except Exception as e:
            print(f"Notice: DALL-E generation error ({e}). Falling back to template generation.")
            break

    return generated_paths


def create_branded_template_images(title: str, count: int = 3) -> list:
    """
    Generates branded topic images from local templates with Montserrat-Black bold overlay.
    Used as an immediate fallback or local generation option.
    """
    generated_paths = []
    text_to_draw = title.upper()

    for idx in range(1, count + 1):
        template_idx = (idx - 1) % len(TEMPLATE_FILES)
        template_name = TEMPLATE_FILES[template_idx]
        template_path = template_name

        if not os.path.exists(template_path):
            template_path = TEMPLATE_FILES[0]

        if not os.path.exists(template_path):
            img = Image.new("RGB", (1280, 1024), color=(25, 25, 25))
        else:
            img = Image.open(template_path).convert("RGB")

        width, height = img.size
        draw = ImageDraw.Draw(img)

        # Clear top banner area
        banner_height = 150
        draw.rectangle([0, 0, width, banner_height], fill=(15, 15, 15))

        # Neat word wrapping
        wrapped_lines = textwrap.wrap(text_to_draw, width=34)
        if len(wrapped_lines) > 3:
            font = get_font(30)
            wrapped_lines = textwrap.wrap(text_to_draw, width=42)
            line_spacing = 38
        else:
            font = get_font(36)
            line_spacing = 44

        total_text_height = len(wrapped_lines) * line_spacing
        start_y = max(15, (banner_height - total_text_height) // 2)

        for line in wrapped_lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            line_w = bbox[2] - bbox[0]
            x = (width - line_w) // 2

            # Drop shadow and white text
            draw.text((x + 2, start_y + 2), line, fill=(0, 0, 0), font=font)
            draw.text((x, start_y), line, fill=(255, 255, 255), font=font)
            start_y += line_spacing

        output_filename = f"generated_image_{idx}.jpg"
        img.save(output_filename, "JPEG", quality=95)
        generated_paths.append(output_filename)
        print(f" -> Generated template image: {output_filename}")

    return generated_paths


def create_unique_images(title: str, use_dalle: bool = True) -> list:
    """
    Main entry point for image generation.
    Tries DALL-E with dynamic randomized arrays; falls back to template if needed.
    Guarantees exactly 3 unique images are returned.
    """
    images = []
    if use_dalle:
        images = generate_dalle_images(title, count=3)

    if len(images) < 3:
        fallback_images = create_branded_template_images(title, count=3)
        images = fallback_images

    return images


def cleanup_local_images(image_paths: list) -> None:
    """
    Removes generated images locally after they have been uploaded to WordPress,
    preventing file buildup and image looping.
    """
    if not image_paths:
        return

    for path in image_paths:
        try:
            if path and os.path.exists(path):
                os.remove(path)
                print(f"🧹 Cleaned up local file: {path}")
        except Exception as e:
            print(f"Notice: Could not delete local file {path}: {e}")


# Backward compatibility aliases
generate_blog_images = create_unique_images
create_branded_images = create_branded_template_images