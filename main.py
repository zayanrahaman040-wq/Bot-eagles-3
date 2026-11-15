import discord
import os
from discord.ext import commands

TOKEN = os.getenv("TOKEN")
RUOLO_STAFF = "Staff"

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

presenza_attiva = False
presenti = set()

class BottonePresente(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="SONO PRESENTE", style=discord.ButtonStyle.green, emoji="🟢", custom_id="presente_btn")
    async def presente(self, interaction: discord.Interaction, button: discord.ui.Button):
        global presenti
        ruolo = discord.utils.get(interaction.guild.roles, name=RUOLO_STAFF)
        if ruolo not in interaction.user.roles:
            await interaction.response.send_message("❌ Tu non sei Staff!", ephemeral=True)
            return
        if interaction.user.id in presenti:
            await interaction.response.send_message("Sei già segnato! ✅", ephemeral=True)
            return
        presenti.add(interaction.user.id)
        await interaction.response.send_message(f"✅ {interaction.user.mention} segnato come PRESENTE! 🦅", ephemeral=True)

@bot.event
async def on_ready():
    print(f"Bot acceso come {bot.user} 🟢")
    bot.add_view(BottonePresente())

@bot.command()
@commands.has_permissions(administrator=True)
async def presenza(ctx):
    global presenza_attiva, presenti
    if presenza_attiva:
        await ctx.send("⚠️ Appello già attivo!")
        return
    presenza_attiva = True
    presenti = set()
    embed = discord.Embed(
        title="📢 APPELLO STAFF - MILANO RP 🦅",
        description="**TUTTI I PRESENTI CLICCANO IL BOTTONE VERDE!**\n\nChi non clicca = **RIMOZIONE RUOLO STAFF!**\n\nHai tempo finché un Founder non scrive `!stoppresenza`",
        color=0x00ff00
    )
    embed.set_footer(text="EAGLES - MILANO RP | Sistema Presenze")
    await ctx.send(embed=embed, view=BottonePresente())
    await ctx.send("✅ **APPELLO ATTIVATO!** Ora tutti devono cliccare 🟢")

@bot.command()
@commands.has_permissions(administrator=True)
async def stoppresenza(ctx):
    global presenza_attiva
    if not presenza_attiva:
        await ctx.send("⚠️ Nessun appello attivo!")
        return
    presenza_attiva = False
    guild = ctx.guild
    ruolo = discord.utils.get(guild.roles, name=RUOLO_STAFF)
    if not ruolo:
        await ctx.send(f"❌ Non trovo il ruolo `{RUOLO_STAFF}`!")
        return
    tutti_staff = [m for m in guild.members if ruolo in m.roles and not m.bot]
    lista_presenti = []
    lista_assenti = []
    for membro in tutti_staff:
        if membro.id in presenti:
            lista_presenti.append(membro.mention)
        else:
            lista_assenti.append(membro)
    for assente in lista_assenti:
        try:
            await assente.remove_roles(ruolo, reason="Assente all'appello Staff")
        except:
            pass
    testo_presenti = ", ".join(lista_presenti) if lista_presenti else "Nessuno!"
    testo_assenti = ", ".join([m.mention for m in lista_assenti]) if lista_assenti else "Nessuno! Tutti presenti! 🎉"
    embed = discord.Embed(title="✅ FINE APPELLO - MILANO RP", color=0xff0000)
    embed.add_field(name=f"🟢 PRESENTI ({len(lista_presenti)})", value=testo_presenti, inline=False)
    embed.add_field(name=f"🔴 ASSENTI - RUOLO RIMOSSO ({len(lista_assenti)})", value=testo_assenti, inline=False)
    await ctx.send(embed=embed)

bot.run(TOKEN)
