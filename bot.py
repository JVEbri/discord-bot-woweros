import discord
from discord.ext import commands
import requests
from datetime import datetime
from afijos import Afijos
import os
from dotenv import load_dotenv
load_dotenv()


# Obtener el token desde la variable de entorno
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
# Datos del cliente
client_id = '7c9cc266513f45188d2328232366ab86'
client_secret = 'AGJHyd7fanHMHgX33JFdWdqrnsUgbSNO'

def get_time(timestamp_ms):
    timestamp = datetime.utcfromtimestamp(timestamp_ms / 1000)  # Convertir de ms a segundos
    current_time = datetime.utcnow()
    
    # Calcular el tiempo transcurrido
    time_diff = current_time - timestamp
    hours_passed = time_diff.total_seconds() / 3600  # Convertir segundos a horas
    
    if hours_passed < 1:
        minutes_passed = int(time_diff.total_seconds() / 60) 
        formatted_time = f"Hace {minutes_passed} minutos"
    else:
        formatted_time = f"Hace {int(hours_passed)} horas"
    
    return formatted_time

async def getAccesToken():
    url = 'https://oauth.battle.net/token'
    # Encabezados y datos
    auth = (client_id, client_secret)
    data = {'grant_type': 'client_credentials'}

    # Realiza la petición
    response = requests.post(url, data=data, auth=auth)
    # Verifica si la petición fue exitosa
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data['access_token']
        print(f"Access Token: {access_token}")
        return access_token
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None
    
async def get_wow_token_price(access_token):
    url = 'https://eu.api.blizzard.com/data/wow/token/?namespace=dynamic-eu'
    
    # Configurar los encabezados con el token de acceso
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    # Realizar la petición GET
    response = requests.get(url, headers=headers)

    # Verificar si la petición fue exitosa
    if response.status_code == 200:
        data = response.json()
        
        # Extraer y convertir el timestamp
        timestamp_ms = data['last_updated_timestamp']
        formatted_time = get_time(timestamp_ms)

        # Extraer y convertir el precio
        raw_price = data['price']
        formatted_price = f"{raw_price / 10000:,.0f}".replace(',', '.')


        # Imprimir los resultados
        print(f"Last Updated: {formatted_time}")
        print(f"Token Price: {formatted_price} gold")
        
        return {
            'timestamp': formatted_time,
            'price': formatted_price
        }
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

# Configuración de los intents
intents = discord.Intents.default()
intents.message_content = True  # Permite que el bot lea el contenido de los mensajes

# Inicializa el bot con un prefijo para los comandos
bot = commands.Bot(command_prefix="!", intents=intents)

# Evento: Se ejecuta cuando el bot se conecta exitosamente a Discord
@bot.event
async def on_ready():
    print(f'{bot.user.name} ha iniciado sesión y está listo para funcionar!')

@bot.command(name='ayuda')
async def ayuda(ctx):
    embed = discord.Embed(title="Comandos Disponibles", color=discord.Color.green())

    # Recorre todos los comandos registrados en el bot
    for command in bot.commands:
        if not command.hidden:  # Opcional: Ignora los comandos ocultos
            embed.add_field(
                name=f"!{command.name}",
                value=command.help or "No description provided.",
                inline=False
            )

    await ctx.send(embed=embed)

@bot.command(name='token',help='Mira el precio de la moneda de WoW')
async def token(ctx):
    access_token = await getAccesToken()
    gold = await get_wow_token_price(access_token)
    if gold:
        embed = discord.Embed(
            title="Región:\t 🇪🇺",  
            description=f"Oro: {gold['price']} 🪙",  
            color=discord.Color.blue()
        )
        
        embed.set_author(name="Ficha del WoW")
        embed.set_footer(text=gold['timestamp'])
        
        # Enviar el embed
        await ctx.send(embed=embed)
    else:
        await ctx.send("Hubo un problema al obtener los datos del token.")

# Comando: Responde "¡Hola! Estoy funcionando correctamente." cuando se escribe !hola en el chat
@bot.command(name='afix',help='Comprueba los afijos de esta semana y la siguiente')
async def afix(ctx):
    afijos = Afijos()  # Crear una instancia de la clase Afijos
    current_week, next_week = await afijos.get_affix_info()

    # Combinar imágenes para la semana actual
    current_icons = [affix['icon'] for affix in current_week]
    combined_image_current = await afijos.combine_images(current_icons)
    file_current = discord.File(combined_image_current, filename="current_affixes.png")

    # Crear embed para la semana actual
    current_embed = discord.Embed(title="Afijos de esta semana", color=discord.Color.blue())
    for affix in current_week:
        current_embed.add_field(name=affix['name'], value="", inline=True)
    current_embed.set_image(url="attachment://current_affixes.png")

    # Combinar imágenes para la próxima semana
    next_icons = [affix['icon'] for affix in next_week]
    combined_image_next = await afijos.combine_images(next_icons)
    file_next = discord.File(combined_image_next, filename="next_affixes.png")

    # Crear embed para la próxima semana
    next_embed = discord.Embed(title="Afijos de la próxima semana", color=discord.Color.gold())
    for affix in next_week:
        next_embed.add_field(name=affix['name'], value="", inline=True)
    next_embed.set_image(url="attachment://next_affixes.png")

    # Enviar los embeds con las imágenes combinadas
    await ctx.send(embed=current_embed, file=file_current)
    await ctx.send(embed=next_embed, file=file_next)

@bot.command(name='jose',help='Aaaay José!!')
async def jose(ctx):
    await ctx.send("Aaaaay José!!",
                   embed=discord.Embed().set_image(url='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQd9stqrIOLvKVMVEALbwsvrBk_JtDoR8cKPg&s'))
    
@bot.command()
async def ejemplo(ctx):
    embed = discord.Embed(
        title="¡Este es un título!",
        description="Aquí hay una descripción del mensaje.",
        color=discord.Color.blue()  # Puedes cambiar el color
    )
    
    embed.set_author(name="Nombre del Autor", icon_url="https://wow.zamimg.com/images/wow/icons/large/ability_ironmaidens_whirlofblood.jpg")
    embed.set_thumbnail(url="https://wow.zamimg.com/images/wow/icons/large/ability_ironmaidens_whirlofblood.jpg")
    embed.add_field(name="Campo 1", value="Aquí hay un valor", inline=False)
    embed.add_field(name="Campo 2", value="Otro valor", inline=True)
    embed.set_image(url="https://wow.zamimg.com/images/wow/icons/large/ability_ironmaidens_whirlofblood.jpg")
    embed.set_footer(text="Este es el pie de página")

    await ctx.send(embed=embed)
    
@bot.command(name='c',help='¿Quieres amor?')
async def c(ctx):
    await ctx.send("¡Te envío un corazón! ❤️")

# Corre el bot con el token
bot.run(DISCORD_TOKEN)
