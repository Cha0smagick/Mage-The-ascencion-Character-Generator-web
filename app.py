import streamlit as st
import random
import time
from freeGPTFix import Client as ImageClient # Renombramos para evitar conflictos
from PIL import Image
import streamlit.components.v1 as components
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO
from reportlab.lib.enums import TA_JUSTIFY
from data import (
    first_names, last_names, natures, demeanors, essences, affiliations, sects,
    concepts, sexes, morality_levels, ages, body_types, hair_colors, hair_styles,
    heights, clothing_styles, expressions,
    eye_colors, ugliness_levels, distinguishing_marks, quirks, character_traits, 
    backgrounds, phobias, merits, flaws, cherished_possessions, secrets, goals,
    paradigms, all_spheres, affiliation_spheres, skin_tones, face_shapes,
    eye_shapes, nose_shapes, lip_shapes, hair_textures, ancestries)

# --- Inicialización del Estado de la Sesión (CRÍTICO) ---
# Esto debe estar al principio para evitar errores de 'AttributeError'.
if "mode" not in st.session_state:
    st.session_state.mode = "selection"
    st.session_state.character_sheet = None
    st.session_state.locks = {} # Nuevo: para guardar los bloqueos

if "generated_image" not in st.session_state:
    st.session_state.generated_image = None

# --- Funciones de Generación de Imagen ---
def generate_image_with_fallback(prompt):
    """Intenta generar una imagen con reintentos automáticos en caso de fallo."""
    max_retries = 5
    delay_seconds = 2
    provider = "pollinations"  # Usamos solo el proveedor que funciona.

    for attempt in range(max_retries):
        try:
            # Mostrar un mensaje al usuario en los reintentos
            if attempt > 0:
                st.info(f"Intento {attempt + 1} de {max_retries}... El servicio puede estar ocupado.")

            # Intentar generar la imagen con el proveedor actual
            image_bytes = ImageClient.create_generation(provider, prompt)
            if image_bytes:
                try:
                    # Intentar abrir los datos como una imagen
                    image = Image.open(BytesIO(image_bytes))
                    st.success(f"¡Imagen generada con `{provider}`!")
                    return image # Si tiene éxito, salimos de la función
                except Exception:
                    # Si no es una imagen, es un error del proveedor, así que lo tratamos como un fallo para reintentar.
                    st.warning(f"El proveedor `{provider}` devolvió una respuesta no válida en el intento {attempt + 1}. Reintentando...")
            else:
                st.warning(f"El proveedor `{provider}` no devolvió datos en el intento {attempt + 1}. Reintentando...")

        except Exception as e:
            st.warning(f"Fallo en el intento {attempt + 1} de {max_retries}: {e}. Reintentando en {delay_seconds} segundos...")
        
        # Esperar antes del siguiente intento (excepto en el último)
        if attempt < max_retries - 1:
            time.sleep(delay_seconds)

    st.error(f"No se pudo generar la imagen después de {max_retries} intentos. El servicio podría estar caído o sobrecargado.")
    return None

# Función para generar una descripción del personaje
def generate_description():
    return random.choice(character_traits)

# Función para generar un personaje
def generate_character():
    """
    Genera un personaje aleatorio pero válido según las reglas de Mago.
    Esta función ahora simula la distribución de puntos.
    """
    # Si no hay personaje previo, crea uno nuevo. Si no, usa el de la sesión.
    char = st.session_state.get("character_sheet", None)
    if char is None:
        char = initialize_character_build()

    locks = st.session_state.get("locks", {})

    # Asignaciones aleatorias de conceptos
    if not locks.get("Concepto"):
        char["Name"] = f"{random.choice(first_names)} {random.choice(last_names)}"
        char["Nature"] = random.choice(natures)
        char["Demeanor"] = random.choice(demeanors)
        char["Essence"] = random.choice(essences)
        char["Affiliation"] = random.choice(list(affiliation_spheres.keys()) + ["Hollow Ones"])
        char["Concept"] = random.choice(concepts)
        char["Sect"] = random.choice(sects)

    # Lógica de puntos aleatoria pero válida
    # Atributos (7/5/3)
    if not locks.get("Atributos"):
        # Reiniciar atributos antes de redistribuir
        for attr in char["Attributes"]: char["Attributes"][attr] = 1
        attr_categories = [
            ["Intelligence", "Wits", "Resolve"],
            ["Strength", "Dexterity", "Stamina"],
            ["Presence", "Manipulation", "Composure"]
        ]
        random.shuffle(attr_categories)
        points_dist = [7, 5, 3]
        for i, category in enumerate(attr_categories):
            points_to_spend = points_dist[i]
            for _ in range(points_to_spend):
                attr_to_raise = random.choice(category)
                if char["Attributes"][attr_to_raise] < 5:
                    char["Attributes"][attr_to_raise] += 1

    # Habilidades (13/9/5)
    if not locks.get("Habilidades"):
        for cat in ["Talents", "Skills", "Knowledges"]:
            for abil in char[cat]: char[cat][abil] = 0
        abil_categories = [
            list(char["Talents"].keys()),
            list(char["Skills"].keys()),
            list(char["Knowledges"].keys())
        ]
        random.shuffle(abil_categories)
        points_dist = [13, 9, 5]
        for i, category in enumerate(abil_categories):
            points_to_spend = points_dist[i]
            cat_name = ""
            if category[0] in char["Talents"]: cat_name = "Talents"
            elif category[0] in char["Skills"]: cat_name = "Skills"
            else: cat_name = "Knowledges"

            for _ in range(points_to_spend):
                abil_to_raise = random.choice(category)
                if char[cat_name][abil_to_raise] < 3: # Regla: no más de 3 en creación
                    char[cat_name][abil_to_raise] += 1

    # Trasfondos (5 puntos)
    if not locks.get("Ventajas"):
        for bg in char["Backgrounds"]: char["Backgrounds"][bg] = 0
        for _ in range(5):
            bg_to_raise = random.choice(list(char["Backgrounds"].keys()))
            if char["Backgrounds"][bg_to_raise] < 5:
                char["Backgrounds"][bg_to_raise] += 1

    # Esferas (1 en afinidad + 5 puntos)
    if not locks.get("Magia"):
        for sphere in char["Spheres"]: char["Spheres"][sphere] = 0
        primary_sphere = affiliation_spheres.get(char["Affiliation"])
        if primary_sphere:
            char["Spheres"][primary_sphere] = 1
        else: # Hollow Ones
            primary_sphere = random.choice(all_spheres)
            char["Spheres"][primary_sphere] = 1

        for _ in range(5):
            sphere_to_raise = random.choice(all_spheres)
            if char["Spheres"][sphere_to_raise] < 3:
                char["Spheres"][sphere_to_raise] += 1

    # Voluntad
    char["Advantages"]["Willpower"] = 5

    # Rellenar el resto de detalles
    if not locks.get("Perfil"):
        char["Morality"] = random.choice(morality_levels)
        char["Phobia"] = random.choice(phobias)
        char["Secret"] = random.choice(secrets)
        char["Goal"] = random.choice(goals)
        char["Paradigm"] = random.choice(paradigms)
        char["Cherished Possession"] = random.choice(cherished_possessions)
        char["Advantages"]["Merit"] = random.choice(merits)
        char["Advantages"]["Flaw"] = random.choice(flaws)
        char["Other Traits"]["Quirks"] = random.choice(quirks)
        char["Background"] = generate_background()

    if not locks.get("Apariencia"):
        char["Age"] = random.choice(ages)
        char["Sex"] = random.choice(sexes)
        char["Body Type"] = random.choice(body_types)
        char["Skin Tone"] = random.choice(skin_tones)
        char["Face Shape"] = random.choice(face_shapes)
        char["Nose Shape"] = random.choice(nose_shapes)
        char["Lip Shape"] = random.choice(lip_shapes)
        char["Ancestry"] = random.choice(ancestries)
        char["Height"] = random.choice(heights)
        char["Clothing Style"] = random.choice(clothing_styles)
        char["Expression"] = random.choice(expressions)
        char["Hair Color"] = random.choice(hair_colors)
        char["Hair Texture"] = random.choice(hair_textures)
        char["Hair Style"] = random.choice(hair_styles)
        char["Eye Color"] = random.choice(eye_colors)
        char["Eye Shape"] = random.choice(eye_shapes)
        char["Ugliness Level"] = random.choice(ugliness_levels)
        char["Distinguishing Mark"] = random.choice(distinguishing_marks)

    # La descripción siempre se regenera para reflejar los cambios
    char["Description"] = generate_description()
    char["Equipment"] = "A few personal items, a smartphone, and some cash."

    return char

