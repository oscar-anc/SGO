# INTEGRACION_PORTAPAPELES.md

## Integración de portapapeles entre CartaDeDespacho y MailDeDespacho

**Documento destinado a:** Claude Sonnet 4.6 implementando el botón
"Copiar para despacho" en la aplicación `cartadedespacho.app`.

---

## Contexto

Existen dos aplicaciones dentro de la carpeta `SGO/`:

```
SGO/
├── cartadedespacho.app/   ← app existente (agrega el botón aquí)
│   └── db.json
└── maildedespacho.app/    ← app nueva (ya implementada, lee el portapapeles)
    └── config_loader.py   ← parse_clipboard_data() ya implementada
```

El flujo es:

1. El usuario está en `cartadedespacho.app` y tiene un cliente/póliza seleccionado.
2. Hace clic en **"Copiar para despacho"** → la app copia un JSON al portapapeles.
3. El usuario cambia a `maildedespacho.app` y hace clic en **"Pegar datos"**.
4. `maildedespacho` parsea el JSON y pre-llena los campos del formulario.

---

## Especificación del JSON a copiar

### Estructura exacta requerida

```json
{
    "_tipo": "despacho_digital_v1",
    "contratante": "EMPRESA CONSTRUCTORA SAC",
    "contacto": "Juan Pérez García",
    "aseguradora": "RIMAC SEGUROS Y REASEGUROS",
    "ramo": "AUTOS",
    "nro_poliza": "001-2024-00123",
    "vigencia_inicio": "2024",
    "vigencia_fin": "2025"
}
```

### Descripción de cada campo

| Campo             | Tipo   | Requerido | Descripción |
|-------------------|--------|-----------|-------------|
| `_tipo`           | string | **Sí**    | Firma de versión. Siempre `"despacho_digital_v1"`. No cambiar. |
| `contratante`     | string | **Sí**    | Nombre completo del contratante o asegurado. |
| `contacto`        | string | No        | Nombre de la persona de contacto directo. |
| `aseguradora`     | string | No        | Nombre de la CIA aseguradora. Debe coincidir **exactamente** con un valor de `db.json["aseguradoras"]`. |
| `ramo`            | string | No        | Ramo del seguro. Debe coincidir **exactamente** con un valor de `db.json["ramos"]`. |
| `nro_poliza`      | string | No        | Número de póliza completo. |
| `vigencia_inicio` | string | No        | Año de inicio de vigencia. Solo el año: `"2024"`. |
| `vigencia_fin`    | string | No        | Año de fin de vigencia. Solo el año: `"2025"`. |

### Reglas críticas

1. **`_tipo` es obligatorio y fijo.** El valor debe ser exactamente `"despacho_digital_v1"`.
   `maildedespacho` lo usa para validar que el contenido proviene de la fuente correcta.

2. **Los valores de `aseguradora` y `ramo` deben coincidir exactamente** con las cadenas
   del `db.json` compartido. Si no hay match, el QComboBox correspondiente quedará
   en blanco y se mostrará una advertencia al usuario (no es error fatal).

3. **`vigencia_inicio` y `vigencia_fin` son solo el año** como string de 4 dígitos.
   Ejemplo: `"2024"`, no `"01/01/2024"` ni `2024` (int).

4. **Todos los valores son strings**, incluso los años. No usar int ni null.

5. **No incluir campos adicionales** más allá de los listados. Campos desconocidos
   son ignorados pero podrían confundir en versiones futuras.

---

## Implementación en CartaDeDespacho (PySide6 + Python)

### Código mínimo del botón

Agregar este método a la clase que maneja la póliza/cliente seleccionado:

