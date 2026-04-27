# coding: utf-8
"""
config_loader.py — Carga y acceso al db.json compartido.

Lee el archivo db.json ubicado en ../cartadedespacho.app/db.json
relativo a la raíz de maildedespacho.app.

Estructura esperada del db.json:
  {
    "ramos":                  ["AUTOS", "GMM", ...],
    "aseguradoras":           ["RIMAC SEGUROS...", "MAPFRE...", ...],
    "nomenclatura_comprobantes": {
        "RIMAC SEGUROS...": "LIQUIDACION",
        "MAPFRE...":        "SUPLEMENTO",
        ...
    }
  }

Uso:
    from config_loader import ConfigLoader
    cfg = ConfigLoader()
    ramos        = cfg.ramos()
    aseguradoras = cfg.aseguradoras()
    label_endoso = cfg.label_endoso("MAPFRE PERU")   # → "SUPLEMENTO"
"""

import json
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Ruta al db.json relativa a este archivo:
# maildedespacho.app/config_loader.py → ../cartadedespacho.app/db.json
_DB_PATH = Path(__file__).parent.parent / "cartadedespacho.app" / "db.json"

# Fallbacks por si el db.json no tiene la clave o no se puede leer
_FALLBACK_RAMOS = [
    "ACCIDENTES PERSONALES", "AUTOS", "DAÑOS", "GMM",
    "INCENDIO", "RC", "TRANSPORTES", "VIDA",
]
_FALLBACK_ASEGURADORAS = [
    "AXA SEGUROS", "CHUBB", "GNP", "HDI SEGUROS",
    "MAPFRE", "QUALITAS", "RIMAC SEGUROS Y REASEGUROS",
    "SURA", "ZURICH",
]
# Label por defecto para el campo de número de endoso
_DEFAULT_LABEL_ENDOSO = "Nro. de Endoso"


class ConfigLoader:
    """
    Carga única del db.json al instanciarse.
    Provee acceso tipado a las secciones relevantes para maildedespacho.

    Uso recomendado: instanciar una vez en main.py y pasar la instancia
    a los widgets que la necesiten.

        cfg = ConfigLoader()
        cfg.ramos()           → lista de strings
        cfg.aseguradoras()    → lista de strings
        cfg.label_endoso(cia) → string con el label correcto
    """

    def __init__(self, db_path: Optional[Path] = None) -> None:
        self._path = db_path or _DB_PATH
        self._data: dict = {}
        self._loaded = False
        self._load()

    # ── Carga ──────────────────────────────────────────────────────────────────

    def _load(self) -> None:
        """
        Intenta leer y parsear el db.json.
        Si falla, registra el error y usa los valores fallback.
        No lanza excepciones — la app arranca igual con datos por defecto.
        """
        try:
            if not self._path.exists():
                logger.warning(
                    "db.json no encontrado en: %s — usando valores por defecto.",
                    self._path
                )
                return
            raw = self._path.read_text(encoding="utf-8")
            self._data = json.loads(raw)
            self._loaded = True
            logger.info("db.json cargado correctamente desde: %s", self._path)
        except json.JSONDecodeError as e:
            logger.error("db.json tiene formato inválido: %s — usando fallback.", e)
        except OSError as e:
            logger.error("No se pudo leer db.json: %s — usando fallback.", e)

    def reload(self) -> None:
        """
        Recarga el db.json desde disco.
        Útil si la otra app modificó el archivo mientras esta estaba abierta.
        """
        self._data = {}
        self._loaded = False
        self._load()

    # ── Accessors ──────────────────────────────────────────────────────────────

    def is_loaded(self) -> bool:
        """True si el db.json se leyó correctamente."""
        return self._loaded

    def db_path(self) -> Path:
        """Ruta al db.json que se intentó cargar."""
        return self._path

    def ramos(self) -> list[str]:
        """
        Lista de ramos disponibles para el QComboBox de Ramo.
        Retorna los datos del db.json o el fallback si no están disponibles.
        Ordenados alfabéticamente.
        """
        raw = self._data.get("ramos", _FALLBACK_RAMOS)
        return sorted(str(r).strip() for r in raw if r)

    def aseguradoras(self) -> list[str]:
        """
        Lista de aseguradoras para el QComboBox de CIA.
        Retorna los datos del db.json o el fallback si no están disponibles.
        Ordenadas alfabéticamente.
        """
        raw = self._data.get("aseguradoras", _FALLBACK_ASEGURADORAS)
        return sorted(str(a).strip() for a in raw if a)

    def nomenclatura_comprobantes(self) -> dict[str, str]:
        """
        Diccionario completo de nomenclaturas por aseguradora.
        Ej: {"RIMAC SEGUROS Y REASEGUROS": "LIQUIDACION", ...}
        """
        return self._data.get("nomenclatura_comprobantes", {})

    def label_endoso(self, aseguradora: str) -> str:
        """
        Retorna el label correcto para el campo de número de endoso
        según la aseguradora seleccionada.

        Busca la aseguradora en nomenclatura_comprobantes del db.json.
        Si no hay match exacto, intenta match case-insensitive.
        Si no encuentra nada, retorna el label por defecto.

        Args:
            aseguradora: Nombre de la aseguradora tal como viene del QComboBox.

        Returns:
            String con el label, ej. "Nro. de Suplemento", "Nro. de Liquidación"
            o "Nro. de Endoso" por defecto.

        Ejemplos:
            label_endoso("RIMAC SEGUROS Y REASEGUROS") → "Nro. de Liquidación"
            label_endoso("MAPFRE")                     → "Nro. de Suplemento"
            label_endoso("AXA SEGUROS")                → "Nro. de Endoso"
        """
        if not aseguradora:
            return _DEFAULT_LABEL_ENDOSO

        nomenclatura = self.nomenclatura_comprobantes()

        # Match exacto primero
        raw_label = nomenclatura.get(aseguradora)

        # Fallback: match case-insensitive
        if raw_label is None:
            aseg_upper = aseguradora.upper()
            for key, val in nomenclatura.items():
                if key.upper() == aseg_upper:
                    raw_label = val
                    break

        if raw_label is None:
            return _DEFAULT_LABEL_ENDOSO

        # Capitalizar para presentación: "LIQUIDACION" → "Nro. de Liquidación"
        label_capitalizado = raw_label.strip().capitalize()
        return f"Nro. de {label_capitalizado}"

    def label_endoso_short(self, aseguradora: str) -> str:
        """
        Versión corta del label de endoso para espacios reducidos.
        Ej: "Suplemento", "Liquidación", "Endoso"
        """
        full = self.label_endoso(aseguradora)
        # Quitar el prefijo "Nro. de "
        return full.replace("Nro. de ", "")