# Función para generar un background de personaje basado en sus atributos
def generate_background():
    return random.choice(backgrounds)

# Función para generar ganchos de aventura para el Narrador
def generate_story_hooks(character):
    """Genera ideas de trama para el Narrador basadas en el personaje."""
    # Esta función ahora usa una plantilla para evitar llamadas a la IA.
    hook1 = (
        f"El secreto del personaje ('{character['Secret']}') está a punto de ser revelado por un antiguo conocido "
        f"que ha resurgido. Este individuo no busca dinero, sino usar la verdad para destruir la reputación del personaje "
        f"dentro de su facción, la '{character['Affiliation']}'."
    )
    hook2 = (
        f"La meta del personaje ('{character['Goal']}') se cruza directamente con los intereses de un poderoso "
        f"antagonista. Para avanzar, el personaje debe confrontar su mayor debilidad ('{character['Advantages']['Flaw']}') "
        f"en una situación donde podría costarle todo."
    )
    hook3 = (
        f"Un objeto o persona relacionada con el trasfondo del personaje ('{character['Background']}') aparece de repente, "
        f"pero está corrompido por una fuerza misteriosa. Investigar su origen podría llevar al personaje a un lugar "
        f"peligroso que pone a prueba su paradigma ('{character['Paradigm']}') y su moralidad."
    )
    return f"1. {hook1}\n\n2. {hook2}\n\n3. {hook3}"

# Función para generar una historia RÁPIDA Y GRATUITA usando una plantilla
def generate_story_template(character):
    """Genera una historia de personaje usando una plantilla predefinida, sin costo de IA."""
    try:
        highest_attr = max(character['Attributes'], key=character['Attributes'].get)
        lowest_attr = min(character['Attributes'], key=character['Attributes'].get)
        
        # Filtrar habilidades con valor > 0 para que sea más significativo
        positive_talents = {k: v for k, v in character['Talents'].items() if v > 0}
        highest_talent = max(positive_talents, key=positive_talents.get) if positive_talents else "ninguno en particular"

        story = (
            f"{character['Name']} siempre fue diferente. Desde joven, mostró una increíble aptitud para **{highest_talent}**, "
            f"lo que a menudo contrastaba con su torpeza en áreas que requerían **{lowest_attr}**. "
            f"Su trasfondo como '{character['Background']}' le forzó a desarrollar rápidamente sus habilidades de supervivencia.\n\n"
            f"El Despertar de {character['Name']} no fue un evento sutil. Ocurrió en un momento de gran tensión, "
            f"donde su afinidad innata con la magia se manifestó de forma explosiva, atrayendo la atención de la facción '{character['Affiliation']}'. "
            f"Este evento les puso en el radar de la Tradición, quienes vieron en su esencia de '{character['Essence']}' un gran potencial.\n\n"
            f"Internamente, {character['Name']} es un torbellino. Su gran meta es '{character['Goal']}', pero este camino está plagado de obstáculos, "
            f"incluyendo su fobia a '{character['Phobia']}' y un oscuro secreto: '{character['Secret']}'. "
            f"Su forma de entender la magia se basa en un paradigma de '{character['Paradigm']}'. A menudo, su mayor fortaleza, su mérito de '{character['Advantages']['Merit']}', "
            f"es lo único que le permite sobreponerse a su debilitante defecto: '{character['Advantages']['Flaw']}'. "
            f"Siempre lleva consigo '{character['Cherished Possession']}', un objeto que le ancla a su pasado y le da fuerzas para continuar."
        )
        return story
    except Exception as e:
        return f"Error al generar la historia de plantilla: {e}. Es posible que el personaje no tenga talentos asignados."

