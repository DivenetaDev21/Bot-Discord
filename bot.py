import discord
from discord.ext import commands
import datetime

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.presences = True
intents.voice_states = True
intents.guild_messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

LOG_CHANNEL_ID = 1280193940049498123 #id do canal q vai enviar as logs

@bot.event
async def on_ready():
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        embed = discord.Embed(
            title="Bot de Logs Ativo",
            description=f"Log de atividades iniciado em **{datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}**",
            color=discord.Color.green()
        )
        embed.set_footer(text="Desenvolvido por AnonymousDeveloper")
        await log_channel.send(embed=embed)
    print(f'Bot conectado como {bot.user.name}. Desenvolvido por Anonymous Developer.')

def log_embed(title, description, member, color=discord.Color.blue()):
    embed = discord.Embed(
        title=title,
        description=description,
        color=color,
        timestamp=datetime.datetime.utcnow()
    )
    embed.set_footer(text=f"Ação realizada por {member}", icon_url=member.avatar.url if member.avatar else None)
    return embed

@bot.event
async def on_member_update(before, after):
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if before.roles != after.roles:
        added_roles = [role for role in after.roles if role not in before.roles]
        removed_roles = [role for role in before.roles if role not in after.roles]
        if added_roles:
            for role in added_roles:
                async for entry in after.guild.audit_logs(limit=1, action=discord.AuditLogAction.member_role_update):
                    executor = entry.user if entry else "Desconhecido"
                embed = log_embed(
                    title="📌 Cargo Adicionado",
                    description=f"**{after.display_name}** recebeu o cargo **{role.name}**.",
                    member=executor
                )
                await log_channel.send(embed=embed)
        if removed_roles:
            for role in removed_roles:
                async for entry in after.guild.audit_logs(limit=1, action=discord.AuditLogAction.member_role_update):
                    executor = entry.user if entry else "Desconhecido"
                embed = log_embed(
                    title="🚫 Cargo Removido",
                    description=f"**{after.display_name}** perdeu o cargo **{role.name}**.",
                    member=executor,
                    color=discord.Color.red()
                )
                await log_channel.send(embed=embed)

@bot.event
async def on_guild_channel_create(channel):
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    async for entry in channel.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_create):
        creator = entry.user if entry else "Desconhecido"
    embed = log_embed(
        title="📁 Canal Criado",
        description=f"Um novo canal **{channel.name}** foi criado ({channel.type}).",
        member=creator
    )
    await log_channel.send(embed=embed)

@bot.event
async def on_guild_channel_delete(channel):
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    async for entry in channel.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete):
        deleter = entry.user if entry else "Desconhecido"
    embed = log_embed(
        title="🗑️ Canal Deletado",
        description=f"O canal **{channel.name}** foi deletado.",
        member=deleter,
        color=discord.Color.red()
    )
    await log_channel.send(embed=embed)

@bot.event
async def on_voice_state_update(member, before, after):
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if before.channel is None and after.channel is not None:
        embed = log_embed(
            title="🎙️ Entrou no Canal de Voz",
            description=f"**{member.display_name}** entrou no canal **{after.channel.name}**.",
            member=member
        )
        await log_channel.send(embed=embed)
    elif before.channel is not None and after.channel is None:
        embed = log_embed(
            title="👋 Saiu do Canal de Voz",
            description=f"**{member.display_name}** saiu do canal **{before.channel.name}**.",
            member=member,
            color=discord.Color.red()
        )
        await log_channel.send(embed=embed)
    elif before.channel != after.channel:
        embed = log_embed(
            title="🔄 Mudou de Canal de Voz",
            description=f"**{member.display_name}** mudou de **{before.channel.name}** para **{after.channel.name}**.",
            member=member,
            color=discord.Color.orange()
        )
        await log_channel.send(embed=embed)

@bot.event
async def on_member_join(member):
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    embed = log_embed(
        title="📥 Novo Membro",
        description=f"**{member.display_name}** acabou de entrar no servidor.",
        member=member,
        color=discord.Color.green()
    )
    await log_channel.send(embed=embed)

@bot.event
async def on_member_remove(member):
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    embed = log_embed(
        title="📤 Membro Saiu",
        description=f"**{member.display_name}** saiu do servidor.",
        member=member,
        color=discord.Color.red()
    )
    await log_channel.send(embed=embed)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.content.isupper() and len(message.content) > 5:
        await message.delete()
        warning_msg = await message.channel.send(f"{message.author.mention} por favor, não use CAPS LOCK.")
        await warning_msg.delete(delay=5)
    await bot.process_commands(message)

bot.run('TOKEN BOT')
