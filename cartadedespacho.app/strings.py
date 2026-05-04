"""
strings.py
==========
Centralized repository of all user-visible text in the application.

Usage:
    from strings import S

    QPushButton(S['nav_next'])
    CardWidget(S['card_client_data'])
    CustomMessageBox.warning(self, S['msg_warning_title'], S['msg_annex_empty'])

Guidelines:
  - All text shown to the user belongs here.
  - Dynamic content (company name, policy number, executive name, etc.) is NOT here
    — those come from user input and are assembled at runtime.
  - Internal Python error strings from except blocks are NOT here — those are
    technical and only relevant to developers.
  - Keys use snake_case grouped by context prefix.
"""

S = {

    # ── Application window ────────────────────────────────────────────────────
    'app_title':                    'Carta de Despacho',

    # ── Navigation buttons (shared across pages) ──────────────────────────────
    'nav_back':                     'ATRAS',
    'nav_next':                     'SIGUIENTE',
    'nav_generate':                 'GENERAR',
    'nav_generate_docs':            'GENERAR DOCUMENTOS',
    'nav_clear':                    'LIMPIAR',

    # ── Page 1 — Config: Card headers ─────────────────────────────────────────
    'card_client_data':             'DATOS DEL CLIENTE',
    'card_ope':                     'OPE',
    'card_letter_type':             'TIPO DE CARTA',
    'card_lol':                     'IMPORTE LOL',
    'card_output_format':           'FORMATO DE SALIDA',
    'output_word':                  'Word',
    'output_pdf':                   'PDF',
    'output_both':                  'Word + PDF',
    'card_annexes':                 'ANEXOS',

    # ── Page 1 — Config: Form labels ──────────────────────────────────────────
    'label_company_name':           'Nombre de la Empresa/Cliente:',
    'label_address':                'Dirección:',
    'label_contact_name':           'Nombre del Contacto del Cliente:',
    'label_ope_number':             'Número de Carta:',
    'label_ope_barcode':            'Código de Barras:',

    # ── Page 1 — Config: Radio buttons ────────────────────────────────────────
    'letter_type_issue':            'Emisión',
    'letter_type_renewal':          'Renovación',
    'lol_undefined':                'Sin Definir',
    'lol_general':                  'Importe General',
    'lol_fixed':                    'Importe Fijo',
    'lol_multinacional':            'Multinacional',
    'lol_amount_label':             'Monto:',
    'lol_amount_placeholder':       '0.00',

    # ── Page 1 — Config: Annex table ──────────────────────────────────────────
    'btn_add':                      'AGREGAR',
    'btn_update':                   'ACTUALIZAR',
    'btn_delete':                   'ELIMINAR',
    'annex_placeholder':            'Ingrese el contenido del anexo',
    'tree_header_annex_code':       'ANEXO',
    'tree_header_annex_content':    'CONTENIDO',

    # ── Page 1 — Config: Validation messages ──────────────────────────────────
    'msg_warning_title':            'Advertencia',
    'msg_annex_empty':              'Ingrese el contenido del anexo',
    'msg_annex_max':                'Máximo 26 anexos (A-Z)',
    'msg_annex_no_selection':       'Seleccione un anexo de la tabla',

    # ── Page 2 — Unit: Card headers ───────────────────────────────────────────
    'card_segment':                 'SEGMENTO',
    'card_unit':                    'UNIDAD',
    'card_unit_leader':             'LIDER DE UNIDAD',
    'card_executive':               'EJECUTIVO',
    'card_executive_info':          'INFORMACIÓN DEL EJECUTIVO',

    # ── Page 2 — Unit: Segment radio buttons ─────────────────────────────────
    'segment_risk':                 'Risk',
    'segment_corporate':            'Corporate',
    'segment_commercial':           'Commercial',

    # ── Page 2 — Unit: Executive info row labels ──────────────────────────────
    'exec_field_name':              'Nombres:',
    'exec_field_position':          'Puesto:',
    'exec_field_email':             'Correo:',
    'exec_field_mobile':            'Celular:',
    'exec_field_phone':             'Teléfono:',
    'exec_field_empty':             '-',
    'signature_none':               'Sin firma',

    # ── Page 3 — Policies: Card headers ──────────────────────────────────────
    'card_policy_qty':              'CANTIDAD DE PÓLIZAS',
    'card_insured_qty':             'CANTIDAD DE ASEGURADOS',
    'card_policy_data':             'DATOS DE LA PÓLIZA',
    'card_financing':               'FINANCIAMIENTO',
    'card_endorsement':             'CESIONES DE DERECHO',

    # ── Page 3 — Policies: Radio buttons ──────────────────────────────────────
    'policy_qty_single':            'Una Póliza',
    'policy_qty_multiple':          'Varias Pólizas',
    'insured_qty_single':           'Un Asegurado',
    'insured_qty_multiple':         'Varios Asegurados',
    'currency_soles':               'Soles (S/.)',
    'currency_dollars':             'Dólares (US$)',
    'yes':                          'Si',
    'no':                           'No',

    # ── Page 3 — Policies: Policy widget labels ───────────────────────────────
    'policy_label_branch':          'Ramo:',
    'policy_label_number':          'Número:',
    'policy_label_receipt':         'Recibo:',
    'policy_label_premium':         'Prima:',
    'policy_label_premium_total':   'Prima Total:',
    'policy_placeholder_premium':   '0.00',
    'policy_branch_placeholder':    'Buscar ramo...',

    # ── Page 3 — Policies: Policy data card labels ────────────────────────────
    'policy_data_insurer_placeholder': 'Seleccione o escriba...',
    'policy_data_insurer':          'Aseguradora:',
    'policy_data_validity':         'Vigencia:',
    'policy_data_validity_to':      'al',
    'policy_data_currency':         'Moneda:',

    # ── Page 3 — Policies: Insured widget labels ──────────────────────────────
    'insured_label_name':           'Nombre:',

    # ── Page 3 — Policies: Endorsement widget labels ──────────────────────────
    'endorsement_simple':           'Sí (Simple)',
    'endorsement_detailed':         'Sí (Detallado)',
    'endorsement_label_branch':     'Ramo:',
    'endorsement_label_beneficiary':'Beneficiario:',

    # ── Page 3 — Policies: Buttons ────────────────────────────────────────────
    'btn_add_policy':               'AGREGAR PÓLIZA',
    'btn_add_insured':              'AGREGAR ASEGURADO',

    # ── Page 4 — Finance: Card headers ────────────────────────────────────────
    'card_quote_type':              'TIPO DE CUOTA',
    'card_financing_type':          'TIPO DE FINANCIAMIENTO',
    'finance_total_label':          'TOTAL:',

    # ── Page 4 — Finance: Form labels ─────────────────────────────────────────
    'finance_label_receipt':        'Número de Recibo:',
    'finance_label_premium':        'Prima de Cuota:',
    'finance_label_due_date':       'Fecha de Vencimiento:',
    'finance_placeholder_amount':   '0.00',

    # ── Page 4 — Finance: Tree headers ────────────────────────────────────────
    'tree_header_quota':            'Cuota',
    'tree_header_receipt':          'Recibo',
    'tree_header_due_date':         'Vencimiento',
    'tree_header_amount':           'Importe',

    # ── Page 4 — Finance: Radio button labels (dynamic) ───────────────────────
    'finance_individual_case2':     'Individual (por cada póliza)',
    'finance_collective_case2':     'Agrupado (pólizas agrupadas por asegurado)',
    'finance_individual_case4':     'Individual (por cada póliza)',
    'finance_collective_case4':     'Agrupado (todas las pólizas)',

    # ── Page 4 — Finance: Dynamic card title prefixes ─────────────────────────
    'finance_card_policy_prefix':   '{branch}',
    'finance_card_insured_prefix':  '{name}',
    'finance_card_collective':        'FINANCIAMIENTO AGRUPADO',
    'finance_card_collective_prefix': 'COLECTIVO - {name}',
    'finance_card_policy_fallback': 'Póliza',
    'finance_card_insured_fallback':'Asegurado',

    # ── Page 4 — Finance: Buttons ─────────────────────────────────────────────
    'btn_add_quota':                'AGREGAR',
    'btn_update_quota':             'ACTUALIZAR',
    'btn_delete_quota':             'ELIMINAR',

    # ── Page 4 — Finance: Validation messages ─────────────────────────────────
    'msg_quota_no_selection':       'Seleccione una cuota de la tabla.',

    # ── Page 5 — Annex: Card headers ──────────────────────────────────────────
    'card_manual':                  'MANUAL DE PROCEDIMIENTO EN CASO DE SINIESTROS',
    'card_guarantees':              'GARANTÍAS PARTICULARES',

    # ── Page 5 — Annex: Manual checkboxes ────────────────────────────────────

    # Manual procedure items — edit text here as needed
    'manual_item_01':  'Aspectos Generales',
    'manual_item_02':  'Seguro de Todo Riesgo de Incendio y Líneas Aliadas',
    'manual_item_03':  'Equipo Electrónico',
    'manual_item_04':  'Rotura de Maquinaria',
    'manual_item_05':  'Todo Riesgo Equipo Contratista',
    'manual_item_06':  'Todo Riesgo Construcción - CAR',
    'manual_item_07':  'Seguro de Montaje EAR',
    'manual_item_08':  'Robo y/o Asalto',
    'manual_item_09':  'Deshonestidad',
    'manual_item_10':  'Seguro de Responsabilidad Civil',
    'manual_item_11':  'Seguro de Transporte Nacional',
    'manual_item_12':  'Seguro de Importaciones',
    'manual_item_13':  'Seguro de Vehículos',
    'manual_item_obligatorio':     'obligatorio',
    'manual_select_all':            'Seleccionar todos',

    # ── Page 5 — Annex: GuaranteesEditor title (branch is dynamic) ────────────
    'guarantees_editor_title':      'Garantías - {branch}',

    # ── Page 5 — Annex: Labels ────────────────────────────────────────────────
    'guarantees_select_hint':       (
        'Selecciona las pólizas para generar las Garantías Particulares.\n'
        'Si no hay opciones disponibles, el documento se generará únicamente '
        'con la póliza predeterminada.'
    ),
    'editor_paste_hint':            'Al pegar contenido (Ctrl+V), se eliminará su formato original.',

    # ── Page 5 — Annex: Toolbar button tooltips ───────────────────────────────
    'toolbar_bold_tip':             'Negrita (Ctrl+B)',
    'toolbar_italic_tip':           'Cursiva (Ctrl+I)',
    'toolbar_underline_tip':        'Subrayado (Ctrl+U)',
    'toolbar_list_tip':             'Lista bullet (»)',
    'toolbar_clear_tip':            'Quitar formato de lista',

    # ── app.py: Generate flow dialogs ─────────────────────────────────────────
    'dlg_annex_question_title':     'Generación de Documentos',
    'dlg_annex_question_body':      '¿Necesitas generar los anexos obligatorios?',

    'dlg_manual_no_items_title':    'Manual sin ramos seleccionados',
    'dlg_manual_no_items_body':     (
        'No seleccionaste ningún ramo para el Manual.\n\n'
        '¿Deseas generarlo solo con Aspectos Generales (obligatorio)?'
    ),

    'dlg_cancelled_title':          'Cancelado',
    'dlg_cancelled_body':           'Generación de documentos cancelada.',

    'dlg_error_title':              'Error',
    'dlg_error_generate_body':      'Error al generar el documento:\n\n{error}',

    'dlg_partial_title':            'Parcial',
    'dlg_partial_body':             'Se generaron correctamente:\n\n{generated}\n\nErrores:\n{errors}',

    'dlg_success_title':            'Listo',
    'dlg_success_body':             'Se generaron correctamente:\n\n{generated}',

    # ── Generated document bullet list items ──────────────────────────────────
    'doc_item_carta':               '• Carta de Despacho',
    'doc_item_manual':              '• Manual de Procedimiento en Caso de Siniestros',
    'doc_item_manual_skipped':      '• Manual: omitido por el usuario',
    'doc_item_guarantees':          '• Garantías Particulares',
    'doc_item_carta_docx':           '• Carta de Despacho (.docx)',
    'doc_item_carta_pdf':            '• Carta de Despacho (.pdf)',
    'doc_item_carta_both':           '• Carta de Despacho (.docx & .pdf)',
    'dlg_clear_all_title':           'Limpiar todo',
    'dlg_clear_all_body':            '¿Está seguro que desea limpiar todo el formulario?\n\nSe perderán todos los datos ingresados en todas las páginas,\ncomo si acabara de abrir la aplicación.',
    'dlg_clear_page_title':          'Limpiar página',
    'dlg_clear_unit_body':           '¿Está seguro que desea limpiar los datos de esta página?\n\nSe perderán los datos de unidad y ejecutivo seleccionados.',
    'dlg_clear_policies_body':       '¿Está seguro que desea limpiar los datos de esta página?\n\nSe perderán los datos de pólizas, asegurados y financiamiento.',
    'dlg_clear_finance_body':        '¿Está seguro que desea limpiar los datos de esta página?\n\nSe perderán todos los datos de financiamiento ingresados.',
    'dlg_clear_annex_body':          '¿Está seguro que desea limpiar los datos de esta página?\n\nSe perderán las selecciones de Manual, Garantías y Cesiones.',
    'doc_item_cesiones':             '• Cesiones de Derecho',
    'card_cesiones':                 'CESIONES DE DERECHO',
    'cesiones_detalle_col':          'Detalle',
    'cesiones_monto_col':            'Monto Endosado',
    'cesiones_endosatario_col':      'Endosatario',
    'cesiones_add_group':            'Agregar Grupo',
    'cesiones_group_placeholder':    'Nombre de entidad / banco...',
    'cesiones_detalle_placeholder':  'Descripción del bien o derecho endosado...',
    'cesiones_monto_placeholder':    'Monto',
    'cesiones_view_detail':          'Ver detalle completo',
    'trec_equipo_col':               'Equipo',
    'trec_marca_col':                'Marca',
    'trec_modelo_col':               'Modelo',
    'trec_serie_col':                'Serie',
    'trec_placa_col':                'Placa',
    'trec_anio_col':                 'Año',
    'trec_leasing_col':              'Nro. Leasing',
    'trec_suma_col':                 'Suma Asegurada',
    'trec_equipo_ph':                'Descripción del equipo',
    'trec_marca_ph':                 'Marca',
    'trec_modelo_ph':                'Modelo',
    'trec_serie_ph':                 'Serie / N° de serie',
    'trec_placa_ph':                 'Placa / Identificador',
    'trec_anio_ph':                  'Año',
    'trec_leasing_ph':               'N° de contrato',
    'trec_suma_ph':                  'Suma asegurada',
    'trec_endosatario_ph':           'Escribe o selecciona el endosatario...',
    'cesiones_download_template':    'Descargar Plantilla',
    'cesiones_import_excel':         'Importar Excel',
    'cesiones_import_ok':            'Se importaron {n} filas en {g} grupo(s).',
    'cesiones_import_err':           'No se pudo importar el archivo:\n{error}',
    'cesiones_import_val_err':       'Fila {row}: el valor de Suma Asegurada contiene punto como separador de miles.\nUse coma o punto decimal únicamente. Valor: "{val}"',
    'trec_view_detail':              'Ver detalle',
    'endorsement_policy_card_title': '{branch} {numero}',
    'endorsement_records_count':     '({n} registros)',
    'endorsement_groups_count':      '({n} grupos)',
    'cesiones_template_saved':       'Plantilla guardada en:\n{path}',
    'cesiones_template_err':         'No se pudo guardar la plantilla:\n{error}',
    'cesiones_import_success_title': 'Importación exitosa',
    'cesiones_template_title':       'Plantilla descargada',
    'btn_close':                     'CERRAR',
    'insured_no_name':               '(sin nombre)',
    'dlg_cesiones_reduce_title':     'Reducción de configuración',
    'endtable_view_title':            'Ver registros',
    'endtable_edit_title':            'Editar registros',
    'endtable_btn_view':              'Ver',
    'endtable_btn_edit':              'Editar',
    'endtable_btn_import':            'Importar Excel',
    'endtable_add_endorsee':          'Agregar Endosatario',
    'endtable_add_column':            'Agregar Columna',
    'endtable_del_column':            'Eliminar Columna',
    'endtable_col_name_placeholder':  'Nombre de columna...',
    'endtable_endorsee_placeholder':  'Nombre del endosatario...',
    'endtable_count_individual':    '{e} endosatario(s) & {n} fila(s)',
    'endtable_count_rows':            '({n} filas)',
    'endtable_count_zero':            '(0 filas)',
    'endtable_no_col_selected':       'Seleccione una columna para eliminar.',
    'endtable_col_empty_name':        'El nombre de la columna no puede estar vacío.',
    'endtable_import_mismatch_title': 'Columnas diferentes',
    'endtable_import_mismatch_body':  'Las columnas del archivo Excel difieren de las columnas actuales.\n\nColumnas actuales: {current}\nColumnas Excel: {excel}\n\n¿Desea reemplazar o fusionar?',
    'endtable_import_replace':        'Reemplazar',
    'endtable_import_merge':          'Fusionar',
    'endtable_import_cancel':         'Cancelar',
    'endtable_import_ok':             'Se importaron {n} filas en {g} grupo(s).',
    'endtable_import_err':            'No se pudo importar el archivo:\n{error}',
    'endtable_import_val_err':        'Fila {row}: valor numérico inválido en columna "{col}". Valor: "{val}"',
    'endtable_download_template':     'Descargar Plantilla',
    'endtable_template_saved':        'Plantilla guardada en:\n{path}',
    'endtable_template_err':          'No se pudo guardar la plantilla:\n{error}',
    'endtable_endorsee_name_title':   'Endosatario',
    'endtable_reorder_title':         'Confirmar reordenamiento',
    'dlg_detallado_clear_title':      'Cambio de opción',
    'dlg_detallado_clear_body':       'Al cambiar la opción, se perderán todos los registros de Cesiones de Derecho ingresados.\n\n¿Desea continuar?',
    'endtable_dialog_view_title':     'CESIONES DE DERECHO - PÓLIZA {branch}',
    'endtable_dialog_edit_title':     'EDITAR CESIONES DE DERECHO',
    'reduce_intro':             'Ha reducido la cantidad de pólizas o asegurados.',
    'reduce_will_lose':         'Se perderá la siguiente información:',
    'reduce_confirm':           '¿Desea continuar?',
    'reduce_data_policies':     '• Datos de pólizas (ramo, número, prima)',
    'reduce_data_payment':      '• Cuotas de financiamiento',
    'reduce_data_cesiones':     '• Cesiones de Derecho',
    'reduce_data_garantias':    '• Garantías Particulares',
    'placeholder_no_name':         '(Sin nombre)',
    'guarantees_view_title':       'Ver Garantías Particulares',
    'guarantees_edit_title':       'Editar Garantías Particulares',
    'guarantees_empty_hint':       'Sin contenido aún.',
    'endtable_btn_close':          'Cerrar',
    'endtable_btn_save':              'GUARDAR REGISTROS',
    'endtable_btn_cancel':            'CANCELAR',
    'endtable_clear_confirm_title':   'Limpiar Cesiones',
    'endtable_clear_confirm_body':    '¿Está seguro que desea limpiar todos los registros de Cesiones de Derecho de esta página?',
    'endtable_mode_single':         'Agrupado',
    'endtable_mode_by_endorsee':     'Individual',
    'endtable_mode_conflict_title':  'Columnas diferentes',
    'endtable_mode_conflict_body':   'Los grupos tienen columnas diferentes. Al unificar se perderán las columnas adicionales.\n\n¿Desea continuar?',
    'endtable_col_config_placeholder': 'Nombre de columna...',
    'endtable_col_add_tip':          'Agregar columna',
    'endtable_col_remove_tip':       'Eliminar columna seleccionada',
    'endtable_col_rename_tip':       'Actualizar nombre de columna seleccionada',
    'endtable_gear_tip':             'Configurar columnas',
    'endtable_accordion_tip':        'Expandir / Colapsar',


    'dlg_cesiones_reduce_body':      'Al reducir la cantidad de pólizas o asegurados, también se perderán los registros de Cesiones de Derecho que excedan la nueva configuración.\n\nLos datos que excedan la nueva configuración se perderán.\n\n¿Desea continuar?',


    'btn_add_group':                 'AGREGAR GRUPO',
    'btn_import_excel':              'IMPORTAR EXCEL',
    'btn_download_template':         'DESCARGAR PLANTILLA',

    # ── Page 5 — Annex: Global Cesiones buttons ────────────────────────────
    'cesiones_global_import':        'IMPORTAR EXCEL (GLOBAL)',
    'cesiones_global_download':      'DESCARGAR PLANTILLA (GLOBAL)',
    'cesiones_global_import_title':  'Importar Excel Global',
    'cesiones_global_download_title':'Descargar Plantilla Global',
    'cesiones_global_import_ok':     'Se importaron {n} filas en total.',
    'cesiones_global_import_err':    'Error en importación global:\n{error}',
    'cesiones_global_download_ok':   'Plantilla global guardada en:\n{path}',
    'cesiones_global_download_err':  'Error al guardar plantilla global:\n{error}',


    # ── helpers.py: File not found errors ────────────────────────────────────
    'err_template_garantias':       (
        'Archivo template_garantias.docx no encontrado. '
        'Ejecuta node build_template_garantias.js para generarlo.'
    ),
}