# --- Configuración de la Página ---
st.set_page_config(
    page_title="Mage: The Ascension Character Creator",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Mage: The Ascension Character Creator")
st.markdown("#### Forge a destiny in a world of hidden magic. The Ascension War awaits.")
st.divider()

# --- NUEVA ESTRUCTURA ---

def initialize_character_build():
    """Crea una hoja de personaje en blanco con los valores iniciales."""
    return {
        "Name": "New Mage",
        "Nature": natures[0], "Demeanor": demeanors[0], "Essence": essences[0],
        "Affiliation": list(affiliation_spheres.keys())[0], "Sect": sects[0],
        "Concept": concepts[0], "Sex": sexes[0], "Morality": "Neutral",
        "Phobia": phobias[0], "Secret": secrets[0], "Goal": goals[0],
        "Paradigm": paradigms[0], "Cherished Possession": cherished_possessions[0],
        "Age": ages[0], "Body Type": body_types[0], "Skin Tone": skin_tones[0], "Ancestry": ancestries[0],
        "Hair Color": hair_colors[0], "Hair Style": hair_styles[0], "Hair Texture": hair_textures[0],
        "Eye Color": eye_colors[0], "Eye Shape": eye_shapes[0], "Height": heights[0],
        "Clothing Style": clothing_styles[0], "Expression": expressions[0],
        "Face Shape": face_shapes[0], "Nose Shape": nose_shapes[0], "Lip Shape": lip_shapes[0],
        "Ugliness Level": "Average", "Distinguishing Mark": distinguishing_marks[0],
        "Description": "", "Background": "", "Story": "", "StoryHooks": "", "Equipment": "",
        "Attributes": {
            "Intelligence": 1, "Wits": 1, "Resolve": 1,
            "Strength": 1, "Dexterity": 1, "Stamina": 1,
            "Presence": 1, "Manipulation": 1, "Composure": 1
        },
        "Talents": {talent: 0 for talent in ["Alertness", "Athletics", "Brawl", "Empathy", "Expression", "Intimidation", "Persuasion", "Streetwise", "Subterfuge"]},
        "Skills": {skill: 0 for skill in ["Animal Ken", "Crafts", "Drive", "Etiquette", "Firearms", "Melee", "Performance", "Stealth", "Survival"]},
        "Knowledges": {knowledge: 0 for knowledge in ["Academics", "Computer", "Investigation", "Law", "Linguistics", "Medicine", "Occult", "Politics", "Science"]},
        "Spheres": {sphere: 0 for sphere in all_spheres},
        "Advantages": {
            "Willpower": 5, "Merit": merits[0], "Flaw": flaws[0]
        },
        "Backgrounds": {bg: 0 for bg in ["Resources", "Allies", "Contacts", "Fame", "Mentor", "Retainer", "Safehouse", "Status"]},
        "Other Traits": {"Quirks": quirks[0]},
        # Puntos para gastar en modo manual
        "Points": {
            "Attributes": {"Mental": 7, "Physical": 5, "Social": 3}, # Prioridades a elegir
            "Abilities": {"Talents": 13, "Skills": 9, "Knowledges": 5}, # Prioridades a elegir
            "Backgrounds": 5,
            "Spheres": 5,
            "Freebies": 15
        }
    }

def display_character_builder_ui():
    """Muestra la interfaz para construir el personaje manualmente."""
    st.info("Modo de Construcción Manual: Asigna los puntos según las reglas de Mago: La Ascensión.")

    char = st.session_state.character_sheet

    tab_concept, tab_attrs, tab_abil, tab_adv, tab_finish = st.tabs([
        "Concepto", "Atributos", "Habilidades", "Ventajas", "Finalizar"
    ])

    with tab_concept:
        st.header("Identidad y Concepto")
        char["Name"] = st.text_input("Nombre del Personaje", value=char["Name"])
        c1, c2 = st.columns(2)
        with c1:
            char["Nature"] = st.selectbox("Naturaleza", natures, index=natures.index(char["Nature"]))
            char["Demeanor"] = st.selectbox("Conducta", demeanors, index=demeanors.index(char["Demeanor"]))
            char["Affiliation"] = st.selectbox("Afiliación", list(affiliation_spheres.keys()) + ["Hollow Ones"], index=0)
        with c2:
            char["Essence"] = st.selectbox("Esencia", essences, index=essences.index(char["Essence"]))
            char["Concept"] = st.selectbox("Concepto", concepts, index=concepts.index(char["Concept"]))
            char["Sect"] = st.selectbox("Secta", sects, index=sects.index(char["Sect"]))

    with tab_attrs:
        st.header("Atributos (7/5/3)")
        st.warning("Esta sección es un prototipo. La lógica completa de puntos (7/5/3) requiere una implementación más compleja con callbacks, pero aquí puedes ajustar los valores base.")
        # Aquí iría la lógica para asignar prioridades y gastar puntos.
        # Por ahora, sliders simples para demostrar la idea.
        for attr in char["Attributes"]:
            char["Attributes"][attr] = st.slider(f"{attr}", 1, 5, char["Attributes"][attr])

    with tab_abil:
        st.header("Habilidades (13/9/5)")
        st.warning("Prototipo: Ajusta los valores base. La lógica de puntos completa se añadiría aquí.")
        st.subheader("Talentos")
        for talent in char["Talents"]:
            char["Talents"][talent] = st.slider(f"{talent}", 0, 3, char["Talents"][talent])
        # ... Repetir para Skills y Knowledges

    with tab_adv:
        st.header("Ventajas")
        st.warning("Prototipo: Ajusta los valores base.")
        st.subheader("Trasfondos (5 puntos)")
        for bg in char["Backgrounds"]:
            char["Backgrounds"][bg] = st.slider(f"{bg}", 0, 5, char["Backgrounds"][bg], key=f"build_{bg}")
        st.subheader("Esferas")
        # ... Lógica para esferas

    with tab_finish:
        st.header("Finalizar y Generar Historia")
        st.write("Una vez que estés satisfecho con tu personaje, puedes generar su historia y ganchos de aventura.")
        if st.button("Completar Personaje y Generar Narrativa"):
            with st.spinner('Forjando el destino del personaje...'):
                # Para el modo manual, podemos usar la IA por defecto o añadir otra opción aquí
                # Por simplicidad, usaremos la IA para el modo manual.
                st.session_state.character_sheet['Story'] = generate_story_template(st.session_state.character_sheet)
                st.session_state.character_sheet['StoryHooks'] = generate_story_hooks(st.session_state.character_sheet)
                st.session_state.mode = "display" # Cambiar a modo de visualización
                st.rerun()

def display_final_character_sheet(character_sheet):
    """Muestra la hoja de personaje final de forma profesional y organizada."""
    
    st.header(f"Character Sheet: {character_sheet['Name']}")
    st.caption(f"*{character_sheet['Concept']}*")
    st.divider()

    # --- Pestañas para organizar la información (con la nueva pestaña Portrait) ---
    tab_overview, tab_stats, tab_magic, tab_identity, tab_portrait = st.tabs([
        "✨ Overview & Story", "📊 Core Stats", "🔮 Magic & Merits", "👤 Identity & Appearance", "🖼️ Portrait"
    ])

    with tab_overview:
        # Mostrar la imagen generada si existe, justo al principio de la pestaña de historia.
        if st.session_state.get("generated_image"):
            # Usar columnas para centrar la imagen
            _, col_img, _ = st.columns([1, 2, 1])
            with col_img:
                st.image(st.session_state.generated_image, caption="Character Portrait", use_column_width=True)
            st.divider()

        st.subheader("Character Story")
        st.markdown(character_sheet['Story'])
        
        with st.expander("Storyteller's Notes (Adventure Hooks)"):
            st.markdown(character_sheet.get('StoryHooks', 'No hooks generated.'))
    with tab_stats:
        st.subheader("Attributes")
        attr_cols = st.columns(3)
        attr_groups = [("Mental", ["Intelligence", "Wits", "Resolve"]), 
                       ("Physical", ["Strength", "Dexterity", "Stamina"]), 
                       ("Social", ["Presence", "Manipulation", "Composure"])]
        for i, (cat, attrs) in enumerate(attr_groups):
            with attr_cols[i]:
                with st.container(border=True):
                    st.markdown(f"**{cat}**")
                    for attr in attrs:
                        st.write(f"{attr}: {character_sheet['Attributes'][attr]}")

        st.subheader("Abilities")
        abil_cols = st.columns(3)
        abil_groups = [("Talents", character_sheet['Talents']), 
                       ("Skills", character_sheet['Skills']), 
                       ("Knowledges", character_sheet['Knowledges'])]
        for i, (cat, abils) in enumerate(abil_groups):
            with abil_cols[i]:
                with st.container(border=True):
                    st.markdown(f"**{cat}**")
                    for abil, value in abils.items():
                        st.write(f"{abil}: {value}")
    with tab_magic:
        col1, col2 = st.columns(2)
        with col1:
            with st.container(border=True):
                st.subheader("Spheres")
                for sphere, value in character_sheet['Spheres'].items():
                    st.write(f"{sphere}: {value}")
        with col2:
            with st.container(border=True):
                st.subheader("Core Advantages")
                st.write(f"**Willpower:** {character_sheet['Advantages']['Willpower']}")
                st.write(f"**Morality:** {character_sheet['Morality']}")
                st.write(f"**Paradigm:** {character_sheet['Paradigm']}")
            
            with st.container(border=True):
                st.subheader("Merits & Flaws")
                st.write(f"**Merit:** {character_sheet['Advantages']['Merit']}")
                st.write(f"**Flaw:** {character_sheet['Advantages']['Flaw']}")

        with st.container(border=True):
            st.subheader("Backgrounds")
            bg_cols = st.columns(3)
            bg_items = list(character_sheet['Backgrounds'].items())
            for i, (bg, value) in enumerate(bg_items):
                with bg_cols[i % 3]:
                    st.write(f"{bg}: {value}")
    with tab_identity:
        st.subheader("Core Identity")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Nature", character_sheet['Nature'])
        with col2:
            st.metric("Demeanor", character_sheet['Demeanor'])
        with col3:
            st.metric("Essence", character_sheet['Essence'])

        with st.container(border=True):
            c1, c2 = st.columns(2)
            c1.write(f"**Affiliation:** {character_sheet['Affiliation']}")
            c2.write(f"**Sect:** {character_sheet['Sect']}")

        st.subheader("Psychological Profile")
        with st.container(border=True):
            c1, c2 = st.columns(2)
            c1.write(f"**Goal:** {character_sheet['Goal']}")
            c2.write(f"**Secret:** {character_sheet['Secret']}")
            c1.write(f"**Phobia:** {character_sheet['Phobia']}")
            c2.write(f"**Cherished Possession:** {character_sheet['Cherished Possession']}")

        st.subheader("Physical Appearance")
        with st.container(border=True):
            c1, c2, c3 = st.columns(3)
            c1.write(f"**Age:** {character_sheet['Age']}")
            c2.write(f"**Sex:** {character_sheet['Sex']}")
            c3.write(f"**Ancestry:** {character_sheet['Ancestry']}")
            
            st.write(f"**Build:** {character_sheet['Height']}, with a {character_sheet['Body Type']} complexion.")
            st.write(f"**Appearance:** {character_sheet['Ugliness Level']}.")
            st.write(f"**Skin:** {character_sheet['Skin Tone']}")
            st.write(f"**Hair:** {character_sheet['Hair Style']}, {character_sheet['Hair Texture']}, and {character_sheet['Hair Color']} color.")
            st.write(f"**Face:** A {character_sheet['Face Shape']} face with {character_sheet['Lip Shape']} lips and a {character_sheet['Nose Shape']} nose.")
            st.write(f"**Eyes:** {character_sheet['Eye Color']} and {character_sheet['Eye Shape']}.")
            st.write(f"**Attitude:** They have {character_sheet['Expression'].lower()}.")
            st.write(f"**Style:** Their clothing style is {character_sheet['Clothing Style'].lower()}.")
            st.divider()
            st.write(f"**Distinguishing Mark:** {character_sheet['Distinguishing Mark']}")
            st.write(f"**Quirk:** {character_sheet['Other Traits']['Quirks']}")
    
    with tab_portrait:
        generate_and_display_portrait_ui(character_sheet)

def generate_prompt_for_image(character_sheet, image_type="Portrait"):
    """Construye un prompt detallado para la generación de imágenes."""
    prompt_parts = []

    # 1. Tipo de toma y sujeto principal
    base_subject = f"a {character_sheet['Sex']} of {character_sheet['Ancestry']} descent, appearing as a {character_sheet['Age']}"
    if image_type == "Portrait":
        prompt_parts.append(f"Close-up portrait of {base_subject}")
    elif image_type == "Full Body (Front View)":
        prompt_parts.append(f"Full body character concept of {base_subject}, front view, standing pose")
    elif image_type == "Full Body (Back View)":
        prompt_parts.append(f"Full body character concept of {base_subject}, view from behind")
    elif image_type == "Full Body (Side View)":
        prompt_parts.append(f"Full body character concept of {base_subject}, side profile view, standing pose")

    # 2. Apariencia General y Corporal
    ugliness_level = character_sheet['Ugliness Level'].lower()
    prompt_parts.append(f"They are {character_sheet['Height']}. Their build is {character_sheet['Body Type']}. They have a {ugliness_level} appearance.")
    
    # Refuerzo para apariencias no atractivas
    unattractive_terms = ["repulsive", "hideous", "grotesque", "ugly", "unpleasant", "plain", "homely", "unattractive", "harsh-featured"]
    if any(term in ugliness_level for term in unattractive_terms):
        prompt_parts.append("unattractive, plain features, unconventional looking.")

    prompt_parts.append(f"Their skin tone is {character_sheet['Skin Tone']}.")

    # 3. Rasgos Faciales, Expresión y Marca Distintiva (¡IMPORTANTE!)
    prompt_parts.append(f"Their face is {character_sheet['Face Shape'].lower()} with {character_sheet['Eye Color'].lower()} {character_sheet['Eye Shape'].lower()} eyes, a {character_sheet['Nose Shape'].lower()} nose, and {character_sheet['Lip Shape'].lower()} lips.")
    prompt_parts.append(f"Their typical expression is one of {character_sheet['Expression'].lower()}.")
    prompt_parts.append(f"A highly detailed, prominent feature is: {character_sheet['Distinguishing Mark']}.")
    prompt_parts.append(f"Their hair is {character_sheet['Hair Style'].lower()}, {character_sheet['Hair Texture'].lower()}, and {character_sheet['Hair Color'].lower()} in color.")

    # 4. Estilo y Atributos
    prompt_parts.append(f"Their clothing style is {character_sheet['Clothing Style'].lower()}.")
    prompt_parts.append("asymmetrical face, realistic skin texture.") # Forzar realismo y evitar la "perfección" de la IA
    if character_sheet['Attributes']['Intelligence'] >= 4:
        prompt_parts.append("Has an intelligent and sharp look.")
    elif character_sheet['Attributes']['Intelligence'] == 1:
        prompt_parts.append("Has a dull, unintelligent, or vacant expression.")

    # 5. Aura y Afiliación
    prompt_parts.append(f"Their demeanor is {character_sheet['Demeanor'].lower()}.")
    
    # AÑADIR ELEMENTOS MÁGICOS SUTILES BASADOS EN LA AFILIACIÓN
    affiliation = character_sheet['Affiliation']
    if affiliation == "Order of Hermes":
        prompt_parts.append("subtle hermetic symbols glow faintly on their clothing or in the air around them.")
    elif affiliation == "Virtual Adepts":
        prompt_parts.append("the air around them seems to glitch slightly, like a digital distortion, data streams faintly visible.")
    elif affiliation in ["Verbena", "Dreamspeakers"]:
        prompt_parts.append("a faint, primal energy, like heat haze, surrounds them, faint scent of herbs and earth.")
    elif affiliation == "Cult of Ecstasy":
        prompt_parts.append("a subtle psychedelic shimmer in the air, eyes hold a universe of experiences.")
    elif affiliation == "Sons of Ether":
        prompt_parts.append("tiny sparks of static electricity crackle around their fingertips, wearing strange goggles.")
    else: # Genérico para otras afiliaciones
        prompt_parts.append("a subtle, almost invisible aura of power shimmers around them.")

    if "Good" in character_sheet['Morality'] or "Benevolent" in character_sheet['Morality']:
        prompt_parts.append("a kind and benevolent aura.")
    elif "Evil" in character_sheet['Morality'] or "Malevolent" in character_sheet['Morality']:
        prompt_parts.append("a sinister and malevolent aura.")
    prompt_parts.append("Style: dark fantasy art, detailed digital painting, character concept art, atmospheric lighting, plain background.")
    
    return ' '.join(prompt_parts)

def generate_and_display_portrait_ui(character_sheet):
    """Muestra la UI para generar y ver el retrato del personaje."""
    st.subheader("Character Portrait")

    # Selección del tipo de imagen
    image_type = st.selectbox(
        "Select Image Type",
        ["Portrait", "Full Body (Front View)", "Full Body (Back View)", "Full Body (Side View)"],
        key="image_type_selector"
    )

    # Construcción del prompt
    default_prompt = generate_prompt_for_image(character_sheet, image_type)
    prompt = st.text_area("Image Generation Prompt", value=default_prompt, height=200)

    if st.button("Generate Portrait", use_container_width=True):
        with st.spinner("Contactando a los oráculos visuales... Esto puede tardar un momento."):
            try:
                # La función ahora puede devolver None si falla
                generated_image = generate_image_with_fallback(prompt) 
                if generated_image:
                    st.session_state.generated_image = generated_image
            except Exception as e:
                st.error(f"No se pudo generar el retrato: {e}")
    
    # Mostrar la imagen si ya ha sido generada y guardada en el estado
    if st.session_state.get("generated_image"):
        st.image(st.session_state.generated_image, caption="Retrato Generado", use_column_width=True)
        # Botón para descargar la imagen generada
        buf = BytesIO()
        st.session_state.generated_image.save(buf, format="PNG")
        st.download_button("Download Portrait", data=buf.getvalue(), file_name="character_portrait.png", mime="image/png", use_container_width=True)
    
def generate_pdf_sheet(character_sheet, image_data=None):
    """Generates a PDF character sheet using reportlab."""
    # Importar componentes de PLATYPUS para maquetación automática
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepInFrame
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
    from reportlab.lib import colors
    from reportlab.lib.units import inch

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=0.75*inch, leftMargin=0.75*inch,
                            topMargin=0.75*inch, bottomMargin=0.75*inch)

    # --- Estilos ---
    styles = getSampleStyleSheet()
    # Modificar estilos existentes o crearlos si no existen, para evitar KeyError.
    styles['Title'].fontName = 'Helvetica-Bold'
    styles['Title'].fontSize = 24
    styles.add(ParagraphStyle(name='Subtitle', parent=styles['h2'], fontName='Helvetica-Oblique', fontSize=14, alignment=TA_LEFT, spaceAfter=12))
    styles.add(ParagraphStyle(name='SectionTitle', parent=styles['h3'], fontName='Helvetica-Bold', fontSize=12, spaceAfter=6, spaceBefore=12))
    styles.add(ParagraphStyle(name='SubSectionTitle', parent=styles['h4'], fontName='Helvetica-Oblique', fontSize=10, spaceAfter=4))
    styles['BodyText'].alignment = TA_JUSTIFY
    styles.add(ParagraphStyle(name='TraitLabel', parent=styles['Normal'], fontSize=9))

    # --- Contenedor de elementos "Flowable" ---
    elements = []

    # --- Helper para crear tablas de rasgos ---
    def create_trait_table(title, traits_dict, max_dots=5):
        sub_elements = [Paragraph(title, styles['SubSectionTitle'])]
        data = []
        for trait, value in traits_dict.items():
            if value > 0: # Solo mostrar rasgos con puntos
                dots = '● ' * value + '○ ' * (max_dots - value)
                data.append([Paragraph(trait, styles['TraitLabel']), Paragraph(dots, styles['TraitLabel'])])
        if not data:
            return [] # No añadir sección si está vacía
        
        tbl = Table(data, colWidths=[1.5*inch, 1.2*inch])
        tbl.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ]))
        sub_elements.append(tbl)
        sub_elements.append(Spacer(1, 0.2*inch))
        return sub_elements

    # --- Cabecera con Imagen ---
    header_content = [
        Paragraph(character_sheet['Name'], styles['Title']),
        Paragraph(f"<i>{character_sheet['Concept']}</i>", styles['Subtitle'])
    ]
    if image_data:
        img_buffer = BytesIO()
        image_data.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        img = Image(img_buffer, width=1.5*inch, height=1.5*inch)
        img.hAlign = 'RIGHT'
        header_table_data = [[header_content, img]]
    else:
        header_table_data = [[header_content, '']]
    
    header_table = Table(header_table_data, colWidths=['*', 1.5*inch])
    header_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    elements.append(header_table)
    elements.append(Spacer(1, 0.2*inch))

    # --- Información Básica ---
    info_items = {
        "Nature": character_sheet['Nature'], "Demeanor": character_sheet['Demeanor'],
        "Essence": character_sheet['Essence'], "Affiliation": character_sheet['Affiliation'],
        "Sect": character_sheet['Sect'], "Paradigm": character_sheet['Paradigm']
    }
    info_data = [[f"<b>{k}:</b> {v}" for k, v in info_items.items()]]
    info_table = Table(info_data, colWidths=[2.5*inch] * 3)
    info_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    #elements.append(info_table) # Esto puede ser muy ancho, mejor una lista
    info_paras = [Paragraph(f"<b>{k}:</b> {v}", styles['Normal']) for k,v in info_items.items()]
    elements.extend(info_paras)
    elements.append(Spacer(1, 0.2*inch))

    # --- Columnas Principales (Atributos, Ventajas, Trackers) ---
    # Columna 1: Atributos y Habilidades
    col1_content = []
    col1_content.append(Paragraph("Attributes", styles['SectionTitle']))
    attr_groups = {
        "Mental": {k: v for k, v in character_sheet['Attributes'].items() if k in ["Intelligence", "Wits", "Resolve"]},
        "Physical": {k: v for k, v in character_sheet['Attributes'].items() if k in ["Strength", "Dexterity", "Stamina"]},
        "Social": {k: v for k, v in character_sheet['Attributes'].items() if k in ["Presence", "Manipulation", "Composure"]}
    }
    for group_name, attrs in attr_groups.items():
        col1_content.extend(create_trait_table(group_name, attrs))

    col1_content.append(Paragraph("Abilities", styles['SectionTitle']))
    col1_content.extend(create_trait_table("Talents", character_sheet['Talents']))
    col1_content.extend(create_trait_table("Skills", character_sheet['Skills']))
    col1_content.extend(create_trait_table("Knowledges", character_sheet['Knowledges']))

    # Columna 2: Ventajas
    col2_content = []
    col2_content.append(Paragraph("Advantages", styles['SectionTitle']))
    col2_content.extend(create_trait_table("Spheres", character_sheet['Spheres']))
    col2_content.extend(create_trait_table("Backgrounds", character_sheet['Backgrounds']))

    # Columna 3: Trackers y otros rasgos
    col3_content = []
    # Health Tracker
    health_data = [[Paragraph("Health", styles['SectionTitle'])]]
    health_levels = ["Bruised (-0)", "Hurt (-1)", "Injured (-1)", "Wounded (-2)", "Mauled (-2)", "Crippled (-5)", "Incapacitated"]
    box = '☐'
    for level in health_levels:
        health_data.append([Paragraph(level, styles['TraitLabel']), box])
    health_table = Table(health_data, colWidths=[1.5*inch, 0.2*inch])
    health_table.setStyle(TableStyle([('SPAN', (0,0), (1,0)), ('ALIGN', (1,1), (1,-1), 'CENTER')]))
    col3_content.append(health_table)
    col3_content.append(Spacer(1, 0.2*inch))

    # Willpower & Paradox
    wp_data = [
        [Paragraph("Willpower", styles['TraitLabel']), '● ' * character_sheet['Advantages']['Willpower'] + '○ ' * (10 - character_sheet['Advantages']['Willpower'])],
        [Paragraph("Paradox", styles['TraitLabel']), '☐ ' * 10]
    ]
    wp_table = Table(wp_data, colWidths=[0.8*inch, '*'])
    col3_content.append(wp_table)
    col3_content.append(Spacer(1, 0.2*inch))

    # Merits & Flaws
    col3_content.append(Paragraph("Merits & Flaws", styles['SectionTitle']))
    col3_content.append(Paragraph(f"<b>Merit:</b> {character_sheet['Advantages']['Merit']}", styles['Normal']))
    col3_content.append(Paragraph(f"<b>Flaw:</b> {character_sheet['Advantages']['Flaw']}", styles['Normal']))
    col3_content.append(Spacer(1, 0.2*inch))

    # Otros Rasgos
    col3_content.append(Paragraph("Other Traits", styles['SectionTitle']))
    col3_content.append(Paragraph(f"<b>Possession:</b> {character_sheet['Cherished Possession']}", styles['Normal']))
    col3_content.append(Paragraph(f"<b>Quirk:</b> {character_sheet['Other Traits']['Quirks']}", styles['Normal']))

    # Ensamblar las 3 columnas en una tabla principal
    # Usamos KeepInFrame para evitar el LayoutError si el contenido es demasiado grande para una página.
    # Esto agrupa el contenido de la tabla y lo mueve a la página siguiente si no cabe.
    main_content_table = Table([[col1_content, col2_content, col3_content]], 
                               colWidths=[2.8*inch, 2.4*inch, 2.3*inch]) # Ajuste de anchos
    main_content_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    
    elements.append(KeepInFrame(0, 0, [main_content_table]))

    # --- Segunda Página: Historia y Notas ---
    elements.append(PageBreak())
    elements.append(Paragraph(f"{character_sheet['Name']} - Story & Notes", styles['Title']))
    elements.append(Spacer(1, 0.2*inch))

    elements.append(Paragraph("Character Story", styles['SectionTitle']))
    story_text = character_sheet['Story'].replace('\n', '<br/>')
    elements.append(Paragraph(story_text, styles['BodyText']))

    elements.append(Paragraph("Story Hooks", styles['SectionTitle']))
    hooks_text = character_sheet.get('StoryHooks', 'No hooks generated.').replace('\n', '<br/>')
    elements.append(Paragraph(hooks_text, styles['BodyText']))

    # --- Construir el PDF ---
    doc.build(elements)
    buffer.seek(0)
    return buffer

