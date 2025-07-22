from PIL import Image, ImageDraw
import random

def create_gradient_background(width, height):
    """
    Create a gradient background image.
    
    Args:
        width (int): Image width
        height (int): Image height
        
    Returns:
        PIL.Image: Generated gradient background
    """
    # Create base image
    image = Image.new('RGBA', (width, height), (0, 0, 0, 255))
    draw = ImageDraw.Draw(image)
    
    # Define gradient colors (Discord-like colors)
    colors = [
        [(88, 101, 242), (88, 101, 242)],  # Discord Blurple
        [(114, 137, 218), (78, 93, 148)], # Discord Blue gradient
        [(153, 170, 181), (99, 102, 241)], # Gray to purple
        [(67, 56, 202), (139, 69, 19)],   # Purple to brown
        [(59, 130, 246), (147, 51, 234)], # Blue to purple
    ]
    
    # Select random gradient
    start_color, end_color = random.choice(colors)
    
    # Create vertical gradient
    for y in range(height):
        # Calculate interpolation factor
        factor = y / height
        
        # Interpolate between start and end colors
        r = int(start_color[0] * (1 - factor) + end_color[0] * factor)
        g = int(start_color[1] * (1 - factor) + end_color[1] * factor)
        b = int(start_color[2] * (1 - factor) + end_color[2] * factor)
        
        # Draw horizontal line
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))
    
    # Add subtle pattern overlay
    _add_pattern_overlay(image, draw, width, height)
    
    return image

def _add_pattern_overlay(image, draw, width, height):
    """Add a subtle pattern overlay to the background."""
    try:
        # Add some geometric patterns
        pattern_color = (255, 255, 255, 20)  # Very subtle white
        
        # Add diagonal lines pattern
        line_spacing = 50
        for i in range(0, width + height, line_spacing):
            # Diagonal lines from top-left to bottom-right
            start_x = max(0, i - height)
            start_y = max(0, height - i)
            end_x = min(width, i)
            end_y = min(height, height - (i - width))
            
            if start_x < width and start_y < height:
                draw.line([(start_x, start_y), (end_x, end_y)], fill=pattern_color, width=1)
        
        # Add some circles for decoration
        for i in range(5):
            x = random.randint(0, width)
            y = random.randint(0, height)
            radius = random.randint(20, 80)
            
            # Draw circle outline only
            draw.ellipse([x - radius, y - radius, x + radius, y + radius], 
                        outline=(255, 255, 255, 30), width=2)
        
        # Add corner highlights
        highlight_color = (255, 255, 255, 40)
        corner_size = 100
        
        # Top-left highlight
        for i in range(corner_size):
            alpha = int(40 * (1 - i / corner_size))
            color = (255, 255, 255, alpha)
            draw.line([(0, i), (corner_size - i, 0)], fill=color, width=2)
        
        # Bottom-right highlight
        for i in range(corner_size):
            alpha = int(40 * (1 - i / corner_size))
            color = (255, 255, 255, alpha)
            start_x = width - corner_size + i
            start_y = height - 1
            end_x = width - 1
            end_y = height - corner_size + i
            if start_x < width and end_y >= 0:
                draw.line([(start_x, start_y), (end_x, end_y)], fill=color, width=2)
                
    except Exception:
        # If pattern overlay fails, just continue with plain gradient
        pass

def create_discord_themed_background(width, height):
    """
    Create a Discord-themed background with the official branding colors.
    
    Args:
        width (int): Image width  
        height (int): Image height
        
    Returns:
        PIL.Image: Generated Discord-themed background
    """
    # Discord brand colors
    discord_blurple = (88, 101, 242)
    discord_dark = (35, 39, 42)
    discord_gray = (153, 170, 181)
    
    # Create base with dark background
    image = Image.new('RGBA', (width, height), discord_dark + (255,))
    draw = ImageDraw.Draw(image)
    
    # Create radial-like gradient effect
    center_x, center_y = width // 2, height // 2
    max_distance = ((width // 2) ** 2 + (height // 2) ** 2) ** 0.5
    
    for y in range(height):
        for x in range(0, width, 4):  # Sample every 4 pixels for performance
            # Calculate distance from center
            distance = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
            factor = min(distance / max_distance, 1.0)
            
            # Interpolate between blurple and dark
            r = int(discord_blurple[0] * (1 - factor) + discord_dark[0] * factor)
            g = int(discord_blurple[1] * (1 - factor) + discord_dark[1] * factor)
            b = int(discord_blurple[2] * (1 - factor) + discord_dark[2] * factor)
            
            # Draw vertical line (since we're sampling every 4 pixels)
            draw.rectangle([x, y, x + 3, y], fill=(r, g, b, 255))
    
    return image
