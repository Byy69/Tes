import json
import os
import logging

logger = logging.getLogger(__name__)

class BotConfig:
    """Manages bot configuration including welcome channels for each guild."""
    
    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.config = self._load_config()
    
    def _load_config(self):
        """Load configuration from file."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            else:
                return {'guilds': {}}
        except Exception as e:
            logger.error(f'Error loading config: {str(e)}')
            return {'guilds': {}}
    
    def _save_config(self):
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logger.error(f'Error saving config: {str(e)}')
    
    def get_welcome_channel(self, guild_id):
        """Get welcome channel ID for a guild."""
        guild_id_str = str(guild_id)
        return self.config.get('guilds', {}).get(guild_id_str, {}).get('welcome_channel')
    
    def set_welcome_channel(self, guild_id, channel_id):
        """Set welcome channel ID for a guild."""
        guild_id_str = str(guild_id)
        
        if 'guilds' not in self.config:
            self.config['guilds'] = {}
        
        if guild_id_str not in self.config['guilds']:
            self.config['guilds'][guild_id_str] = {}
        
        self.config['guilds'][guild_id_str]['welcome_channel'] = channel_id
        self._save_config()
        
        logger.info(f'Set welcome channel {channel_id} for guild {guild_id}')
    
    def remove_welcome_channel(self, guild_id):
        """Remove welcome channel setting for a guild."""
        guild_id_str = str(guild_id)
        
        if guild_id_str in self.config.get('guilds', {}):
            if 'welcome_channel' in self.config['guilds'][guild_id_str]:
                del self.config['guilds'][guild_id_str]['welcome_channel']
                self._save_config()
                logger.info(f'Removed welcome channel for guild {guild_id}')
                return True
        
        return False
    
    def get_guild_config(self, guild_id):
        """Get all configuration for a guild."""
        guild_id_str = str(guild_id)
        return self.config.get('guilds', {}).get(guild_id_str, {})
    
    def get_all_guilds(self):
        """Get all configured guilds."""
        return self.config.get('guilds', {})
