import asyncio
import aiohttp
import io
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
import tempfile
import logging
from assets.background import create_gradient_background

logger = logging.getLogger(__name__)

class WelcomeImageGenerator:
    """Generates welcome images for new Discord members."""
    
    def __init__(self):
        self.width = 800
        self.height = 400
        self.avatar_size = 120
        self.custom_background_url = "https://i.postimg.cc/LXL4Lyw2/20250720-155752.jpg"
        
    async def create_welcome_image(self, member):
        """
        Create a welcome image for a Discord member.
        
        Args:
            member: Discord member object
            
        Returns:
            str: Path to the generated image file, or None if failed
        """
        try:
            # Download member's avatar
            avatar_image = await self._download_avatar(member)
            if not avatar_image:
                logger.error(f'Failed to download avatar for {member.name}')
                return None
            
            # Create the welcome image
            image = await self._generate_image(member, avatar_image)
            
            # Save to temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            image.save(temp_file.name, 'PNG')
            temp_file.close()
            
            return temp_file.name
            
        except Exception as e:
            logger.error(f'Error creating welcome image: {str(e)}')
            return None
    
    async def _download_avatar(self, member):
        """Download member's avatar image."""
        try:
            # Get avatar URL
            avatar_url = member.display_avatar.url
            
            # Download avatar
            async with aiohttp.ClientSession() as session:
                async with session.get(avatar_url) as response:
                    if response.status == 200:
                        avatar_data = await response.read()
                        return Image.open(io.BytesIO(avatar_data))
            
            return None
            
        except Exception as e:
            logger.error(f'Error downloading avatar: {str(e)}')
            return None
    
    async def _create_custom_background(self):
        """Download and prepare custom background image."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.custom_background_url) as response:
                    if response.status == 200:
                        background_data = await response.read()
                        background_image = Image.open(io.BytesIO(background_data))
                        
                        # Resize background to fit our dimensions while maintaining aspect ratio
                        background_image = background_image.convert('RGBA')
                        
                        # Calculate resize to cover the entire area
                        bg_width, bg_height = background_image.size
                        scale_w = self.width / bg_width
                        scale_h = self.height / bg_height
                        scale = max(scale_w, scale_h)  # Use max to cover entire area
                        
                        new_width = int(bg_width * scale)
                        new_height = int(bg_height * scale)
                        
                        # Resize the background
                        background_image = background_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                        
                        # Crop to exact dimensions from center
                        left = (new_width - self.width) // 2
                        top = (new_height - self.height) // 2
                        right = left + self.width
                        bottom = top + self.height
                        
                        background_image = background_image.crop((left, top, right, bottom))
                        
                        # Add semi-transparent overlay for better text visibility
                        overlay = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 100))
                        background_image = Image.alpha_composite(background_image, overlay)
                        
                        return background_image
            
            return None
            
        except Exception as e:
            logger.error(f'Error downloading custom background: {str(e)}')
            return None
    
    async def _generate_image(self, member, avatar_image):
        """Generate the welcome image with background and text."""
        # Create background using custom image
        image = await self._create_custom_background()
        if not image:
            # Fallback to gradient if custom image fails
            image = create_gradient_background(self.width, self.height)
        draw = ImageDraw.Draw(image)
        
        # Process avatar
        avatar = self._process_avatar(avatar_image)
        
        # Calculate positions
        avatar_x = (self.width - self.avatar_size) // 2
        avatar_y = 50
        
        # Paste avatar
        image.paste(avatar, (avatar_x, avatar_y), avatar)
        
        # Add text
        self._add_text(draw, member)
        
        # Add decorative elements
        self._add_decorations(draw)
        
        return image
    
    def _process_avatar(self, avatar_image):
        """Process avatar image to be circular with border."""
        # Resize avatar
        avatar = avatar_image.resize((self.avatar_size, self.avatar_size), Image.Resampling.LANCZOS)
        
        # Create circular mask
        mask = Image.new('L', (self.avatar_size, self.avatar_size), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse([0, 0, self.avatar_size, self.avatar_size], fill=255)
        
        # Apply mask to avatar
        avatar.putalpha(mask)
        
        # Create avatar with border
        border_size = 4
        bordered_size = self.avatar_size + border_size * 2
        bordered_avatar = Image.new('RGBA', (bordered_size, bordered_size), (0, 0, 0, 0))
        border_draw = ImageDraw.Draw(bordered_avatar)
        
        # Draw border
        border_draw.ellipse([0, 0, bordered_size, bordered_size], fill=(255, 255, 255, 255))
        
        # Paste avatar on border
        bordered_avatar.paste(avatar, (border_size, border_size), avatar)
        
        # Resize back to original size
        return bordered_avatar.resize((self.avatar_size, self.avatar_size), Image.Resampling.LANCZOS)
    
    def _add_text(self, draw, member):
        """Add welcome text to the image."""
        try:
            # Try to load a better font, fallback to default
            try:
                title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
                subtitle_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
                info_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
            except (OSError, IOError):
                title_font = ImageFont.load_default()
                subtitle_font = ImageFont.load_default()
                info_font = ImageFont.load_default()
            
            # Welcome text
            welcome_text = "Selamat Datang!"
            username_text = f"{member.display_name}"
            server_text = f"ke {member.guild.name}"
            
            # Calculate text positions
            title_bbox = draw.textbbox((0, 0), welcome_text, font=title_font)
            title_width = title_bbox[2] - title_bbox[0]
            title_x = (self.width - title_width) // 2
            title_y = 200
            
            username_bbox = draw.textbbox((0, 0), username_text, font=subtitle_font)
            username_width = username_bbox[2] - username_bbox[0]
            username_x = (self.width - username_width) // 2
            username_y = 250
            
            server_bbox = draw.textbbox((0, 0), server_text, font=info_font)
            server_width = server_bbox[2] - server_bbox[0]
            server_x = (self.width - server_width) // 2
            server_y = 290
            
            # Draw text with shadow effect
            shadow_offset = 2
            shadow_color = (0, 0, 0, 128)
            text_color = (255, 255, 255, 255)
            
            # Draw shadows
            draw.text((title_x + shadow_offset, title_y + shadow_offset), welcome_text, 
                     font=title_font, fill=shadow_color)
            draw.text((username_x + shadow_offset, username_y + shadow_offset), username_text, 
                     font=subtitle_font, fill=shadow_color)
            draw.text((server_x + shadow_offset, server_y + shadow_offset), server_text, 
                     font=info_font, fill=shadow_color)
            
            # Draw main text
            draw.text((title_x, title_y), welcome_text, font=title_font, fill=text_color)
            draw.text((username_x, username_y), username_text, font=subtitle_font, fill=text_color)
            draw.text((server_x, server_y), server_text, font=info_font, fill=text_color)
            
        except Exception as e:
            logger.error(f'Error adding text to image: {str(e)}')
    
    def _add_decorations(self, draw):
        """Add decorative elements to the image."""
        try:
            # Add some decorative lines
            line_color = (255, 255, 255, 100)
            
            # Top decorative line
            draw.rectangle([150, 180, 650, 182], fill=line_color)
            
            # Bottom decorative line
            draw.rectangle([150, 320, 650, 322], fill=line_color)
            
            # Corner decorations
            corner_size = 20
            corner_color = (255, 255, 255, 80)
            
            # Top-left corner
            draw.arc([20, 20, 20 + corner_size, 20 + corner_size], 180, 270, fill=corner_color, width=3)
            
            # Top-right corner
            draw.arc([self.width - 20 - corner_size, 20, self.width - 20, 20 + corner_size], 
                    270, 360, fill=corner_color, width=3)
            
            # Bottom-left corner
            draw.arc([20, self.height - 20 - corner_size, 20 + corner_size, self.height - 20], 
                    90, 180, fill=corner_color, width=3)
            
            # Bottom-right corner
            draw.arc([self.width - 20 - corner_size, self.height - 20 - corner_size, 
                     self.width - 20, self.height - 20], 0, 90, fill=corner_color, width=3)
            
        except Exception as e:
            logger.error(f'Error adding decorations: {str(e)}')
