# Discord Welcome Bot

## Overview

This is a Discord bot that automatically generates and sends custom welcome images when new members join a server. The bot creates personalized gradient background images featuring the new member's avatar and welcome message, then sends them to a configurable welcome channel.

## User Preferences

Preferred communication style: Simple, everyday language.
User language: Indonesian (Bahasa Indonesia)
Custom background image: https://postimg.cc/YG2wwxts (landscape/nature theme)
Welcome text language: Indonesian ("Selamat Datang!" instead of "Welcome!")
Custom welcome message format: "Selamat datang {user} di {server}. Jangan lupa mampir ke #rules dan #general. Selamat berdiskusi 🎉"
Channel references: <#1396367392644530209> dan <#1396367050787786873>

## System Architecture

The bot follows a modular architecture with clear separation of concerns:

- **Main Entry Point** (`main.py`): Handles Discord client initialization, event handling, and bot lifecycle
- **Configuration Management** (`bot/config.py`): JSON-based configuration storage for guild-specific settings
- **Command System** (`bot/commands.py`): Discord slash commands for bot configuration and management
- **Image Generation** (`bot/image_generator.py`): Asynchronous image processing for welcome graphics with custom backgrounds
- **Asset Generation** (`assets/background.py`): Procedural background image creation with gradient effects
- **Wiki System** (`bot/wiki.py`): Local wiki storage and management for server-specific information
- **Web Scraper** (`bot/wiki_scraper.py`): Lord of Mysteries Wiki scraper using trafilatura for content extraction

## Key Components

### Bot Core
- **Discord.py Framework**: Uses discord.py with command extensions for bot functionality
- **Event-Driven Architecture**: Responds to Discord events (member joins, bot ready)
- **Logging System**: Comprehensive logging with file and console output
- **Environment Configuration**: Uses dotenv for secure token management

### Image Processing Pipeline
- **PIL (Pillow)**: Core image manipulation library for creating welcome graphics
- **Async HTTP Client**: aiohttp for downloading member avatars
- **Gradient Generator**: Custom algorithm for creating Discord-themed gradient backgrounds
- **Temporary File Management**: Secure handling of generated images

### Configuration System
- **JSON Storage**: Simple file-based configuration for guild settings
- **Guild-Specific Settings**: Per-server welcome channel configuration
- **Auto-Save Mechanism**: Automatic persistence of configuration changes

## Data Flow

1. **Member Join Event**: Discord triggers `on_member_join` when someone joins a server
2. **Channel Lookup**: Bot checks if guild has configured welcome channel
3. **Avatar Download**: Asynchronously fetches member's Discord avatar
4. **Image Generation**: Creates gradient background and composites with avatar
5. **Message Delivery**: Sends generated image to configured welcome channel
6. **Cleanup**: Removes temporary image files after sending

## External Dependencies

### Core Libraries
- **discord.py**: Discord API wrapper and bot framework
- **Pillow (PIL)**: Image processing and manipulation
- **aiohttp**: Async HTTP client for avatar downloads
- **python-dotenv**: Environment variable management

### Discord API Integration
- **Bot Permissions**: Requires `send_messages`, `attach_files`, and `manage_guild` permissions
- **Intents**: Uses `message_content`, `members`, and `guilds` intents
- **Rate Limiting**: Handled automatically by discord.py

## Deployment Strategy

### Environment Setup
- **Token Security**: Discord bot token stored in `.env` file
- **File Permissions**: Bot needs write access for config.json and temporary files
- **Logging Output**: Dual logging to both file (`bot.log`) and console

### Configuration Requirements
- **Guild Setup**: Administrators use `!setwelcome` command to configure welcome channels
- **Permission Validation**: Bot checks channel permissions before setting welcome channel
- **Graceful Degradation**: Bot continues running even if image generation fails

### Scalability Considerations
- **Memory Management**: Temporary files are cleaned up after use
- **Async Operations**: Non-blocking image generation and HTTP requests
- **Error Handling**: Comprehensive exception handling with logging
- **Multi-Guild Support**: Independent configuration for multiple Discord servers

The architecture prioritizes reliability and ease of maintenance while providing a smooth user experience for Discord communities wanting automated welcome messages with custom imagery.