```python
import json
from PySide6.QtWidgets import QApplication, QPushButton
from PySide6.QtGui import QClipboard


def copiar_para_despacho(self) -> None:
    """
    Copia los datos del cliente/póliza actualmente seleccionado
    al portapapeles en formato JSON para maildedespacho.app.

    Conectar a: btn_copiar_despacho.clicked.connect(self.copiar_para_despacho)
    """
    # ── Construir el dict con los datos actuales ──────────────────────────────
    # Reemplazar cada .text() / .currentText() con el getter real de tu widget.
    datos = {
        "_tipo":           "despacho_digital_v1",
        "contratante":     self.input_contratante.text().strip(),
        "contacto":        self.input_contacto.text().strip(),
        "aseguradora":     self.combo_aseguradora.currentText().strip(),
        "ramo":            self.combo_ramo.currentText().strip(),
        "nro_poliza":      self.input_nro_poliza.text().strip(),
        "vigencia_inicio": self.input_vigencia_ini.text().strip(),   # solo año "2024"
        "vigencia_fin":    self.input_vigencia_fin.text().strip(),   # solo año "2025"
    }

    # ── Validación mínima antes de copiar ─────────────────────────────────────
    if not datos["contratante"]:
        # Mostrar advertencia con el CustomMessageBox de cartadedespacho
        # (adaptar al sistema de diálogos que ya uses en esa app)
        self._mostrar_aviso("No hay contratante seleccionado para copiar.")
        return

    # ── Serializar y copiar al portapapeles ───────────────────────────────────
    json_str = json.dumps(datos, ensure_ascii=False, indent=2)
    clipboard: QClipboard = QApplication.clipboard()
    clipboard.setText(json_str)

    # ── Feedback visual opcional ──────────────────────────────────────────────
    # Puedes cambiar el texto del botón temporalmente como confirmación:
    btn = self.sender()          # el QPushButton que disparó la señal
    if isinstance(btn, QPushButton):
        original_text = btn.text()
        btn.setText("✓ Copiado")
        btn.setEnabled(False)
        # Restaurar después de 1.5 segundos
        from PySide6.QtCore import QTimer
        QTimer.singleShot(1500, lambda: (
            btn.setText(original_text),
            btn.setEnabled(True)
        ))
```

### Agregar el botón al layout existente

```python
from PySide6.QtWidgets import QPushButton

# Dentro del método que construye la UI de la card/sección de póliza:
btn_copiar = QPushButton("Copiar para despacho")
btn_copiar.setObjectName("BtnCopiarDespacho")
btn_copiar.setToolTip("Copia los datos de esta póliza a MailDeDespacho")
btn_copiar.clicked.connect(self.copiar_para_despacho)
# Agregar al layout donde corresponda:
layout_acciones.addWidget(btn_copiar)
```

### Estilo QSS sugerido (agregar al theme.py de CartaDeDespacho)

```python
# En QSSD de cartadedespacho:
'btn_copiar_despacho_bg':     '#e6f1fb',
'btn_copiar_despacho_border': '#0078d4',
'btn_copiar_despacho_text':   '#0078d4',
'btn_copiar_despacho_hover':  '#0078d4',
'btn_copiar_despacho_hover_text': '#FFFFFF',

# En build_qss() de cartadedespacho:
"""
#BtnCopiarDespacho {
    background-color: %(btn_copiar_despacho_bg)s;
    color:            %(btn_copiar_despacho_text)s;
    border:           1px solid %(btn_copiar_despacho_border)s;
    border-radius:    4px;
    padding:          6px 14px;
    font-weight:      bold;
}
#BtnCopiarDespacho:hover {
    background-color: %(btn_copiar_despacho_hover)s;
    color:            %(btn_copiar_despacho_hover_text)s;
}
"""
```

---

## Flujo completo desde el punto de vista del usuario

```
CartaDeDespacho                          MailDeDespacho
─────────────────────────────────────    ─────────────────────────────────
1. Seleccionar cliente/póliza
2. Clic en "Copiar para despacho"   →   portapapeles tiene el JSON
                                         3. Cambiar a la app
                                         4. Seleccionar Línea de negocio
                                         5. Seleccionar tipo de plantilla
                                         6. Seleccionar modo de envío
                                         7. Clic en "Pegar datos"
                                         8. Campos se pre-llenan:
                                            - Contratante ✓
                                            - Contacto ✓
                                            - CIA (si match en db.json) ✓
                                            - Ramo (si match en db.json) ✓
                                            - Nro. Póliza ✓
                                            - Vigencia inicio/fin ✓
                                         9. Revisar, ajustar, abrir Outlook
```

---

## Manejo de errores en MailDeDespacho (ya implementado)

`maildedespacho.app/config_loader.py` → función `parse_clipboard_data(text)`:

- **Portapapeles vacío** → mensaje: "El portapapeles está vacío."
- **No es JSON** → mensaje: "No es un formato reconocido. Usa el botón 'Copiar para despacho'."
- **JSON inválido** → mensaje: "Formato inválido."
- **Falta `contratante`** → mensaje: "Falta el campo contratante."
- **`aseguradora` sin match en db.json** → el combo queda vacío, advertencia suave.
- **`ramo` sin match en db.json** → el combo queda vacío, advertencia suave.

El usuario siempre puede corregir manualmente cualquier campo que no haya coincidido.

---

## Versionado

Si en el futuro se agregan campos al JSON, incrementar `_tipo`:
- `"despacho_digital_v1"` → versión actual
- `"despacho_digital_v2"` → versión futura con campos adicionales

`maildedespacho` acepta `v1` y registra un warning para versiones desconocidas
pero intenta parsear de todas formas.

---

*Documento generado para integración entre CartaDeDespacho y MailDeDespacho — SGO.*