def download_html_new(character_sheet, image_data=None):
    """Generates a styled HTML string for character sheet download."""
    def generate_list_items(data_dict):
        return ''.join(f'<li><strong>{key}:</strong> {value}</li>' for key, value in data_dict.items() if value > 0)
    
    story_html = character_sheet["Story"].replace('\n\n', '</p><p>')
    hooks_html = character_sheet.get("StoryHooks", "N/A").replace('\n', '<br>')

    image_html = ""
    if image_data:
        import base64
        buffered = BytesIO()
        image_data.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        image_html = f'<div class="portrait-section"><img src="data:image/png;base64,{img_str}" alt="Character Portrait"></div>'


    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>{character_sheet["Name"]} - Mage Character Sheet</title>
        <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Lato:wght@400;700&display=swap" rel="stylesheet">
        <style>
            body {{ font-family: 'Lato', sans-serif; background-color: #1a1a1a; color: #e0e0e0; margin: 0; padding: 20px; font-size: 14px; line-height: 1.6; }}
            .container {{ max-width: 1200px; margin: auto; background-color: #2b2b2b; border: 1px solid #444; box-shadow: 0 0 15px rgba(0,0,0,0.5); }}
            header {{ text-align: center; padding: 20px; border-bottom: 2px solid #8a2be2; background-color: #1f1f1f; }}
            h1, h2 {{ font-family: 'Cinzel', serif; color: #8a2be2; margin: 0; text-transform: uppercase; letter-spacing: 2px; }}
            h1 {{ font-size: 36px; }}
            h2 {{ font-size: 24px; }}
            h3 {{ font-family: 'Cinzel', serif; color: #c7a2e8; border-bottom: 1px solid #555; padding-bottom: 5px; margin-top: 20px; }}
            .main-content {{ display: flex; flex-wrap: wrap; padding: 20px; }}
            .portrait-section {{ flex-basis: 100%; text-align: center; margin-bottom: 20px; }}
            .portrait-section img {{ max-width: 400px; width: 100%; border: 3px solid #8a2be2; border-radius: 8px; }}
            .column {{ flex: 1; min-width: 350px; padding: 0 15px; }}
            .section {{ background-color: #333; border: 1px solid #444; border-radius: 5px; padding: 15px; margin-bottom: 20px; }}
            ul {{ list-style-type: none; padding: 0; }}
            li {{ padding: 4px 0; border-bottom: 1px solid #404040; }}
            li:last-child {{ border-bottom: none; }}
            strong {{ color: #b39ddb; }}
            .story-section p {{ text-align: justify; margin-top: 0; }}
        </style>
        <style>
            /* Additional styles for trackers */
            .tracker-row {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 8px;
                padding: 4px;
                border-bottom: 1px solid #404040;
            }}
            .tracker-row:last-child {{ border-bottom: none; }}
            .tracker-label {{ font-weight: bold; font-size: 13px; }}
            .tracker-boxes {{ display: flex; gap: 5px; }}
            .box {{
                width: 20px;
                height: 20px;
                border: 1px solid #b39ddb;
                background-color: #222;
            }}
            .inventory-box {{
                min-height: 150px;
                border: 1px dashed #555;
                margin-top: 10px;
                padding: 10px;
                border-radius: 3px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>{character_sheet["Name"]}</h1>
                <h2>{character_sheet["Concept"]}</h2>
            </header>
            {image_html}
            <div class="main-content">
                <div class="column">
                    <div class="section"><h3>Core Identity</h3><ul>
                        <li><strong>Nature:</strong> {character_sheet['Nature']}</li>
                        <li><strong>Demeanor:</strong> {character_sheet['Demeanor']}</li>
                        <li><strong>Essence:</strong> {character_sheet['Essence']}</li>
                        <li><strong>Affiliation:</strong> {character_sheet['Affiliation']} ({character_sheet['Sect']})</li>
                    </ul></div>
                    <div class="section"><h3>Attributes</h3><ul>{generate_list_items(character_sheet['Attributes'])}</ul></div>
                    <div class="section"><h3>Talents</h3><ul>{generate_list_items(character_sheet['Talents'])}</ul></div>
                    <div class="section"><h3>Skills</h3><ul>{generate_list_items(character_sheet['Skills'])}</ul></div>
                    <div class="section"><h3>Knowledges</h3><ul>{generate_list_items(character_sheet['Knowledges'])}</ul></div>
                </div>
                <div class="column">
                    <div class="section">
                        <h3>Trackers</h3>
                        <div class="tracker-row">
                            <span class="tracker-label">Paradox</span>
                            <div class="tracker-boxes">
                                {'<div class="box"></div>' * 10}
                            </div>
                        </div>
                        <div class="tracker-row"><span class="tracker-label">Bruised (-0)</span><div class="box"></div></div>
                        <div class="tracker-row"><span class="tracker-label">Hurt (-1)</span><div class="box"></div></div>
                        <div class="tracker-row"><span class="tracker-label">Injured (-1)</span><div class="box"></div></div>
                        <div class="tracker-row"><span class="tracker-label">Wounded (-2)</span><div class="box"></div></div>
                        <div class="tracker-row"><span class="tracker-label">Mauled (-2)</span><div class="box"></div></div>
                        <div class="tracker-row"><span class="tracker-label">Crippled (-5)</span><div class="box"></div></div>
                        <div class="tracker-row"><span class="tracker-label">Incapacitated</span><div class="box"></div></div>
                    </div>
                    <div class="section"><h3>Advantages</h3><ul>
                        <li><strong>Willpower:</strong> {character_sheet['Advantages']['Willpower']}</li>
                        <li><strong>Paradigm:</strong> {character_sheet['Paradigm']}</li>
                        <li><strong>Merit:</strong> {character_sheet['Advantages']['Merit']}</li>
                        <li><strong>Flaw:</strong> {character_sheet['Advantages']['Flaw']}</li>
                    </ul></div>
                    <div class="section"><h3>Spheres</h3><ul>{generate_list_items(character_sheet['Spheres'])}</ul></div>
                    <div class="section"><h3>Backgrounds</h3><ul>{generate_list_items(character_sheet['Backgrounds'])}</ul></div>
                    <div class="section"><h3>Equipment & Possessions</h3><ul>
                        <li><strong>Cherished Possession:</strong> {character_sheet['Cherished Possession']}</li>
                    </ul><div class="inventory-box"></div></div>
                    <div class="section"><h3>Psychological Profile</h3><ul>
                        <li><strong>Goal:</strong> {character_sheet['Goal']}</li>
                        <li><strong>Secret:</strong> {character_sheet['Secret']}</li>
                        <li><strong>Phobia:</strong> {character_sheet['Phobia']}</li>
                    </ul></div>
                    <div class="section story-section">
                        <h3>Character Story</h3>
                        <p>{story_html}</p>
                    </div>
                    <div class="section story-section">
                        <h3>Story Hooks</h3>
                        <p>{hooks_html}</p>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

# --- Control de modo en la barra lateral ---
mode = st.sidebar.radio("Modo de Creación", ["Seleccionar", "Generación Aleatoria", "Construcción Manual"], index=0, key="creation_mode")

st.sidebar.divider()

if mode == "Seleccionar":
    st.session_state.mode = "selection"
    st.session_state.character_sheet = None
    st.info("Select a creation mode from the sidebar to begin.")

elif mode == "Generación Aleatoria":
    st.sidebar.header("Random Generation")
    if st.sidebar.button("Generate Random Character", use_container_width=True):
        st.session_state.character_sheet = None # Forzar creación desde cero
        st.session_state.generated_image = None # Limpiar imagen al generar nuevo personaje

        with st.spinner("Forjando un nuevo destino..."):
            char_sheet = generate_character()
            # Generar historias después de crear el personaje
            char_sheet['Story'] = generate_story_template(char_sheet) # La historia se regenera
            char_sheet['StoryHooks'] = generate_story_hooks(char_sheet)
            st.session_state.character_sheet = char_sheet
            
            # Generar el retrato dentro del mismo spinner para asegurar que se complete
            with st.spinner("Pintando el retrato del alma... (Esto puede tardar un momento)"):
                prompt = generate_prompt_for_image(char_sheet, "Portrait")
                generated_image = generate_image_with_fallback(prompt)
                st.session_state.generated_image = generated_image

        st.session_state.mode = "display"

elif mode == "Construcción Manual":
    st.session_state.mode = "build"
    st.session_state.generated_image = None # Limpiar imagen al construir nuevo personaje

# --- Lógica de visualización ---
if st.session_state.mode == "build":
    if st.session_state.character_sheet is None or st.sidebar.button("Start Over"):
        st.session_state.character_sheet = initialize_character_build()
    display_character_builder_ui()

elif st.session_state.mode == "display" and st.session_state.character_sheet:
    display_final_character_sheet(st.session_state.character_sheet)

    # --- NUEVA SECCIÓN: REFINAR PERSONAJE ---
    st.sidebar.divider()
    st.sidebar.header("Refine Character")
    st.sidebar.write("Lock the parts you like and re-roll the rest.")

    st.session_state.locks['Concepto'] = st.sidebar.checkbox("Lock Concept & Name", value=st.session_state.locks.get('Concepto', False))
    st.session_state.locks['Apariencia'] = st.sidebar.checkbox("Lock Appearance", value=st.session_state.locks.get('Apariencia', False))
    st.session_state.locks['Atributos'] = st.sidebar.checkbox("Lock Attributes", value=st.session_state.locks.get('Atributos', False))
    st.session_state.locks['Habilidades'] = st.sidebar.checkbox("Lock Abilities", value=st.session_state.locks.get('Habilidades', False))
    st.session_state.locks['Magia'] = st.sidebar.checkbox("Lock Magic (Spheres)", value=st.session_state.locks.get('Magia', False))
    st.session_state.locks['Ventajas'] = st.sidebar.checkbox("Lock Advantages (Backgrounds)", value=st.session_state.locks.get('Ventajas', False))
    st.session_state.locks['Perfil'] = st.sidebar.checkbox("Lock Profile (Goals, Secrets, etc.)", value=st.session_state.locks.get('Perfil', False))

    if st.sidebar.button("Refine Character", use_container_width=True):
        with st.spinner("Refinando el destino..."):
            # La función generate_character ahora leerá los locks del session_state
            char_sheet = generate_character()
            # Regenerar historia y ganchos para que coincidan con los nuevos rasgos
            char_sheet['Story'] = generate_story_template(char_sheet)
            char_sheet['StoryHooks'] = generate_story_hooks(char_sheet)
            st.session_state.character_sheet = char_sheet
            st.session_state.generated_image = None # Limpiar imagen para incentivar una nueva generación
        st.rerun()

    # --- Botón de Descarga ---
    st.sidebar.divider()
    st.sidebar.header("Download Sheet")

    # --- Descarga HTML ---
    html_content = download_html_new(st.session_state.character_sheet, st.session_state.get("generated_image"))
    st.sidebar.download_button(
        label="Download as HTML",
        data=html_content,
        file_name=f"{st.session_state.character_sheet['Name'].replace(' ', '_')}_sheet.html",
        mime="text/html",
    )

    # --- Descarga PDF ---
    pdf_buffer = generate_pdf_sheet(st.session_state.character_sheet, st.session_state.get("generated_image"))
    st.sidebar.download_button(
        label="Download as PDF",
        data=pdf_buffer,
        file_name=f"{st.session_state.character_sheet['Name'].replace(' ', '_')}_sheet.pdf",
        mime="application/pdf",
    )