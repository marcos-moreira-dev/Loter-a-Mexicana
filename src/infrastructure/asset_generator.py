"""Generador de assets visuales para las cartas de la Lotería Mexicana."""

import os
from PIL import Image, ImageDraw, ImageFont
from typing import Tuple, List


def crear_carta(
    id_carta: int,
    nombre: str,
    descripcion: str,
    size: Tuple[int, int] = (300, 400),
    output_path: str = ""
) -> None:
    """Crea una imagen de carta de Lotería Mexicana.
    
    Args:
        id_carta: Número de la carta (1-54).
        nombre: Nombre tradicional de la carta.
        descripcion: Descripción de la imagen.
        size: Tamaño de la imagen (ancho, alto).
        output_path: Ruta donde guardar la imagen.
    """
    # Crear imagen base
    img = Image.new('RGB', size, color=(255, 248, 220))  # Fondo crema
    draw = ImageDraw.Draw(img)
    
    # Colores
    color_borde = (231, 76, 60)  # Rojo coral
    color_texto = (44, 62, 80)   # Azul oscuro
    color_numero = (241, 196, 15)  # Amarillo dorado
    color_fondo_numero = (231, 76, 60)  # Rojo coral
    
    # Dibujar borde decorativo
    borde = 8
    draw.rectangle([borde, borde, size[0]-borde, size[1]-borde], outline=color_borde, width=4)
    
    # Dibujar número en esquina superior izquierda
    numero_texto = f"{id_carta:02d}"
    draw.ellipse([15, 15, 65, 65], fill=color_fondo_numero)
    
    # Intentar usar fuente por defecto o crear texto
    try:
        font_numero = ImageFont.truetype("arial.ttf", 28)
        font_titulo = ImageFont.truetype("arial.ttf", 24)
        font_desc = ImageFont.truetype("arial.ttf", 14)
    except:
        font_numero = ImageFont.load_default()
        font_titulo = ImageFont.load_default()
        font_desc = ImageFont.load_default()
    
    # Centrar número
    bbox = draw.textbbox((0, 0), numero_texto, font=font_numero)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = 15 + (50 - text_width) // 2
    y = 15 + (50 - text_height) // 2 - 5
    draw.text((x, y), numero_texto, fill=(255, 255, 255), font=font_numero)
    
    # Dibujar ilustración central (representación simbólica)
    centro_x = size[0] // 2
    centro_y = size[1] // 2 - 20
    
    # Dibujar forma decorativa según el tipo de carta
    color_forma = (
        (231, 76, 60),    # Rojo
        (46, 204, 113),   # Verde
        (52, 152, 219),   # Azul
        (241, 196, 15),   # Amarillo
        (155, 89, 182),   # Púrpura
        (230, 126, 34),   # Naranja
    )[id_carta % 6]
    
    # Dibujar círculo central decorativo
    radio = 80
    draw.ellipse(
        [centro_x - radio, centro_y - radio, centro_x + radio, centro_y + radio],
        fill=color_forma,
        outline=color_borde,
        width=3
    )
    
    # Dibujar emoji o símbolo representativo (primer carácter del nombre)
    simbolo = nombre[3] if nombre.startswith("El ") else (nombre[4] if nombre.startswith("La ") else nombre[0])
    
    try:
        font_simbolo = ImageFont.truetype("seguisym.ttf", 72)  # Fuente con emojis
    except:
        font_simbolo = font_titulo
        simbolo = str(id_carta)
    
    bbox = draw.textbbox((0, 0), simbolo, font=font_simbolo)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = centro_x - text_width // 2
    y = centro_y - text_height // 2
    draw.text((x, y), simbolo, fill=(255, 255, 255), font=font_simbolo)
    
    # Dibujar nombre en la parte inferior
    y_nombre = size[1] - 80
    bbox = draw.textbbox((0, 0), nombre, font=font_titulo)
    text_width = bbox[2] - bbox[0]
    x = (size[0] - text_width) // 2
    draw.text((x, y_nombre), nombre, fill=color_texto, font=font_titulo)
    
    # Dibujar línea decorativa
    y_linea = y_nombre - 15
    draw.line([(50, y_linea), (size[0]-50, y_linea)], fill=color_borde, width=2)
    
    # Guardar imagen
    img.save(output_path, 'PNG')


