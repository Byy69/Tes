import discord
from discord.ext import commands
import asyncio
import logging
import os
from dotenv import load_dotenv
from bot.image_generator import WelcomeImageGenerator
from bot.config import BotConfig
from bot.commands import setup_commands

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)
config = BotConfig()
image_generator = WelcomeImageGenerator()

@bot.event
async def on_ready():
    """Called when the bot is ready and connected to Discord."""
    logger.info(f'{bot.user} has connected to Discord!')
    logger.info(f'Bot is in {len(bot.guilds)} guilds')
    
    # Set bot activity
    activity = discord.Activity(type=discord.ActivityType.watching, name="for new members")
    await bot.change_presence(activity=activity)

@bot.event
async def on_member_join(member):
    """Called when a new member joins a guild."""
    try:
        logger.info(f'New member joined: {member.name} in guild {member.guild.name}')
        
        # Get welcome channel for this guild
        welcome_channel_id = config.get_welcome_channel(member.guild.id)
        if not welcome_channel_id:
            logger.warning(f'No welcome channel set for guild {member.guild.name}')
            return
        
        welcome_channel = bot.get_channel(welcome_channel_id)
        if not welcome_channel:
            logger.error(f'Welcome channel {welcome_channel_id} not found')
            return
        
        # Generate welcome image
        logger.info(f'Generating welcome image for {member.name}')
        image_path = await image_generator.create_welcome_image(member)
        
        if not image_path:
            logger.error(f'Failed to generate welcome image for {member.name}')
            # Send text-only welcome message as fallback
            embed = discord.Embed(
                title="Selamat Datang!",
                description=f"Selamat datang {member.mention} di {member.guild.name}. Jangan lupa mampir ke <#1396367392644530209> dan <#1396367050787786873>. Selamat berdiskusi 🎉",
                color=0x00ff00
            )
            await welcome_channel.send(embed=embed)
            return
        
        # Send welcome message with image
        with open(image_path, 'rb') as f:
            file = discord.File(f, filename='welcome.png')
            embed = discord.Embed(
                title="Selamat Datang!",
                description=f"Selamat datang {member.mention} di {member.guild.name}. Jangan lupa mampir ke <#1396367392644530209> dan <#1396367050787786873>. Selamat berdiskusi 🎉",
                color=0x00ff00
            )
            embed.set_image(url="attachment://welcome.png")
            embed.set_footer(text=f"Member #{member.guild.member_count}")
            
            await welcome_channel.send(embed=embed, file=file)
        
        # Clean up temporary image file
        try:
            os.remove(image_path)
        except OSError:
            pass
        
        logger.info(f'Welcome message sent for {member.name}')
        
    except Exception as e:
        logger.error(f'Error processing member join for {member.name}: {str(e)}')

@bot.event
async def on_command_error(ctx, error):
    """Global error handler for commands."""
    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Kamu tidak punya permission untuk menggunakan command ini.")
        logger.warning(f'Missing permissions error for user {ctx.author}: {str(error)}')
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Parameter yang diperlukan hilang: {error.param}")
        logger.warning(f'Missing argument error: {str(error)}')
    elif isinstance(error, discord.Forbidden):
        await ctx.send("❌ Bot tidak punya permission untuk melakukan ini. Cek role dan permission bot.")
        logger.error(f'Bot missing permissions: {str(error)}')
    else:
        await ctx.send("❌ Terjadi kesalahan saat memproses command.")
        logger.error(f'Command error: {str(error)}', exc_info=True)

async def main():
    """Main function to start the bot."""
    # Setup commands
    await setup_commands(bot, config)
    
    # Get bot token from environment
    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token:
        logger.error('DISCORD_BOT_TOKEN not found in environment variables')
        return
    
    # Start the bot
    try:
        await bot.start(token)
    except discord.LoginFailure:
        logger.error('Invalid bot token')
    except Exception as e:
        logger.error(f'Error starting bot: {str(e)}')

if __name__ == '__main__':
    asyncio.run(main())