# =============================================================================
# CLIPBOARD PASTE — parseo del portapapeles
# =============================================================================

# Claves esperadas en el JSON del portapapeles (enviado por cartadedespacho)
_CLIPBOARD_REQUIRED_KEYS = {"contratante"}
_CLIPBOARD_OPTIONAL_KEYS = {
    "contacto", "aseguradora", "ramo",
    "nro_poliza", "vigencia_inicio", "vigencia_fin",
}
_ALL_CLIPBOARD_KEYS = _CLIPBOARD_REQUIRED_KEYS | _CLIPBOARD_OPTIONAL_KEYS


def parse_clipboard_data(text: str) -> tuple[bool, dict, str]:
    """
    Intenta parsear el texto del portapapeles como JSON de despacho.

    El formato esperado es el producido por el botón "Copiar para despacho"
    de cartadedespacho.app. Ver documento INTEGRACION_PORTAPAPELES.md
    para la especificación completa.

    Args:
        text: Texto crudo del portapapeles (QApplication.clipboard().text())

    Returns:
        Tuple (ok, datos, mensaje_error):
          ok            → True si el parseo fue exitoso
          datos         → dict con los datos (vacío si ok=False)
          mensaje_error → string con descripción del error (vacío si ok=True)

    Formato esperado del JSON:
        {
            "_tipo": "despacho_digital_v1",
            "contratante": "...",
            "contacto": "...",
            "aseguradora": "...",
            "ramo": "...",
            "nro_poliza": "...",
            "vigencia_inicio": "2024",
            "vigencia_fin": "2025"
        }
    """
    if not text or not text.strip():
        return False, {}, "El portapapeles está vacío."

    text = text.strip()

    # Verificar que parece JSON
    if not text.startswith("{"):
        return False, {}, (
            "El contenido del portapapeles no es un formato reconocido.\n"
            "Usa el botón 'Copiar para despacho' en CartaDeDespacho."
        )

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return False, {}, (
            "El contenido del portapapeles tiene formato inválido.\n"
            "Usa el botón 'Copiar para despacho' en CartaDeDespacho."
        )

    # Verificar firma del tipo
    tipo = data.get("_tipo", "")
    if tipo != "despacho_digital_v1":
        # No es error fatal — puede ser de una versión anterior. Solo advertir.
        logger.warning(
            "Portapapeles sin _tipo esperado. Encontrado: '%s'. Intentando de todas formas.", tipo
        )

    # Verificar claves requeridas
    missing = _CLIPBOARD_REQUIRED_KEYS - set(data.keys())
    if missing:
        return False, {}, (
            f"El contenido del portapapeles no tiene los campos requeridos: "
            f"{', '.join(sorted(missing))}.\n"
            "Usa el botón 'Copiar para despacho' en CartaDeDespacho."
        )

    # Extraer solo las claves conocidas (ignorar basura extra)
    result = {k: str(data[k]).strip() for k in _ALL_CLIPBOARD_KEYS if k in data}

    if not result.get("contratante"):
        return False, {}, "El campo 'contratante' está vacío en el portapapeles."

    return True, result, ""