def generar_cartas_si_no_existen(
    assets_path: str = "assets/cards",
    *,
    verbose: bool = True,
) -> None:
    """Genera todas las cartas si no existen.
    
    Args:
        assets_path: Ruta donde guardar las cartas.
    """
    # Crear directorio si no existe
    os.makedirs(assets_path, exist_ok=True)
    
    # Lista de cartas tradicionales
    cartas: List[Tuple[int, str, str]] = [
        (1, "El Gallo", "Gallo cantando"),
        (2, "El Diablo", "Diablo travieso"),
        (3, "La Dama", "Dama elegante"),
        (4, "El Catrín", "Caballero distinguido"),
        (5, "El Paraguas", "Paraguas protector"),
        (6, "La Sirena", "Sirena marina"),
        (7, "La Escalera", "Escalera al cielo"),
        (8, "La Botella", "Botella de licor"),
        (9, "El Barril", "Barril de cerveza"),
        (10, "El Árbol", "Árbol frondoso"),
        (11, "El Melón", "Melón dulce"),
        (12, "El Valiente", "Soldado valiente"),
        (13, "El Gorrito", "Gorrito de fiesta"),
        (14, "La Muerte", "Calavera"),
        (15, "La Pera", "Pera madura"),
        (16, "La Bandera", "Bandera nacional"),
        (17, "El Bandolón", "Instrumento musical"),
        (18, "El Violoncello", "Violonchelo"),
        (19, "La Garza", "Ave garza"),
        (20, "El Pájaro", "Pájaro cantor"),
        (21, "La Mano", "Mano con dedos"),
        (22, "La Bota", "Bota de cuero"),
        (23, "La Luna", "Luna en el cielo"),
        (24, "El Cotorro", "Pájaro cotorro"),
        (25, "El Borracho", "Hombre borracho"),
        (26, "El Negrito", "Niño sonriente"),
        (27, "El Corazón", "Corazón rojo"),
        (28, "La Sandía", "Sandía fresca"),
        (29, "El Tambor", "Tambor musical"),
        (30, "El Camarón", "Camarón marino"),
        (31, "Las Jaras", "Jaras para ropear"),
        (32, "El Músico", "Músico tocando"),
        (33, "La Araña", "Araña tejiendo"),
        (34, "El Soldado", "Soldado militar"),
        (35, "La Estrella", "Estrella brillante"),
        (36, "El Cazo", "Cazo de cocina"),
        (37, "El Mundo", "Planeta tierra"),
        (38, "El Apache", "Indígena apache"),
        (39, "El Nopal", "Cactus nopal"),
        (40, "El Alacrán", "Escorpión alacrán"),
        (41, "La Rosa", "Flor rosa"),
        (42, "La Calavera", "Calavera decorada"),
        (43, "La Campana", "Campana sonando"),
        (44, "El Cantarito", "Cantaro de barro"),
        (45, "El Venado", "Ciervo venado"),
        (46, "El Sol", "Sol brillante"),
        (47, "La Corona", "Corona real"),
        (48, "La Chalupa", "Barca chalupa"),
        (49, "El Pino", "Árbol pino"),
        (50, "El Pescado", "Pez pescado"),
        (51, "La Palma", "Palmera palma"),
        (52, "La Maceta", "Maceta con flores"),
        (53, "El Arpa", "Arpa musical"),
        (54, "La Rana", "Rana saltando"),
    ]
    
    # Verificar qué cartas faltan
    faltantes = []
    for id_carta, nombre, desc in cartas:
        path = os.path.join(assets_path, f"carta_{id_carta:02d}.png")
        if not os.path.exists(path):
            faltantes.append((id_carta, nombre, desc, path))
    
    if faltantes:
        if verbose:
            print(f"Generando {len(faltantes)} cartas...")
        for id_carta, nombre, desc, path in faltantes:
            crear_carta(id_carta, nombre, desc, output_path=path)
            if verbose:
                print(f"  [OK] Carta {id_carta:02d}: {nombre}")
        if verbose:
            print("Cartas generadas exitosamente!")
    elif verbose:
        print("Todas las cartas ya existen.")


if __name__ == '__main__':
    generar_cartas_si_no_existen()
