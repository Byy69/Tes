import discord
from discord.ext import commands
import logging
from bot.wiki import WikiSystem
from bot.wiki_scraper import LordOfMysteriesWikiScraper

logger = logging.getLogger(__name__)

async def setup_commands(bot, config):
    """Setup bot commands."""
    
    # Initialize wiki system and scraper
    wiki = WikiSystem()
    lom_scraper = LordOfMysteriesWikiScraper()
    
    @bot.command(name='setwelcome')
    @commands.has_permissions(manage_guild=True)
    async def set_welcome_channel(ctx, channel: discord.TextChannel = None):
        """Set the welcome channel for this server."""
        try:
            if not channel:
                channel = ctx.channel
            
            # Check if bot has permissions to send messages in the channel
            permissions = channel.permissions_for(ctx.guild.me)
            if not permissions.send_messages or not permissions.attach_files:
                await ctx.send("❌ I don't have permission to send messages or attach files in that channel.")
                return
            
            # Set welcome channel
            config.set_welcome_channel(ctx.guild.id, channel.id)
            
            embed = discord.Embed(
                title="✅ Welcome Channel Set",
                description=f"Welcome messages will now be sent to {channel.mention}",
                color=0x00ff00
            )
            await ctx.send(embed=embed)
            
            logger.info(f'Welcome channel set to {channel.name} in guild {ctx.guild.name}')
            
        except Exception as e:
            logger.error(f'Error setting welcome channel: {str(e)}')
            await ctx.send("❌ An error occurred while setting the welcome channel.")
    
    @bot.command(name='welcomeinfo')
    async def welcome_info(ctx):
        """Show current welcome channel configuration."""
        try:
            welcome_channel_id = config.get_welcome_channel(ctx.guild.id)
            
            if not welcome_channel_id:
                embed = discord.Embed(
                    title="Welcome Channel Info",
                    description="No welcome channel is currently set for this server.\nUse `!setwelcome #channel` to set one.",
                    color=0xffaa00
                )
            else:
                welcome_channel = bot.get_channel(welcome_channel_id)
                if welcome_channel:
                    embed = discord.Embed(
                        title="Welcome Channel Info",
                        description=f"Welcome messages are sent to {welcome_channel.mention}",
                        color=0x00ff00
                    )
                else:
                    embed = discord.Embed(
                        title="Welcome Channel Info",
                        description="Welcome channel is set but the channel no longer exists.\nPlease set a new welcome channel.",
                        color=0xff0000
                    )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f'Error getting welcome info: {str(e)}')
            await ctx.send("❌ An error occurred while getting welcome information.")
    
    @bot.command(name='removewelcome')
    @commands.has_permissions(manage_guild=True)
    async def remove_welcome_channel(ctx):
        """Remove the welcome channel setting for this server."""
        try:
            success = config.remove_welcome_channel(ctx.guild.id)
            
            if success:
                embed = discord.Embed(
                    title="✅ Welcome Channel Removed",
                    description="Welcome messages are now disabled for this server.",
                    color=0x00ff00
                )
            else:
                embed = discord.Embed(
                    title="ℹ️ No Welcome Channel Set",
                    description="There was no welcome channel set for this server.",
                    color=0xffaa00
                )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f'Error removing welcome channel: {str(e)}')
            await ctx.send("❌ An error occurred while removing the welcome channel.")
    
    @bot.command(name='testwelcome')
    @commands.has_permissions(manage_guild=True)
    async def test_welcome(ctx, member: discord.Member = None):
        """Test the welcome message with a specific member (or yourself)."""
        try:
            if not member:
                member = ctx.author
            
            welcome_channel_id = config.get_welcome_channel(ctx.guild.id)
            if not welcome_channel_id:
                await ctx.send("❌ No welcome channel is set. Use `!setwelcome` first.")
                return
            
            welcome_channel = bot.get_channel(welcome_channel_id)
            if not welcome_channel:
                await ctx.send("❌ Welcome channel no longer exists. Please set a new one.")
                return
            
            # Simulate member join event
            await ctx.send(f"🧪 Testing welcome message for {member.mention}...")
            
            # Trigger the welcome logic (we'll import the image generator here)
            from bot.image_generator import WelcomeImageGenerator
            import os
            
            image_generator = WelcomeImageGenerator()
            image_path = await image_generator.create_welcome_image(member)
            
            if not image_path:
                await ctx.send("❌ Failed to generate welcome image.")
                return
            
            # Send test welcome message
            with open(image_path, 'rb') as f:
                file = discord.File(f, filename='welcome.png')
                embed = discord.Embed(
                    title="🧪 Test - Selamat Datang!",
                    description=f"Selamat datang {member.mention} di {member.guild.name}. Jangan lupa mampir ke <#1396367392644530209> dan <#1396367050787786873>. Selamat berdiskusi 🎉",
                    color=0x00ff00
                )
                embed.set_image(url="attachment://welcome.png")
                embed.set_footer(text=f"Member #{member.guild.member_count}")
                
                await welcome_channel.send(embed=embed, file=file)
            
            # Clean up
            try:
                os.remove(image_path)
            except OSError:
                pass
            
            await ctx.send("✅ Test welcome message sent!")
            
        except Exception as e:
            logger.error(f'Error testing welcome: {str(e)}')
            await ctx.send("❌ An error occurred while testing the welcome message.")
    
    @bot.command(name='welcomehelp')
    async def help_command(ctx):
        """Show bot help information."""
        embed = discord.Embed(
            title="🤖 Welcome Bot Help",
            description="A bot that creates custom welcome images for new members!",
            color=0x0099ff
        )
        
        embed.add_field(
            name="🔧 Setup Commands",
            value=(
                "`!setwelcome [#channel]` - Set welcome channel\n"
                "`!welcomeinfo` - Show current welcome settings\n"
                "`!removewelcome` - Disable welcome messages\n"
            ),
            inline=False
        )
        
        embed.add_field(
            name="🧪 Testing",
            value="`!testwelcome [@member]` - Test welcome message",
            inline=False
        )
        
        embed.add_field(
            name="📋 Permissions Required",
            value="Manage Server permission needed for setup commands",
            inline=False
        )
        
        embed.set_footer(text="The bot automatically creates welcome images when new members join!")
        
        await ctx.send(embed=embed)
    
    # Wiki Commands
    @bot.command(name='wiki')
    async def wiki_get(ctx, *, title):
        """Get a wiki entry."""
        try:
            entry = wiki.get_entry(title, ctx.guild.id)
            if not entry:
                await ctx.send(f"❌ Wiki entry '{title}' tidak ditemukan. Gunakan `!wikisearch {title}` untuk mencari.")
                return
            
            embed = discord.Embed(
                title=f"📖 {entry['title']}",
                description=entry['content'],
                color=0x0099ff
            )
            embed.set_footer(text=f"Dibuat: {entry['created_at'][:10]} • Edit: {entry['edit_count']} kali")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f'Error getting wiki entry: {str(e)}')
            await ctx.send("❌ Terjadi kesalahan saat mengambil wiki entry.")
    
    @bot.command(name='wikiadd')
    @commands.has_permissions(manage_messages=True)
    async def wiki_add(ctx, title, *, content):
        """Add a new wiki entry."""
        try:
            # Check if entry already exists
            existing = wiki.get_entry(title, ctx.guild.id)
            if existing:
                await ctx.send(f"❌ Wiki entry '{title}' sudah ada. Gunakan `!wikiedit` untuk mengedit.")
                return
            
            success = wiki.add_entry(title, content, ctx.author.id, ctx.guild.id)
            if success:
                embed = discord.Embed(
                    title="✅ Wiki Entry Ditambahkan",
                    description=f"Entry **{title}** berhasil ditambahkan ke wiki.",
                    color=0x00ff00
                )
                await ctx.send(embed=embed)
            else:
                await ctx.send("❌ Gagal menambahkan wiki entry.")
                
        except Exception as e:
            logger.error(f'Error adding wiki entry: {str(e)}')
            await ctx.send("❌ Terjadi kesalahan saat menambahkan wiki entry.")
    
    @bot.command(name='wikiedit')
    @commands.has_permissions(manage_messages=True)
    async def wiki_edit(ctx, title, *, content):
        """Edit an existing wiki entry."""
        try:
            success = wiki.edit_entry(title, content, ctx.author.id, ctx.guild.id)
            if success:
                embed = discord.Embed(
                    title="✅ Wiki Entry Diperbarui",
                    description=f"Entry **{title}** berhasil diperbarui.",
                    color=0x00ff00
                )
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"❌ Wiki entry '{title}' tidak ditemukan.")
                
        except Exception as e:
            logger.error(f'Error editing wiki entry: {str(e)}')
            await ctx.send("❌ Terjadi kesalahan saat mengedit wiki entry.")
    
    @bot.command(name='wikidelete')
    @commands.has_permissions(manage_messages=True)
    async def wiki_delete(ctx, *, title):
        """Delete a wiki entry."""
        try:
            success = wiki.delete_entry(title, ctx.guild.id)
            if success:
                embed = discord.Embed(
                    title="✅ Wiki Entry Dihapus",
                    description=f"Entry **{title}** berhasil dihapus dari wiki.",
                    color=0x00ff00
                )
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"❌ Wiki entry '{title}' tidak ditemukan.")
                
        except Exception as e:
            logger.error(f'Error deleting wiki entry: {str(e)}')
            await ctx.send("❌ Terjadi kesalahan saat menghapus wiki entry.")
    
    @bot.command(name='wikisearch')
    async def wiki_search(ctx, *, query):
        """Search wiki entries."""
        try:
            results = wiki.search_entries(query, ctx.guild.id, limit=10)
            
            if not results:
                await ctx.send(f"❌ Tidak ditemukan hasil untuk '{query}'.")
                return
            
            embed = discord.Embed(
                title=f"🔍 Hasil Pencarian: '{query}'",
                color=0x0099ff
            )
            
            for i, result in enumerate(results[:5], 1):
                match_icon = "📖" if result['match_type'] == 'title' else "📝"
                embed.add_field(
                    name=f"{match_icon} {result['title']}",
                    value=result['content'],
                    inline=False
                )
            
            if len(results) > 5:
                embed.set_footer(text=f"Menampilkan 5 dari {len(results)} hasil. Gunakan judul spesifik untuk melihat entry.")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f'Error searching wiki: {str(e)}')
            await ctx.send("❌ Terjadi kesalahan saat mencari wiki entries.")
    
    @bot.command(name='wikilist')
    async def wiki_list(ctx):
        """List all wiki entries."""
        try:
            entries = wiki.list_entries(ctx.guild.id, limit=15)
            
            if not entries:
                await ctx.send("📖 Belum ada wiki entries di server ini. Gunakan `!wikiadd` untuk menambahkan.")
                return
            
            embed = discord.Embed(
                title="📚 Daftar Wiki Entries",
                color=0x0099ff
            )
            
            for entry in entries:
                embed.add_field(
                    name=entry['title'],
                    value=f"{entry['content']}\n*Edit: {entry['edit_count']} kali*",
                    inline=True
                )
            
            embed.set_footer(text=f"Total: {len(entries)} entries. Gunakan !wiki <judul> untuk membaca.")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f'Error listing wiki entries: {str(e)}')
            await ctx.send("❌ Terjadi kesalahan saat menampilkan wiki entries.")
    
    @bot.command(name='wikihelp')
    async def wiki_help(ctx):
        """Show wiki help information."""
        embed = discord.Embed(
            title="📖 Wiki System Help",
            description="Sistem wiki untuk menyimpan informasi server",
            color=0x0099ff
        )
        
        embed.add_field(
            name="👀 Membaca Wiki",
            value=(
                "`!wiki <judul>` - Lihat wiki entry\n"
                "`!wikisearch <kata>` - Cari dalam wiki\n"
                "`!wikilist` - Daftar semua entries\n"
            ),
            inline=False
        )
        
        embed.add_field(
            name="✏️ Mengelola Wiki (Perlu permission)",
            value=(
                "`!wikiadd <judul> <isi>` - Tambah entry baru\n"
                "`!wikiedit <judul> <isi>` - Edit entry\n"
                "`!wikidelete <judul>` - Hapus entry\n"
            ),
            inline=False
        )
        
        embed.add_field(
            name="💡 Tips",
            value="• Judul tidak case-sensitive\n• Gunakan tanda kutip untuk judul dengan spasi\n• Konten bisa panjang dan multi-line",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    # Lord of Mysteries Wiki Commands
    @bot.command(name='lomchar', aliases=['character'])
    async def lom_character(ctx, *, character_name):
        """Search for a Lord of Mysteries character."""
        try:
            # Send initial message
            search_msg = await ctx.send(f"🔍 Mencari informasi karakter '{character_name}' di Lord of Mysteries Wiki...")
            
            info = await lom_scraper.search_character(character_name)
            if not info:
                await search_msg.edit(content=f"❌ Karakter '{character_name}' tidak ditemukan di wiki.")
                return
            
            embed = discord.Embed(
                title=f"👤 {info['title']}",
                description=info['description'][:1000] if info['description'] else "Informasi umum tidak tersedia",
                color=0x8B4513,
                url=info.get('source_url', '')
            )
            
            # Physical Description
            if info.get('physical_description'):
                embed.add_field(
                    name="🧍 Physical Description",
                    value=info['physical_description'][:1000] if len(info['physical_description']) > 1000 else info['physical_description'],
                    inline=False
                )
            
            # Pathways & Authorities
            if info.get('pathways_authorities'):
                embed.add_field(
                    name="⚡ Pathways & Authorities",
                    value=info['pathways_authorities'][:1000] if len(info['pathways_authorities']) > 1000 else info['pathways_authorities'],
                    inline=False
                )
            
            embed.set_footer(text="Sumber: Lord of Mysteries Wiki")
            
            await search_msg.edit(content="", embed=embed)
            
        except Exception as e:
            logger.error(f'Error searching LOM character: {str(e)}')
            await ctx.send("❌ Terjadi kesalahan saat mencari karakter.")
    
    @bot.command(name='lompath', aliases=['pathway'])
    async def lom_pathway(ctx, *, pathway_name):
        """Search for a Lord of Mysteries pathway."""
        try:
            await ctx.send(f"🔍 Mencari informasi pathway '{pathway_name}' di Lord of Mysteries Wiki...")
            
            info = await lom_scraper.search_pathway(pathway_name)
            if not info:
                await ctx.send(f"❌ Pathway '{pathway_name}' tidak ditemukan di wiki.")
                return
            
            embed = discord.Embed(
                title=f"🌟 {info['title']}",
                color=0x4B0082,
                url=info.get('source_url', '')
            )
            
            # General Information
            if info.get('general_information'):
                embed.add_field(
                    name="📋 General Information",
                    value=info['general_information'][:1000] if len(info['general_information']) > 1000 else info['general_information'],
                    inline=False
                )
            
            # Sequence Levels
            if info.get('sequence_levels'):
                embed.add_field(
                    name="⚡ Sequence Levels",
                    value=info['sequence_levels'][:1000] if len(info['sequence_levels']) > 1000 else info['sequence_levels'],
                    inline=False
                )
            
            embed.set_footer(text="Sumber: Lord of Mysteries Wiki")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f'Error searching LOM pathway: {str(e)}')
            await ctx.send("❌ Terjadi kesalahan saat mencari pathway.")
    
    @bot.command(name='lomsearch')
    async def lom_search(ctx, *, search_term):
        """Search for anything on Lord of Mysteries Wiki."""
        try:
            await ctx.send(f"🔍 Mencari '{search_term}' di Lord of Mysteries Wiki...")
            
            info = await lom_scraper.search_general(search_term)
            if not info:
                await ctx.send(f"❌ '{search_term}' tidak ditemukan di wiki.")
                return
            
            embed = discord.Embed(
                title=f"📖 {info['title']}",
                description=info['description'][:2000] if len(info['description']) > 2000 else info['description'],
                color=0x800080,
                url=info.get('source_url', '')
            )
            
            embed.set_footer(text="Sumber: Lord of Mysteries Wiki")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f'Error searching LOM wiki: {str(e)}')
            await ctx.send("❌ Terjadi kesalahan saat mencari di wiki.")
    
    @bot.command(name='lomfact')
    async def lom_fact(ctx):
        """Get a random Lord of Mysteries fact."""
        try:
            fact_msg = await ctx.send("🎲 Mengambil fakta random dari Lord of Mysteries Wiki...")
            
            fact = await lom_scraper.get_random_fact()
            if not fact:
                await fact_msg.edit(content="❌ Tidak bisa mengambil fakta saat ini.")
                return
            
            embed = discord.Embed(
                title="🎲 Random Lord of Mysteries Fact",
                description=fact,
                color=0xFF6347
            )
            
            embed.set_footer(text="Sumber: Lord of Mysteries Wiki")
            
            await fact_msg.edit(content="", embed=embed)
            
        except Exception as e:
            logger.error(f'Error getting LOM fact: {str(e)}')
            await ctx.send("❌ Terjadi kesalahan saat mengambil fakta.")
    
    @bot.command(name='lomhelp')
    async def lom_help(ctx):
        """Show Lord of Mysteries wiki commands help."""
        embed = discord.Embed(
            title="📚 Lord of Mysteries Wiki Commands",
            description="Commands untuk mengakses informasi dari Lord of Mysteries Wiki",
            color=0x4B0082
        )
        
        embed.add_field(
            name="👤 Karakter & Lore",
            value=(
                "`!lomchar <nama>` - Cari karakter\n"
                "`!lompath <nama>` - Cari pathway\n"
                "`!lomsearch <kata>` - Cari apapun di wiki\n"
                "`!lomfact` - Fakta random\n"
            ),
            inline=False
        )
        
        embed.add_field(
            name="💡 Tips",
            value=(
                "• Gunakan nama bahasa Inggris untuk hasil terbaik\n"
                "• Contoh: `!lomchar Klein Moretti`\n"
                "• Contoh: `!lompath Fool`\n"
                "• Bot akan mencari di wiki resmi Lord of Mysteries"
            ),
            inline=False
        )
        
        embed.set_footer(text="Data diambil langsung dari lordofthemysteries.fandom.com")
        
        await ctx.send(embed=embed)
    
    # Test command untuk debugging
    @bot.command(name='test')
    async def test_command(ctx):
        """Test command untuk memastikan bot berfungsi."""
        try:
            embed = discord.Embed(
                title="✅ Bot Test",
                description="Bot berfungsi dengan baik! Semua sistem normal.",
                color=0x00ff00
            )
            embed.add_field(
                name="Status", 
                value="🟢 Online dan siap digunakan",
                inline=False
            )
            await ctx.send(embed=embed)
            logger.info(f"Test command executed successfully by {ctx.author}")
            
        except Exception as e:
            logger.error(f'Error in test command: {str(e)}')
            await ctx.send("❌ Terjadi error pada test command.")
    
    # Error handlers for commands
    @set_welcome_channel.error
    @remove_welcome_channel.error
    @test_welcome.error
    @wiki_add.error
    @wiki_edit.error
    @wiki_delete.error
    async def permission_error(ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You need the 'Manage Messages' permission to use this command.")
        else:
            logger.error(f'Command error: {str(error)}')
