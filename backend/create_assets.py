from PIL import Image, ImageDraw, ImageFont
import os

def create_placeholder_image(name, color, filename):
    img = Image.new('RGB', (800, 600), color=color)
    d = ImageDraw.Draw(img)
    # Load a default font
    # Since we don't know the system fonts, we'll try to use a basic one or default
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 100)
    except IOError:
        font = ImageFont.load_default()
        
    # Calculate text position (centered - roughly, load_default doesn't support getsize well)
    # Using a simple approximation for default font or better positioning if TTF works
    d.text((400, 300), name, fill=(255, 255, 255), anchor="mm", font=font)
    
    img.save(filename)
    print(f"Created {filename}")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(base_dir, "assets")
    os.makedirs(assets_dir, exist_ok=True)
    
    create_placeholder_image("HULK", "green", os.path.join(assets_dir, "hulk.png"))
    create_placeholder_image("SPIDERMAN", "red", os.path.join(assets_dir, "spiderman.png"))
