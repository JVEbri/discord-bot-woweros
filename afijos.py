from discord.ext import commands
import requests
from PIL import Image
from io import BytesIO
class Afijos:
    def __init__(self):
        self.afijos_combinaciones = [
            [9, 134, 11],
            [10, 3, 123],
            [9, 124, 6],
            [10, 134, 7],
            [9, 136, 123],
            [10, 135, 6],
            [9, 3, 8],
            [10, 124, 11],
            [9, 135, 7],
            [10, 136, 8],
        ]
    
    def mostrar_combinaciones(self):
       return self.afijos_combinaciones
    
    async def get_week_affixes(self):
        url = "https://mythicpl.us/affix-eu"
        response = requests.get(url)
        if response.status_code == 200:
            affix_data = response.json()
            affix_ids = [affix['id'] for affix in affix_data.get('affix_details', [])]
            return affix_ids           
        else:
            return None
            
    async def get_next_week(self):
        current_affixes = await self.get_week_affixes()
        for i, combination in enumerate(self.afijos_combinaciones):
                if combination == current_affixes:
                    # Si la combinación actual es la última, la próxima será la primera
                    next_index = (i + 1) % len(self.afijos_combinaciones)
                    next_affixes = self.afijos_combinaciones[next_index]
                    return current_affixes, next_affixes

        return None  # 
    
    async def fetch_affix_details(self, affix_ids):
        affix_details = []
        for affix_id in affix_ids:
            url = f"https://nether.wowhead.com/tooltip/affix/{affix_id}?dataEnv=1&locale=6"
            response = requests.get(url)
            if response.status_code == 200:
                affix_data = response.json()
                icon = affix_data['icon']
                icon_url = f"https://wow.zamimg.com/images/wow/icons/large/{icon}.jpg"
                affix_details.append({  
                    'icon': icon_url,
                    'name': affix_data['name'],
                })
            else:
                print(f"Error al obtener la información del afijo {affix_id}: {response.status_code}")
        
        return affix_details

    async def get_affix_info(self):
        current_affixes, next_affixes = await self.get_next_week()
        
        # Obtener detalles de los afijos actuales y de la próxima semana
        current_affix_details = await self.fetch_affix_details(current_affixes)
        next_affix_details = await self.fetch_affix_details(next_affixes)

        return current_affix_details, next_affix_details

    async def combine_images(self, affix_icons, margin=10):
        images = []
        for icon_url in affix_icons:
            response = requests.get(icon_url)
            img = Image.open(BytesIO(response.content))
            images.append(img)

        # Calcular el tamaño total de la imagen combinada con márgenes
        widths, heights = zip(*(i.size for i in images))
        total_width = sum(widths) + margin * (len(images) - 1)  # Añadir espacio entre imágenes
        max_height = max(heights)

        # Crear una nueva imagen con el tamaño calculado
        new_image = Image.new('RGBA', (total_width, max_height))

        # Pegar las imágenes una al lado de la otra con margen
        x_offset = 0
        for img in images:
            new_image.paste(img, (x_offset, 0))
            x_offset += img.width + margin  # Añadir el margen al desplazamiento horizontal

        # Guardar la imagen combinada en un buffer de bytes
        image_buffer = BytesIO()
        new_image.save(image_buffer, format='PNG')
        image_buffer.seek(0)
        return image_buffer