import asyncio
import aiohttp
import logging
from typing import Optional, Dict, List
import re

try:
    from trafilatura import fetch_url, extract
    TRAFILATURA_AVAILABLE = True
except ImportError:
    TRAFILATURA_AVAILABLE = False

logger = logging.getLogger(__name__)

class LordOfMysteriesWikiScraper:
    """Scrapes Lord of Mysteries Wiki for information."""
    
    def __init__(self):
        self.base_url = "https://lordofthemysteries.fandom.com"
        self.wiki_url = f"{self.base_url}/wiki/"
        
    async def search_character(self, character_name: str) -> Optional[Dict]:
        """Search for a character on the wiki."""
        try:
            # Format character name for URL
            formatted_name = character_name.replace(" ", "_").title()
            url = f"{self.wiki_url}{formatted_name}"
            
            # Fetch the page
            downloaded = fetch_url(url)
            if not downloaded:
                return None
                
            # Extract content
            content = extract(downloaded)
            if not content:
                return None
            
            # Parse content for key information
            info = self._parse_character_info(content, character_name)
            info['source_url'] = url
            
            return info
            
        except Exception as e:
            logger.error(f'Error searching character {character_name}: {str(e)}')
            return None
    
    async def search_pathway(self, pathway_name: str) -> Optional[Dict]:
        """Search for a pathway on the wiki."""
        try:
            # Format pathway name for URL
            formatted_name = f"{pathway_name.replace(' ', '_')}_Pathway"
            url = f"{self.wiki_url}{formatted_name}"
            
            # Fetch the page
            downloaded = fetch_url(url)
            if not downloaded:
                return None
                
            # Extract content
            content = extract(downloaded)
            if not content:
                return None
            
            # Parse content for pathway information
            info = self._parse_pathway_info(content, pathway_name)
            info['source_url'] = url
            
            return info
            
        except Exception as e:
            logger.error(f'Error searching pathway {pathway_name}: {str(e)}')
            return None
    
    async def search_general(self, search_term: str) -> Optional[Dict]:
        """General search on the wiki."""
        try:
            # Format search term for URL
            formatted_term = search_term.replace(" ", "_").title()
            url = f"{self.wiki_url}{formatted_term}"
            
            # Fetch the page
            downloaded = fetch_url(url)
            if not downloaded:
                return None
                
            # Extract content
            content = extract(downloaded)
            if not content:
                return None
            
            # Parse general content
            info = self._parse_general_info(content, search_term)
            info['source_url'] = url
            
            return info
            
        except Exception as e:
            logger.error(f'Error searching {search_term}: {str(e)}')
            return None
    
    def _parse_character_info(self, content: str, character_name: str) -> Dict:
        """Parse character information from wiki content."""
        info = {
            'title': character_name,
            'type': 'Character',
            'description': '',
            'physical_description': '',
            'pathways_authorities': '',
            'key_info': []
        }
        
        lines = content.split('\n')
        current_section = ''
        
        # Track sections we're interested in
        collecting_physical = False
        collecting_pathways = False
        description_lines = []
        physical_lines = []
        pathway_lines = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Detect section headers
            line_lower = line.lower()
            
            # Physical Description section
            if any(keyword in line_lower for keyword in ['physical description', 'appearance', 'description']):
                collecting_physical = True
                collecting_pathways = False
                current_section = 'physical'
                continue
            
            # Pathways & Authorities section  
            elif any(keyword in line_lower for keyword in ['pathway', 'authorities', 'sequence', 'potion']):
                collecting_physical = False
                collecting_pathways = True
                current_section = 'pathways'
                continue
            
            # Stop collecting if we hit another major section
            elif any(keyword in line_lower for keyword in ['history', 'personality', 'abilities', 'trivia', 'references']):
                collecting_physical = False
                collecting_pathways = False
                current_section = ''
                continue
            
            # Collect content based on current section
            if collecting_physical and len(line) > 20:
                physical_lines.append(line)
            elif collecting_pathways and len(line) > 20:
                pathway_lines.append(line)
            elif current_section == '' and len(line) > 30 and len(description_lines) < 3:
                # General description when not in specific section
                description_lines.append(line)
        
        # Build the info
        info['description'] = '\n\n'.join(description_lines)
        info['physical_description'] = '\n'.join(physical_lines[:4])  # Limit to avoid too long
        info['pathways_authorities'] = '\n'.join(pathway_lines[:5])
        
        return info
    
    def _parse_pathway_info(self, content: str, pathway_name: str) -> Dict:
        """Parse pathway information from wiki content."""
        info = {
            'title': f"{pathway_name} Pathway",
            'type': 'Pathway',
            'general_information': '',
            'sequence_levels': '',
            'key_info': []
        }
        
        lines = content.split('\n')
        
        # Track sections
        collecting_general = False
        collecting_sequences = False
        general_lines = []
        sequence_lines = []
        current_section = ''
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            line_lower = line.lower()
            
            # Detect General Information section
            if any(keyword in line_lower for keyword in ['general information', 'overview', 'description']):
                collecting_general = True
                collecting_sequences = False
                current_section = 'general'
                continue
            
            # Detect Sequence section
            elif any(keyword in line_lower for keyword in ['sequence', 'levels', 'potion']):
                collecting_general = False
                collecting_sequences = True
                current_section = 'sequences'
                continue
            
            # Stop collecting if we hit other sections
            elif any(keyword in line_lower for keyword in ['history', 'notable', 'references', 'trivia']):
                collecting_general = False
                collecting_sequences = False
                current_section = ''
                continue
            
            # Collect content
            if collecting_general and len(line) > 20:
                general_lines.append(line)
            elif collecting_sequences and len(line) > 15:
                sequence_lines.append(line)
            elif current_section == '' and len(line) > 30 and len(general_lines) == 0:
                # Fallback to early content as general info
                general_lines.append(line)
        
        info['general_information'] = '\n'.join(general_lines[:4])
        info['sequence_levels'] = '\n'.join(sequence_lines[:8])
        
        return info
    
    def _parse_general_info(self, content: str, search_term: str) -> Dict:
        """Parse general information from wiki content."""
        info = {
            'title': search_term,
            'type': 'General',
            'description': '',
            'key_info': []
        }
        
        lines = content.split('\n')
        description_lines = []
        
        # Extract first few meaningful lines
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if len(line) > 30 and len(description_lines) < 4:
                description_lines.append(line)
        
        info['description'] = '\n\n'.join(description_lines)
        return info
    
    async def get_random_fact(self) -> Optional[str]:
        """Get a random fact from different wiki pages."""
        try:
            import random
            
            # List of different pages to get varied facts from
            fact_pages = [
                'Lord_of_Mysteries_Wiki',
                'Klein_Moretti',
                'Pathways',
                'Sealed_Artifacts',
                'Gods',
                'Angels',
                'Beyonder',
                'History_of_the_World'
            ]
            
            # Randomly select a page
            selected_page = random.choice(fact_pages)
            url = f"{self.wiki_url}{selected_page}"
            
            # Fetch the page
            if TRAFILATURA_AVAILABLE:
                downloaded = fetch_url(url)
                if not downloaded:
                    return None
                content = extract(downloaded)
            else:
                # Fallback method using aiohttp
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        if response.status != 200:
                            return None
                        html = await response.text()
                        # Simple text extraction (basic fallback)
                        import re
                        content = re.sub(r'<[^>]+>', '', html)
            
            if not content:
                return None
            
            # Extract interesting facts with more variety
            lines = content.split('\n')
            facts = []
            
            for line in lines:
                line = line.strip()
                # Look for varied content patterns
                if (len(line) > 40 and len(line) < 300 and 
                    any(keyword in line.lower() for keyword in [
                        'sequence', 'beyonder', 'pathway', 'sealed artifact', 'mystical', 
                        'potion', 'ritual', 'anchor', 'divinity', 'authority', 'domain',
                        'characteristic', 'formula', 'blasphemy', 'tarot', 'fool'
                    ])):
                    # Avoid repetitive or low-quality content
                    if not any(avoid in line.lower() for avoid in [
                        'edit', 'source', 'category', 'file:', 'image:', 'references'
                    ]):
                        facts.append(line)
            
            if facts:
                selected_fact = random.choice(facts)
                return f"📚 {selected_fact}"
            
            return "🌟 Lord of Mysteries adalah novel web serial yang ditulis oleh Cuttlefish That Loves Diving, mengisahkan petualangan Klein Moretti di dunia supernatural dengan sistem pathway dan sequences yang kompleks."
            
        except Exception as e:
            logger.error(f'Error getting random fact: {str(e)}')
            return "🌟 Lord of Mysteries adalah novel web serial yang ditulis oleh Cuttlefish That Loves Diving, mengisahkan petualangan Klein Moretti di dunia supernatural dengan sistem pathway dan sequences yang kompleks."