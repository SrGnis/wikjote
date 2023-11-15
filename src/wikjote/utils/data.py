non_senses = [
    "Información adicional",
    "Locuciones",
    "Etimología",
    "Véase también",
    "Traducciones",
    "Abreviaciones",
    "Derivados",
    "Pronunciación y escritura",
    "Refranes",
    "Conjugacións",
    "Información avanzada",
    "Ejemplos",
]


def is_sense(name: str) -> str:
    if name in non_senses:
        return name
    else:
        return "Senses"
