import json
import os
import logging
from datetime import datetime
import discord
from discord.ext import commands

logger = logging.getLogger(__name__)

class WikiSystem:
    """Manages wiki entries for the Discord bot."""
    
    def __init__(self, wiki_file='wiki.json'):
        self.wiki_file = wiki_file
        self.wiki_data = self._load_wiki()
    
    def _load_wiki(self):
        """Load wiki data from file."""
        try:
            if os.path.exists(self.wiki_file):
                with open(self.wiki_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {'entries': {}, 'aliases': {}}
        except Exception as e:
            logger.error(f'Error loading wiki: {str(e)}')
            return {'entries': {}, 'aliases': {}}
    
    def _save_wiki(self):
        """Save wiki data to file."""
        try:
            with open(self.wiki_file, 'w', encoding='utf-8') as f:
                json.dump(self.wiki_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f'Error saving wiki: {str(e)}')
    
    def add_entry(self, title, content, author_id, guild_id):
        """Add a new wiki entry."""
        title_lower = title.lower()
        guild_id_str = str(guild_id)
        
        if guild_id_str not in self.wiki_data['entries']:
            self.wiki_data['entries'][guild_id_str] = {}
        
        self.wiki_data['entries'][guild_id_str][title_lower] = {
            'title': title,
            'content': content,
            'author_id': author_id,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'edit_count': 0
        }
        
        self._save_wiki()
        logger.info(f'Wiki entry "{title}" added by user {author_id} in guild {guild_id}')
        return True
    
    def edit_entry(self, title, content, author_id, guild_id):
        """Edit an existing wiki entry."""
        title_lower = title.lower()
        guild_id_str = str(guild_id)
        
        if guild_id_str not in self.wiki_data['entries']:
            return False
        
        if title_lower not in self.wiki_data['entries'][guild_id_str]:
            return False
        
        entry = self.wiki_data['entries'][guild_id_str][title_lower]
        entry['content'] = content
        entry['updated_at'] = datetime.now().isoformat()
        entry['edit_count'] += 1
        
        self._save_wiki()
        logger.info(f'Wiki entry "{title}" edited by user {author_id} in guild {guild_id}')
        return True
    
    def get_entry(self, title, guild_id):
        """Get a wiki entry."""
        title_lower = title.lower()
        guild_id_str = str(guild_id)
        
        # Check aliases first
        if guild_id_str in self.wiki_data.get('aliases', {}):
            if title_lower in self.wiki_data['aliases'][guild_id_str]:
                title_lower = self.wiki_data['aliases'][guild_id_str][title_lower]
        
        if guild_id_str in self.wiki_data['entries']:
            return self.wiki_data['entries'][guild_id_str].get(title_lower)
        
        return None
    
    def delete_entry(self, title, guild_id):
        """Delete a wiki entry."""
        title_lower = title.lower()
        guild_id_str = str(guild_id)
        
        if guild_id_str not in self.wiki_data['entries']:
            return False
        
        if title_lower not in self.wiki_data['entries'][guild_id_str]:
            return False
        
        del self.wiki_data['entries'][guild_id_str][title_lower]
        
        # Remove aliases pointing to this entry
        if guild_id_str in self.wiki_data.get('aliases', {}):
            aliases_to_remove = []
            for alias, target in self.wiki_data['aliases'][guild_id_str].items():
                if target == title_lower:
                    aliases_to_remove.append(alias)
            
            for alias in aliases_to_remove:
                del self.wiki_data['aliases'][guild_id_str][alias]
        
        self._save_wiki()
        logger.info(f'Wiki entry "{title}" deleted from guild {guild_id}')
        return True
    
    def search_entries(self, query, guild_id, limit=10):
        """Search wiki entries by title or content."""
        query_lower = query.lower()
        guild_id_str = str(guild_id)
        results = []
        
        if guild_id_str not in self.wiki_data['entries']:
            return results
        
        for title_key, entry in self.wiki_data['entries'][guild_id_str].items():
            # Search in title
            if query_lower in entry['title'].lower():
                results.append({
                    'title': entry['title'],
                    'content': entry['content'][:100] + '...' if len(entry['content']) > 100 else entry['content'],
                    'match_type': 'title'
                })
            # Search in content
            elif query_lower in entry['content'].lower():
                results.append({
                    'title': entry['title'],
                    'content': entry['content'][:100] + '...' if len(entry['content']) > 100 else entry['content'],
                    'match_type': 'content'
                })
            
            if len(results) >= limit:
                break
        
        return results
    
    def list_entries(self, guild_id, limit=20):
        """List all wiki entries for a guild."""
        guild_id_str = str(guild_id)
        entries = []
        
        if guild_id_str not in self.wiki_data['entries']:
            return entries
        
        for entry in self.wiki_data['entries'][guild_id_str].values():
            entries.append({
                'title': entry['title'],
                'content': entry['content'][:50] + '...' if len(entry['content']) > 50 else entry['content'],
                'created_at': entry['created_at'],
                'edit_count': entry['edit_count']
            })
        
        # Sort by creation date (newest first)
        entries.sort(key=lambda x: x['created_at'], reverse=True)
        return entries[:limit]
    
    def add_alias(self, alias, target_title, guild_id):
        """Add an alias for a wiki entry."""
        alias_lower = alias.lower()
        target_lower = target_title.lower()
        guild_id_str = str(guild_id)
        
        # Check if target exists
        if guild_id_str not in self.wiki_data['entries']:
            return False
        
        if target_lower not in self.wiki_data['entries'][guild_id_str]:
            return False
        
        # Initialize aliases for guild if needed
        if 'aliases' not in self.wiki_data:
            self.wiki_data['aliases'] = {}
        
        if guild_id_str not in self.wiki_data['aliases']:
            self.wiki_data['aliases'][guild_id_str] = {}
        
        self.wiki_data['aliases'][guild_id_str][alias_lower] = target_lower
        self._save_wiki()
        
        logger.info(f'Wiki alias "{alias}" -> "{target_title}" added in guild {guild_id}')
        return True