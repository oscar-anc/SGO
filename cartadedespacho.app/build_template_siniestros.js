/**
 * build_template_siniestros.js
 * ============================
 * Generates template_siniestros.docx — Manual de Procedimientos en Caso de Siniestros.
 *
 * Requires: docx, adm-zip
 * Install adm-zip once (dev dependency for this build script only):
 *   npm install adm-zip
 *
 * Run from the project folder:
 *   node build_template_siniestros.js
 *
 * All measurements, styles, numbering, and shape XML extracted directly from
 * MANUAL_DE_PROCEDIMIENTO_EN_CASO_DE_SINIESTRO.docx via python-docx.
 *
 * Jinja2 variables (filled at runtime by helpers.generateManualSiniestros):
 *   {{ companyName }}     — client company name
 *   {{ unitLeader }}      — unit leader full name
 *   {{ leaderMobile }}    — unit leader mobile
 *   {{ leaderEmail }}     — unit leader email
 *   {{ executiveName }}   — executive full name
 *   {{ executiveMobile }} — executive mobile
 *   {{ executiveEmail }}  — executive email
 *   {{ indexItems }}      — list [{number, name, startPage}] for index loop
 *   {{ total_pages }}     — total body pages for "Página X de Y"
 *   {{ show_item_N }}     — True/False flags for optional items 2..13
 *
 * XXXXX in body text = broker/corredor name — replace manually after generation.
 */

'use strict';

const fs = require('fs');

const {
    Document, Packer, Paragraph, TextRun, AlignmentType,
    PageBreak, Header, Footer, ImageRun, Table, TableRow, TableCell,
    PageNumber, NumberFormat, SectionType, WidthType, BorderStyle,
    TabStopType, LeaderType, LineRuleType,
    LevelFormat, TableLayoutType,
} = require('docx');

// ─────────────────────────────────────────────────────────────────────────────
// CONSTANTS — extracted from template XML
// ─────────────────────────────────────────────────────────────────────────────

const FONT       = 'Noto Sans';
const FONT_MARSH = 'Marsh Serif';   // cover title font
const FONT_WING  = 'Wingdings';
const FONT_SYM   = 'Symbol';

// Sizes in half-points (docx internal). pt × 2.
const SZ_11  = 22;   // 11pt — body text
const SZ_8   = 16;   // 8pt  — header
const SZ_10  = 21;   // 10.5pt — footer
const SZ_12  = 24;   // 12pt
const SZ_18  = 36;   // 18pt — index title, section heading
const SZ_32  = 64;   // 32pt — cover title
const SZ_36  = 72;   // 36pt — section start number

// Colors
const WHITE  = 'FFFFFF';
const NAVY   = '000F47';
const BLUE   = '82BAFF';
const BLACK  = '000000';
const AUTO   = 'auto';

// DXA conversions (1 cm = 567 DXA, 1 pt = 20 DXA)
const cm  = (n) => Math.round(n * 567);
const pt  = (n) => Math.round(n * 20);
const EMU = (n) => Math.round(n * 360000);   // cm → EMU

// Page dimensions (Letter)
// Page size in DXA (twips) — docx v9 page.size uses DXA, not EMU
const PAGE_W = 12240;   // 21.59cm = Letter width
const PAGE_H = 15840;   // 27.94cm = Letter height

// ─────────────────────────────────────────────────────────────────────────────
// LOGO LOADER — async, sharp SVG→PNG
// ─────────────────────────────────────────────────────────────────────────────
function getLogoBuffer() {
    // Load logo_sky.png directly — no conversion needed.
    // Falls back gracefully if file not found.
    try { return fs.readFileSync('imgs/logo_sky.png'); } catch (_) { return null; }
}

// ─────────────────────────────────────────────────────────────────────────────
// BACKGROUND SHAPE — injected as raw XML in the first cover paragraph
//
// Exact wp:anchor + wps:wsp XML extracted from template.
// behindDoc="1" ensures it renders behind all text.
// Position: centered relative to page, size = full Letter page in EMU.
// ─────────────────────────────────────────────────────────────────────────────
function makeBackgroundShapeXml() {
    // No inline namespace declarations — document.xml already declares all prefixes
    // at the root <w:document> element. Inline redeclarations cause Word to reject
    // the file with "error trying to open the file".
    // Collapsed to a single line to avoid whitespace issues in XML injection.
    return '<w:drawing>'
        + '<wp:anchor distT="0" distB="0" distL="114300" distR="114300"'
        + ' simplePos="0" relativeHeight="251659264" behindDoc="1"'
        + ' locked="0" layoutInCell="1" allowOverlap="1"'
        + ' wp14:anchorId="32ADB19F" wp14:editId="3EC6DC68">'
        + '<wp:simplePos x="0" y="0"/>'
        + '<wp:positionH relativeFrom="page"><wp:align>center</wp:align></wp:positionH>'
        + '<wp:positionV relativeFrom="page"><wp:align>center</wp:align></wp:positionV>'
        + `<wp:extent cx="${7772400}" cy="${10058400}"/>`
        + '<wp:effectExtent l="0" t="0" r="0" b="0"/>'
        + '<wp:wrapNone/>'
        + '<wp:docPr id="9001" name="Rectangle Background"/>'
        + '<wp:cNvGraphicFramePr/>'
        + '<a:graphic>'
        + '<a:graphicData uri="http://schemas.microsoft.com/office/word/2010/wordprocessingShape">'
        + '<wps:wsp>'
        + '<wps:cNvSpPr/>'
        + '<wps:spPr>'
        + `<a:xfrm><a:off x="0" y="0"/><a:ext cx="${7772400}" cy="${10058400}"/></a:xfrm>`
        + '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
        + `<a:solidFill><a:srgbClr val="${NAVY}"/></a:solidFill>`
        + '<a:ln><a:noFill/></a:ln>'
        + '</wps:spPr>'
        + '<wps:style>'
        + '<a:lnRef idx="2"><a:schemeClr val="accent1"><a:shade val="15000"/></a:schemeClr></a:lnRef>'
        + '<a:fillRef idx="1"><a:schemeClr val="accent1"/></a:fillRef>'
        + '<a:effectRef idx="0"><a:schemeClr val="accent1"/></a:effectRef>'
        + '<a:fontRef idx="minor"><a:schemeClr val="lt1"/></a:fontRef>'
        + '</wps:style>'
        + '<wps:bodyPr rot="0" vert="horz" wrap="square"'
        + ' lIns="91440" tIns="45720" rIns="91440" bIns="45720"'
        + ' anchor="ctr" compatLnSpc="1">'
        + '<a:prstTxWarp prst="textNoShape"><a:avLst/></a:prstTxWarp>'
        + '<a:noAutofit/>'
        + '</wps:bodyPr>'
        + '</wps:wsp>'
        + '</a:graphicData>'
        + '</a:graphic>'
        + '<wp14:sizeRelH relativeFrom="margin"><wp14:pctWidth>0</wp14:pctWidth></wp14:sizeRelH>'
        + '<wp14:sizeRelV relativeFrom="margin"><wp14:pctHeight>0</wp14:pctHeight></wp14:sizeRelV>'
        + '</wp:anchor>'
        + '</w:drawing>';
}

// ─────────────────────────────────────────────────────────────────────────────
// NUMBERING DEFINITIONS
// Exact abstractNum IDs extracted from template numbering.xml:
//   abstractNum 8 → numId 1 → SectionStart  (decimal, 36pt, #82BAFF)
//   abstractNum 2 → numId 2 → TextBody       (» bullet, Noto Sans bold)
//   abstractNum 3 → numId 4 → EmergencyTable (» bullet, Noto Sans bold, smaller indent)
//   abstractNum 0 → numId 8 → ExecData       (Symbol 183 bullet, bold)
//   abstractNum 7 → numId 9 → Sub/SubSub     (level1=Wingdings 252, level2=Wingdings 167)
//   abstractNum 4 → numId 11 → TOC1          (decimal "1.", right dot-leader tab)
// ─────────────────────────────────────────────────────────────────────────────
// Numbering config — inline in Document constructor (docx v9 pattern).
// Each entry defines abstractNumId, reference, and all level definitions.
function bLvl(ilvl, char, font, leftDxa, hangingDxa) {
    return {
        level: ilvl,
        numberFormat: LevelFormat.BULLET,
        text: char,
        alignment: AlignmentType.LEFT,
        style: {
            paragraph: { indent: { left: leftDxa, hanging: hangingDxa } },
            run: { font: font, bold: true },
        },
    };
}

const NUMBERING_CONFIG = [
    // 0 — SectionStart: decimal, 36pt, #82BAFF, page break before
    {
        abstractNumId: 0,
        reference: 'sectionStart',
        levels: [{
            level: 0,
            numberFormat: LevelFormat.DECIMAL,
            text: '%1',
            alignment: AlignmentType.LEFT,
            style: {
                paragraph: { indent: { left: 360, hanging: 360 } },
                run: { bold: true, color: BLUE, size: SZ_36, font: FONT },
            },
        }],
    },
    // 1 — TextBody: » Noto Sans bold, left=227 hanging=227
    {
        abstractNumId: 1,
        reference: 'textBody',
        levels: [
            { level: 0, numberFormat: LevelFormat.BULLET, text: '»',
              alignment: AlignmentType.LEFT,
              style: {
                paragraph: { indent: { left: 227, hanging: 227 } },
                run: { font: FONT, size: SZ_11, bold: true },
              },
            },
            bLvl(1, 'o', 'Courier New', 1440, 360),
            bLvl(2, '',  FONT_WING,     2160, 360),
        ],
    },
    // 2 — EmergencyListTable: » Noto Sans, left=170 hanging=170
    {
        abstractNumId: 2,
        reference: 'emergency',
        levels: [ { level: 0, numberFormat: LevelFormat.BULLET, text: '»',
                    alignment: AlignmentType.LEFT,
                    style: {
                        paragraph: { indent: { left: 170, hanging: 170 } },
                        run: { font: FONT, size: SZ_11, bold: true },
                    },
                  } ],
    },
    // 3 — ExecData: Symbol · (char 183), left=584 hanging=227
    {
        abstractNumId: 3,
        reference: 'execData',
        levels: [ { level: 0, numberFormat: LevelFormat.BULLET, text: '\u00B7',
                    alignment: AlignmentType.LEFT,
                    style: {
                        paragraph: { indent: { left: 984, hanging: 227 } },
                        run: { font: FONT_SYM, size: SZ_11, bold: true },
                    },
                  } ],
    },
    // 4 — Sub/SubSub bullets
    //   level 0: » (unused directly, TextBody owns level 0)
    //   level 1: Wingdings 252, left=1440 hanging=360
    //   level 2: Wingdings 167, left=2160 hanging=360
    {
        abstractNumId: 4,
        reference: 'bullets',
        levels: [
            { level: 0, numberFormat: LevelFormat.BULLET, text: '»',
              alignment: AlignmentType.LEFT,
              style: { paragraph: { indent: { left: 227, hanging: 227 } }, run: { font: FONT, size: SZ_11, bold: true } } },
            { level: 1, numberFormat: LevelFormat.BULLET, text: String.fromCharCode(252),
              alignment: AlignmentType.LEFT,
              style: { paragraph: { indent: { left: 1440, hanging: 360 } }, run: { font: FONT_WING, size: SZ_11, bold: true } } },
            { level: 2, numberFormat: LevelFormat.BULLET, text: String.fromCharCode(167),
              alignment: AlignmentType.LEFT,
              style: { paragraph: { indent: { left: 2160, hanging: 360 } }, run: { font: FONT_WING, size: SZ_11, bold: true } } },
        ],
    },
    // 5 — TOC1: decimal "1.", left=360 hanging=360, number in Noto Sans 11pt
    {
        abstractNumId: 5,
        reference: 'toc1',
        levels: [{
            level: 0,
            numberFormat: LevelFormat.DECIMAL,
            text: '%1.',
            alignment: AlignmentType.LEFT,
            style: {
                paragraph: { indent: { left: 360, hanging: 360 } },
                run: { font: FONT, size: SZ_11 },
            },
        }],
    },
];

// ─────────────────────────────────────────────────────────────────────────────
// RUN HELPERS
// ─────────────────────────────────────────────────────────────────────────────
function r(text, opts = {}) {
    return new TextRun({
        text,
        font:    opts.font  ?? FONT,
        size:    opts.size  ?? SZ_11,
        bold:    opts.bold  ?? false,
        color:   opts.color ?? BLACK,
        allCaps: opts.caps  ?? false,
    });
}
function rW(text, opts = {}) { return r(text, { ...opts, color: WHITE }); }
function rB(text, opts = {}) { return r(text, { ...opts, bold: true }); }
function rWB(text, opts = {}) { return r(text, { ...opts, color: WHITE, bold: true }); }

// ─────────────────────────────────────────────────────────────────────────────
// PARAGRAPH HELPERS
// ─────────────────────────────────────────────────────────────────────────────
const SP_ZERO = { before: 0, after: 0, line: 240, lineRule: LineRuleType.AUTO };

function pEmpty(color = null) {
    // Explicit Noto Sans + 11pt to prevent Word falling back to Times New Roman
    const opts = { font: FONT, size: SZ_11 };
    if (color) opts.color = color;
    return new Paragraph({ children: [new TextRun({ text: '\u00A0', ...opts })], spacing: SP_ZERO });
}

// Plain paragraph — no bullet, no numbering
function p(children, opts = {}) {
    return new Paragraph({
        children: Array.isArray(children) ? children : [r(children, opts)],
        alignment: opts.align ?? AlignmentType.JUSTIFIED,
        spacing:   opts.spacing ?? SP_ZERO,
        indent:    opts.indent ? { left: opts.indent } : undefined,
    });
}

// TextBody bullet paragraph (numId 2, level 0) — » bold, text normal
function pBullet(children) {
    return new Paragraph({
        children: Array.isArray(children) ? children : [r(children)],
        numbering: { reference: 'textBody', level: 0 },
        alignment: AlignmentType.JUSTIFIED,
        spacing:   SP_ZERO,
    });
}

// Sub-Bullets (numId 9/bullets, level 1) — Wingdings 252
function pSubBullet(children) {
    return new Paragraph({
        children:  Array.isArray(children) ? children : [r(children)],
        numbering: { reference: 'bullets', level: 1 },
        alignment: AlignmentType.JUSTIFIED,
        spacing:   SP_ZERO,
    });
}

// Sub-Sub-bullets (numId 9/bullets, level 2) — Wingdings 167
function pSubSubBullet(children) {
    return new Paragraph({
        children:  Array.isArray(children) ? children : [r(children)],
        numbering: { reference: 'bullets', level: 2 },
        alignment: AlignmentType.JUSTIFIED,
        spacing:   SP_ZERO,
    });
}

// Section Start — auto-numbered, 36pt, #82BAFF, page break before, bottom border
function pSectionStart() {
    return new Paragraph({
        children:  [new TextRun({ text: '', font: FONT, size: SZ_36, color: BLUE })],
        numbering: { reference: 'sectionStart', level: 0 },
        spacing:   { before: 0, after: 380, line: 240, lineRule: LineRuleType.AUTO },
        border: {
            bottom: { style: BorderStyle.SINGLE, size: 12, color: BLUE, space: 1 },
        },
        pageBreakBefore: true,
        keepNext: true,
    });
}

// Section Heading — 18pt, bold, #000F47, no spacing
function pHeading(text) {
    return new Paragraph({
        children:  [r(text, { size: SZ_18, bold: true, color: NAVY })],
        spacing:   SP_ZERO,
        outlineLevel: 0,
    });
}

// Title Body — bold, 11pt, black, justified
function pTitleBody(text) {
    return new Paragraph({
        children:  [rB(text)],
        alignment: AlignmentType.JUSTIFIED,
        spacing:   SP_ZERO,
    });
}

// Subtitle Body — bold, 11pt, first line indent 1.26cm
function pSubtitleBody(text) {
    return new Paragraph({
        children:  [rB(text)],
        alignment: AlignmentType.JUSTIFIED,
        spacing:   SP_ZERO,
        indent:    { firstLine: cm(1.26) },
    });
}

// Central+Exec SubTitle — Noto Sans 11pt bold, left=1.26cm hanging=0.63cm
function pCentralTitle(children) {
    return new Paragraph({
        children:  Array.isArray(children) ? children : [new TextRun({ text: children, font: FONT, size: SZ_11, bold: true, color: BLACK })],
        alignment: AlignmentType.JUSTIFIED,
        spacing:   SP_ZERO,
        indent:    { left: cm(1.26) },
    });
}

// Exec Data — Symbol· bullet, label bold + variable normal, Noto Sans 11pt
// left=1.26cm hanging=0.4cm (from numbering), plus extra left from style
function pExecData(label, variable) {
    return new Paragraph({
        children: [
            new TextRun({ text: label + ': ', font: FONT, size: SZ_11, bold: true,  color: BLACK }),
            new TextRun({ text: variable,     font: FONT, size: SZ_11, bold: false, color: BLACK }),
        ],
        numbering: { reference: 'execData', level: 0 },
        alignment: AlignmentType.JUSTIFIED,
        spacing:   SP_ZERO,
    });
}

// Jinja2 control tag paragraph (invisible, minimal size)
function pJinja(tag) {
    return new Paragraph({
        children: [new TextRun({ text: tag, size: 2 })],
        spacing:  { before: 0, after: 0 },
    });
}

// Helper: array of N empty paragraphs
function nbspArr(n) {
    return Array.from({ length: n }, () => pEmpty());
}

// TOC row — numbered decimal, dot-leader right tab at 9350 DXA
function pTocRow(nameVar, pageVar) {
    // Number "1." = Noto Sans 11pt (from numbering run style)
    // Name text and page number = Noto Sans 12pt
    return new Paragraph({
        children: [
            r(nameVar, { size: SZ_12 }),
            new TextRun({ text: '\t', font: FONT, size: SZ_12 }),
            r(pageVar, { size: SZ_12 }),
        ],
        numbering:  { reference: 'toc1', level: 0 },
        tabStops:   [{ type: TabStopType.RIGHT, position: 9350, leader: LeaderType.DOT }],
        spacing:    { before: pt(15), after: 0, line: pt(15), lineRule: LineRuleType.EXACT },
        indent:     { left: 357, hanging: 357 },
    });
}

// ─────────────────────────────────────────────────────────────────────────────
// STANDARD SECTION BUILDERS
// ─────────────────────────────────────────────────────────────────────────────
function closingBullets() {
    return [
        pTitleBody('¿Cuál es el siguiente paso?'),
        pEmpty(),
        pBullet([r('Una vez liquidado el reclamo por parte del ajustador y/o Aseguradora (para casos directos) éstos remitirán a '), rB('{{ brokerName }}'), r(' el convenio de ajuste y/o liquidación, el cual deberá ser firmado y sellado (para los casos con convenio de ajuste) y de ser casos directos, el cliente solo dará su V°B° a la liquidación vía correo, de no encontrarlo conforme, el asegurado podrá enviar sus comentarios correspondientes.')]),
        pEmpty(),
        pBullet([r('Cuando dicho documento se encuentre conforme, firmado y sellado por el cliente, '), rB('{{ brokerName }}'), r(' devolverá dicho convenio al ajustador a fin de que sea remitido a la Cía. Aseguradora conjuntamente con el Informe Final del siniestro.')]),
        pEmpty(),
        pBullet([r('La Cía. de Seguros, de encontrar conforme el certificado de averías y el informe procederá al pago respectivo en un plazo máximo de 30 días siguientes a la firma del Convenio.')]),
        pEmpty(),
        pBullet([r('El asegurado en todo momento tiene la obligación de no hacer abandono de los bienes siniestrados y de sus restos, entregándolos a la Compañía de Seguros, procediendo a su destrucción o compra del salvamento, según sea el acuerdo con la Aseguradora.')]),
        pEmpty(),
        pBullet([r('El asegurado está en la obligación de ceder sus derechos de Subrogación a la Compañía de Seguros por las acciones que tengan que ejecutarse contra terceros como consecuencia del siniestro. Por ningún motivo deben obrar de tal manera que se invalide este derecho.')]),
    ];
}

function transportClosing() {
    return [
        pTitleBody('¿Cuál es el siguiente paso?'),
        pEmpty(),
        pBullet([r('Una vez analizados los documentos completos y enviado al ajustador nombrado, éste remitirá a la Cia. de seguros con copia a '), rB('{{ brokerName }}'), r(' el Informe Final, documento que resume lo actuado para determinar la cobertura del siniestro; así también se emitirá el Convenio de Ajuste, donde se dará conformidad por las partes sobre el monto a ser indemnizado al Asegurado.')]),
        pEmpty(),
        pBullet([r('La Cía. de Seguros, de encontrar conforme el certificado de averías y el informe procederá al pago respectivo en un plazo máximo de 30 días siguientes a la firma del Convenio.')]),
        pEmpty(),
        pBullet([r('El asegurado en todo momento tiene la obligación de no hacer abandono de los bienes siniestrados y de sus restos, entregándolos a la Compañía de Seguros, procediendo a su destrucción o compra del salvamento, según sea el acuerdo con la Aseguradora.')]),
        pEmpty(),
        pBullet([r('El asegurado está en la obligación de ceder sus derechos de Subrogación a la Compañía de Seguros por las acciones que tengan que ejecutarse contra terceros como consecuencia del siniestro. Por ningún motivo deben obrar de tal manera que se invalide este derecho.')]),
    ];
}

function standardDoItems(items) {
    // 1 nbsp BETWEEN bullets — not after the last one
    const result = [];
    items.forEach((t, i) => {
        result.push(pBullet(Array.isArray(t) ? t : [r(t)]));
        if (i < items.length - 1) result.push(pEmpty());
    });
    return result;
}

function standardDocItems(items) {
    return items.map(t => pSubBullet(t));
}

function wrapSection(num, children) {
    return [
        pJinja(`{%p if show_item_${num} %}`),
        ...children,
        pJinja(`{%p endif %}`),
    ];
}

function buildStandardSection(num, title, doItems, docItems, closingNbsp) {
    // closingNbsp = number of nbsp before ¿Cuál es el siguiente paso? (varies by section)
    const closing = nbspArr(closingNbsp ?? 5).concat(closingBullets());
    return wrapSection(num, [
        pSectionStart(),
        pHeading(title),
        pEmpty(),                    // 1 nbsp above ¿Qué debo hacer?
        pTitleBody('¿Qué debo hacer?'),
        pEmpty(),
        ...standardDoItems(doItems),
        pEmpty(),
        pEmpty(),                    // 2 nbsp before ¿Qué documentos?
        pTitleBody('¿Qué documentos debo presentar para que atiendan el siniestro?'),
        pEmpty(),                    // 1 nbsp above Documentación Básica
        pTitleBody('Documentación Básica:'),
        pEmpty(),                    // 1 nbsp below Documentación Básica
        ...standardDocItems(docItems),
        ...closing,
    ]);
}

function buildTransportSection(num, title, doItems, docItems, closingNbsp) {
    const closing = nbspArr(closingNbsp ?? 2).concat(transportClosing());
    return wrapSection(num, [
        pSectionStart(),
        pHeading(title),
        pEmpty(),                    // 1 nbsp above ¿Qué debo hacer?
        pTitleBody('¿Qué debo hacer?'),
        pEmpty(),
        ...standardDoItems(doItems),
        pEmpty(),
        pEmpty(),
        pTitleBody('¿Qué documentos debo presentar para que atiendan el siniestro?'),
        pEmpty(),
        pTitleBody('Documentación Básica:'),
        pEmpty(),
        ...standardDocItems(docItems),
        ...closing,
    ]);
}

// ─────────────────────────────────────────────────────────────────────────────
// EMERGENCY TABLE — Aspectos Generales
// ─────────────────────────────────────────────────────────────────────────────
function buildEmergencyTable() {
    const rows = [
        ['Central de Bomberos',                                    '116', '222-0222'],
        ['Emergencia Policial',                                    '105', '475-2995 / 225-0220'],
        ['Defensa Civil (Lima)',                                   '115', '225-9898'],
        ['Defensa Civil (Callao)',                                  '',    '429-4245'],
        ['Dirección Nacional Contra el Terrorismo - DIRCOTE',      '',    '433-0148'],
        ['Dirección Nacional de Investigación Criminal - DININCRI', '',   '980-121221'],
        ['Unidad de Desactivación de Explosivos - UDEX',           '',    '481-2901'],
        ['Dirección de Prevención de Robo de Vehículos - DIPROVE', '',    '932-456823'],
    ];

    // Borders: only Top/Right/Left/Bottom — no internal borders
    // Total rows = 1 header + 8 data rows = 9
    const TOTAL_ROWS = 1 + rows.length;  // 9
    const TOTAL_COLS = 3;
    const OUTER = { style: BorderStyle.DOUBLE, size: 4, color: BLACK };
    const NONE  = { style: BorderStyle.NONE,   size: 0, color: 'FFFFFF' };

    // Returns border object for a cell at (row, col).
    // Only outer edges of the table get a visible border — all inner edges are NONE.
    function cellBorders(row, col) {
        return {
            top:    row === 0                ? OUTER : NONE,
            bottom: row === TOTAL_ROWS - 1  ? OUTER : NONE,
            left:   col === 0               ? OUTER : NONE,
            right:  col === TOTAL_COLS - 1  ? OUTER : NONE,
        };
    }

    function headerCell(text, align, col) {
        return new TableCell({
            children: [new Paragraph({
                children: [r(text, { bold: true })],
                alignment: align, spacing: SP_ZERO,
            })],
            verticalAlign: 'center',
            borders: cellBorders(0, col),
        });
    }

    function bodyCell(text, align, useList, row, col) {
        const para = useList
            ? new Paragraph({
                children: [r(text, { bold: true })],
                numbering: { reference: 'emergency', level: 0 },
                alignment: align,
                spacing: SP_ZERO,
              })
            : new Paragraph({
                children: [r(text, { bold: true })],
                alignment: align,
                spacing: SP_ZERO,
              });
        return new TableCell({
            children: [para],
            verticalAlign: 'center',
            borders: cellBorders(row, col),
            margins: { top: 100, bottom: 100, left: 100, right: 100 },
        });
    }

    return new Table({
        layout: TableLayoutType.FIXED,
        indent: { size: cm(0.8), type: WidthType.DXA },
        rows: [
            new TableRow({
                children: [
                    headerCell('  Organismo',  AlignmentType.LEFT,   0),
                    headerCell('Emergencia', AlignmentType.CENTER, 1),
                    headerCell('Central',    AlignmentType.CENTER, 2),
                ],
                tableHeader: false,
                height: { value: cm(1.4), rule: 'atLeast' },
            }),
            ...rows.map(([org, em, cen], i) => new TableRow({
                children: [
                    bodyCell(org, AlignmentType.LEFT,   true,  i + 1, 0),
                    bodyCell(em,  AlignmentType.CENTER, false, i + 1, 1),
                    bodyCell(cen, AlignmentType.CENTER, false, i + 1, 2),
                ],
                height: { value: cm(1.4), rule: 'atLeast' },
            })),
        ],
        columnWidths: [cm(6.46), cm(4.61), cm(5.39)],
    });
}

// ─────────────────────────────────────────────────────────────────────────────
// SECTION 1: COVER
// ─────────────────────────────────────────────────────────────────────────────
function buildCoverChildren() {
    const logoBuffer = getLogoBuffer();
    const children   = [];

    // The background shape XML is injected as a raw run in the first paragraph.
    // XmlComponent is not available in docx v9 for raw injection on Paragraph,
    // so we use a workaround: create the first paragraph as a plain paragraph
    // and post-process its XML to insert the drawing run.
    // We track it via a unique marker text that we'll replace later.
    children.push(new Paragraph({
        children: [new TextRun({ text: '__BACKGROUND_SHAPE__', size: 2, color: WHITE })],
        spacing:  SP_ZERO,
    }));

    // Empty lines (2 before logo as per template)
    children.push(pEmpty(WHITE));
    children.push(pEmpty(WHITE));

    // Logo inline image
    if (logoBuffer) {
        children.push(new Paragraph({
            children: [new ImageRun({
                type: 'png',
                data: logoBuffer,
                transformation: {
                    width:  201,   // 5.31cm at 96dpi
                    height:  44,   // 1.16cm at 96dpi
                },
            })],
            alignment: AlignmentType.LEFT,
            spacing:   SP_ZERO,
        }));
    }

    // 6 empty lines after logo
    for (let i = 0; i < 6; i++) children.push(pEmpty(WHITE));

    // Title: "MANUAL DE PROCEDIMIENTO EN CASO DE SINIESTRO"
    // Font: Marsh Serif, 32pt, bold, white, allCaps
    children.push(new Paragraph({
        children: [rWB('Manual de Procedimiento en caso de siniestro', {
            font: FONT_MARSH, size: SZ_32, caps: true,
        })],
        alignment: AlignmentType.LEFT,
        spacing:   SP_ZERO,
    }));

    // 3 empty lines
    for (let i = 0; i < 4; i++) children.push(pEmpty(WHITE));

    // {{companyName}} — Noto Sans, 18pt, white, allCaps
    children.push(new Paragraph({
        children: [rW('{{ companyName }}', { size: SZ_18 })],
        alignment: AlignmentType.LEFT,
        spacing:   SP_ZERO,
    }));

    return children;
}

// ─────────────────────────────────────────────────────────────────────────────
// SECTION 2: INDEX
// ─────────────────────────────────────────────────────────────────────────────
function buildIndexHeader() {
    return new Header({
        children: [new Paragraph({
            children: [r('MANUAL DE PROCEDIMIENTO EN CASO DE SINIESTRO', {
                size: SZ_8, bold: true, caps: true,
            })],
            spacing: SP_ZERO,
        })],
    });
}

function buildIndexChildren() {
    return [
        // "CONTENIDO" title — Noto Sans, 18pt, bold, #000F47
        new Paragraph({
            children: [r('CONTENIDO', { size: SZ_18, bold: true, color: NAVY, caps: true })],
            spacing:  { before: 0, after: pt(18), line: 240, lineRule: LineRuleType.AUTO },
        }),
        // Jinja2 paragraph loop
        pJinja('{%p for item in indexItems %}'),
        pTocRow('{{ item.name }}', '{{ item.startPage }}'),
        pJinja('{%p endfor %}'),
    ];
}

// ─────────────────────────────────────────────────────────────────────────────
// SECTION 3: BODY FOOTER
// ─────────────────────────────────────────────────────────────────────────────
function buildBodyFooter() {
    return new Footer({
        children: [new Paragraph({
            children: [
                r('Página ', { size: SZ_10 }),
                new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: SZ_10, bold: true }),
                r(' de ', { size: SZ_10 }),
                r('{{ total_pages }}', { size: SZ_10, bold: true }),
            ],
            alignment: AlignmentType.RIGHT,
            spacing:   SP_ZERO,
        })],
    });
}

// ─────────────────────────────────────────────────────────────────────────────
// BODY: Aspectos Generales (Item 1 — always present)
// ─────────────────────────────────────────────────────────────────────────────
function buildAspectosGenerales() {
    return [
        pSectionStart(),
        pHeading('Aspectos Generales'),
        pEmpty(),                    // 1 nbsp after heading
        pBullet([r('Actuar en todo momento como si no existiera seguro, empleando en todo momento los medios necesarios para evitar o minimizar las pérdidas.')]),
        pEmpty(),
        pBullet([r('Dar aviso de inmediato a los organismos o instituciones encargadas de acuerdo al tipo de siniestro:')]),
        pEmpty(),
        buildEmergencyTable(),
        pEmpty(),
        pBullet([r('Efectuar la denuncia policial inmediatamente, de ser posible antes de las 24 horas, en la comisaría del sector.')]),
        pEmpty(),
        pBullet([r('Dar aviso a la brevedad a '), rB('{{ brokerName }}:')]),
        pEmpty(),                    // 1 nbsp above Central Telefónica
        pCentralTitle([new TextRun({ text: 'Central Telefónica:', font: FONT, size: SZ_11, bold: true, color: BLACK }),
                       new TextRun({ text: '\t\t(01) 604-1000', font: FONT, size: SZ_11, bold: true, color: BLACK })]),
        pEmpty(),                    // 1 nbsp above Gerente Responsable
        pCentralTitle([new TextRun({ text: 'Gerente Responsable: ', font: FONT, size: SZ_11, bold: true, color: BLACK }),
                       new TextRun({ text: '{{ unitLeader }}',      font: FONT, size: SZ_11, bold: true, color: BLACK })]),
        pExecData('Celular', '{{ leaderMobile }}'),
        pExecData('Correo',  '{{ leaderEmail }}'),
        pEmpty(),                    // 1 nbsp above Ejecutivo/a Responsable
        pCentralTitle([new TextRun({ text: 'Ejecutivo/a Responsable: ', font: FONT, size: SZ_11, bold: true, color: BLACK }),
                       new TextRun({ text: '{{ executiveName }}',       font: FONT, size: SZ_11, bold: true, color: BLACK })]),
        pExecData('Celular', '{{ executiveMobile }}'),
        pExecData('Correo',  '{{ executiveEmail }}'),
        pEmpty(),
        pBullet([r('No tomar acciones de limpieza, remoción de escombros o modificación de los locales o bienes afectados sin la autorización escrita de la compañía de Seguros, salvo los necesarios para detener o minimizar los daños, en estos casos se recomienda tomar fotografías.')]),
        pEmpty(),
        pBullet([r('Tomar las medidas necesarias para aminorar las pérdidas. (Obrar en todo momento como si no tuvieran cobertura de seguro).')]),
        pEmpty(),
        pBullet([r('Ofrecer todas las facilidades del caso a los representantes de la Compañía de Seguros y al Adjuster del siniestro para agilizar los trámites de liquidación del siniestro, así como proporcionar a la brevedad toda la documentación requerida.')]),
    ];
}

// ─────────────────────────────────────────────────────────────────────────────
// ALL BODY SECTIONS
// ─────────────────────────────────────────────────────────────────────────────
const XXXXX_r = () => [rB('{{ brokerName }}')];
const XXXXX_mid = (before, after) => [r(before), rB('{{ brokerName }}'), r(after)];

function buildBodyChildren() {
    return [

        // ── Item 1: Aspectos Generales (always) ──────────────────────────────
        ...buildAspectosGenerales(),

        // ── Item 2: Incendio ──────────────────────────────────────────────────
        ...buildStandardSection(2, 'Seguro de Todo Riesgo de Incendio y Líneas Aliadas',
            [
                'Tomar las medidas necesarias para aminorar las pérdidas. (Obrar en todo momento como si no tuvieran cobertura de seguro).',
                XXXXX_mid('Comunicarse con ', ' por la vía más rápida (Teléfono, mail, etc.) dentro de las 24 horas de la ocurrencia, indicando el lugar, fecha y hora del siniestro, así como las posibles causas que originaron el daño, si es factible.'),
                'Efectuar la denuncia policial en la comisaría del sector, dentro de las 24 horas de ocurrido el evento (en caso de hecho delictuoso y/o accidente).',
                XXXXX_mid('Mantener informado a ', ' sobre el monto total y definitivo al que ascendieron las pérdidas, daños y/o cualquier variación que existiera con respecto al monto original reclamado.'),
            ],
            [
                'Copia Certificada de la Denuncia Policial. (En caso de hecho delictuoso)',
                'Informe Interno de la ocurrencia (fecha y circunstancias).',
                'Informe Técnico sobre el origen del daño (causa raíz), detallando los daños que presentan los bienes del Asegurado.',
                'Presupuesto de Reparación (en el caso de bienes dañados), disgregando los costos unitarios de repuestos y mano de obra, para su revisión y aprobación.',
                'Copia de las facturas de adquisición y cotizaciones de proveedores del ramo para su reemplazo en el caso de bienes destruidos.',
                'Detalle de Pérdida.',
                [r('En caso el ajustador del reclamo solicite información adicional, ésta deberá ser remitida primero a '), rB('{{ brokerName }}'), r(' para su evaluación y posterior entrega al ajustador.')],
            ],
            5
        ),

        // ── Item 3: Equipo Electrónico ────────────────────────────────────────
        ...buildStandardSection(3, 'Equipo Electrónico',
            [
                'Tomar las medidas necesarias para aminorar las pérdidas. (Obrar en todo momento como si no tuvieran cobertura de seguro).',
                XXXXX_mid('Comunicarse con ', ' por la vía más rápida (Teléfono, mail, etc.) dentro de las 24 horas de la ocurrencia, indicando el lugar, fecha y hora del siniestro, así como las posibles causas que originaron el daño, si es factible.'),
                'Efectuar la denuncia policial en la comisaría del sector, dentro de las 24 horas de ocurrido el evento (en caso de hecho delictuoso y/o accidente).',
                XXXXX_mid('Mantener informado a ', ' sobre el monto total y definitivo a que ascendieron las pérdidas, daños y/o cualquier variación que existiera con respecto al monto original reclamado.'),
            ],
            [
                'Informe Interno de la ocurrencia en Word (especificar detalladamente cómo, cuándo, dónde y qué es lo que sucedió).',
                'Informe Técnico sobre el origen del daño, detallando los componentes afectados y los trabajos de reparación, para su evaluación. Especificar si el equipo se encuentra operativo o no, solo en casos de daños a equipos.',
                'Preexistencia del equipo siniestrado (factura de compra y/o guía de remisión y/o pantallazo del sistema SAP, etc.).',
                'Presupuesto y/o cotización de un equipo nuevo similar de iguales características al equipo siniestrado.',
                'Acta de asignación del equipo al trabajador afectado.',
                [r('En caso el ajustador del reclamo solicite información adicional, ésta deberá ser remitida primero a '), rB('{{ brokerName }}'), r(' para su evaluación y posterior entrega al ajustador.')],
            ],
            4
        ),

        // ── Item 4: Rotura de Maquinaria ─────────────────────────────────────
        ...buildStandardSection(4, 'Rotura de Maquinaria',
            [
                'Tomar las medidas necesarias para aminorar las pérdidas. (Obrar en todo momento como si no tuvieran cobertura de seguro).',
                XXXXX_mid('Comunicarse con ', ' por la vía más rápida (Teléfono, mail, etc.) dentro de las 24 horas de la ocurrencia, indicando el lugar, fecha y hora del siniestro, así como las posibles causas que originaron el daño, si es factible.'),
                'Efectuar la denuncia policial en la comisaría del sector, dentro de las 24 horas de ocurrido el evento (en caso de hecho delictuoso y/o accidente).',
                XXXXX_mid('Mantener informado a ', ' sobre el monto total y definitivo a que ascendieron las pérdidas, daños y/o cualquier variación que existiera con respecto al monto original reclamado.'),
            ],
            [
                'Informe Interno de la ocurrencia (fecha y circunstancias).',
                'Informe Técnico sobre el origen del daño, detallando los componentes afectados y los trabajos de reparación, para su evaluación.',
                'Informe Técnico del origen de la falla (causa raíz) por parte de la empresa, designada para la evaluación y reparación del equipo.',
                'Reportes y/o registros de mantenimientos realizados al equipo y reparaciones anteriores (12 meses).',
                'Presupuesto de reparación, disgregando los costos unitarios de repuestos y mano de obra, para su revisión y aprobación.',
                'Presupuesto de un equipo nuevo similar y de las mismas características que el equipo afectado.',
                [r('En caso el ajustador del reclamo solicite información adicional, ésta deberá ser remitida primero a '), rB('{{ brokerName }}'), r(' para su evaluación y posterior entrega al ajustador.')],
            ],
            3
        ),

        // ── Item 5: Todo Riesgo Equipo Contratista ────────────────────────────
        ...buildStandardSection(5, 'Todo Riesgo Equipo Contratista',
            [
                'Tomar las medidas necesarias para aminorar las pérdidas. (Obrar en todo momento como si no tuvieran cobertura de seguro).',
                XXXXX_mid('Comunicarse con ', ' por la vía más rápida (Teléfono, mail, etc.) dentro de las 24 horas de la ocurrencia, indicando el lugar, fecha y hora del siniestro, así como las posibles causas que originaron el daño, si es factible.'),
                'Efectuar la denuncia policial en la comisaría del sector, dentro de las 24 horas de ocurrido el evento (en caso de hecho delictuoso y/o accidente).',
                XXXXX_mid('Mantener informado a ', ' sobre el monto total y definitivo a que ascendieron las pérdidas, daños y/o cualquier variación que existiera con respecto al monto original reclamado.'),
            ],
            [
                'Informe Interno de la ocurrencia, elaborado por el Supervisor Responsable.',
                'Declaración del operador del equipo afectado, sobre la ocurrencia.',
                'Informe Técnico de daños emitido por la empresa especializada designada para la evaluación y reparación del equipo.',
                'Tres últimos reportes y/o registros de mantenimientos realizados al equipo y reparaciones anteriores.',
                'Presupuesto de reparación, disgregando los costos unitarios de repuestos y mano de obra, para su revisión y aprobación.',
                'Presupuesto de un equipo nuevo similar y de las mismas características que el equipo afectado.',
                [r('En caso el ajustador del reclamo solicite información adicional, ésta deberá ser remitida primero a '), rB('{{ brokerName }}'), r(' para su evaluación y posterior entrega al ajustador.')],
            ],
            4
        ),

        // ── Item 6: CAR ───────────────────────────────────────────────────────
        ...buildStandardSection(6, 'Todo Riesgo Construcción - CAR',
            [
                'Tomar las medidas necesarias para aminorar las pérdidas. (Obrar en todo momento como si no tuvieran cobertura de seguro).',
                XXXXX_mid('Comunicarse con ', ' por la vía más rápida (Teléfono, mail, etc.) dentro de las 24 horas de la ocurrencia, indicando el lugar, fecha y hora del siniestro, así como las posibles causas que originaron el daño, si es factible.'),
                'Efectuar la denuncia policial en la comisaría del sector, dentro de las 24 horas de ocurrido el evento (en caso de hecho delictuoso y/o accidente).',
                XXXXX_mid('Mantener informado a ', ' sobre el monto total y definitivo a que ascendieron las pérdidas, daños y/o cualquier variación que existiera con respecto al monto original reclamado.'),
            ],
            [
                'Copia Certificada de la Denuncia Policial. (en caso de hecho delictuoso)',
                'Informe interno de ocurrencia, emitido por el residente de obra respectivo.',
                'Asientos del cuaderno de obra que incluyan la ocurrencia del siniestro.',
                'Presupuesto de reparación de daños detallado por partidas, metrados y precios unitarios.',
                'Memoria descriptiva de la obra asegurada.',
                'Cronograma general de la obra antes y después del siniestro.',
                'Fotografías de los daños ocasionados por el siniestro.',
                'Carta de reclamo del tercero afectado. (en caso de daños provocados a terceros)',
                'Presupuesto de construcción de la obra asegurada.',
                'Medidas de emergencia adoptadas por el asegurado para aminorar la pérdida.',
                [r('En caso el ajustador del reclamo solicite información adicional, ésta deberá ser remitida primero a '), rB('{{ brokerName }}'), r(' para su evaluación y posterior entrega al ajustador.')],
            ],
            3
        ),

        // ── Item 7: EAR ───────────────────────────────────────────────────────
        ...buildStandardSection(7, 'Seguro de Montaje EAR',
            [
                'Tomar las medidas necesarias para aminorar las pérdidas. (Obrar en todo momento como si no tuvieran cobertura de seguro).',
                XXXXX_mid('Comunicarse con ', ' por la vía más rápida (Teléfono, mail, etc.) dentro de las 24 horas de la ocurrencia, indicando el lugar, fecha y hora del siniestro, así como las posibles causas que originaron el daño, si es factible.'),
                'Efectuar la denuncia policial en la comisaría del sector, dentro de las 24 horas de ocurrido el evento (en caso de hecho delictuoso y/o accidente).',
                XXXXX_mid('Mantener informado a ', ' sobre el monto total y definitivo a que ascendieron las pérdidas, daños y/o cualquier variación que existiera con respecto al monto original reclamado.'),
            ],
            [
                'Copia Certificada de la Denuncia Policial. (en caso de hecho delictuoso)',
                'Informe Interno de la ocurrencia emitido por el Supervisor Responsable de Obra.',
                'Informe Técnico emitido por parte del Área Técnica del Asegurado sobre el origen de la avería.',
                'Presupuesto de reparación de daños detallado por partidas, metrados y precios unitarios.',
                'Memoria descriptiva de la obra asegurada.',
                'Planos de las estructuras/instalaciones afectadas, pertenecientes a la obra asegurada.',
                'Fotografías de los daños ocasionados por el siniestro.',
                'Carta de reclamo del tercero afectado. (en caso de daños provocados a terceros)',
                'Medidas de emergencia adoptadas por el asegurado para aminorar la pérdida.',
                [r('En caso el ajustador del reclamo solicite información adicional, ésta deberá ser remitida primero a '), rB('{{ brokerName }}'), r(' para su evaluación y posterior entrega al ajustador.')],
            ],
            2
        ),

        // ── Item 8: Robo y/o Asalto ──────────────────────────────────────────
        ...buildStandardSection(8, 'Robo y/o Asalto',
            [
                'Tomar las medidas necesarias para aminorar las pérdidas. (Obrar en todo momento como si no tuvieran cobertura de seguro).',
                XXXXX_mid('Comunicarse con ', ' por la vía más rápida (Teléfono, mail, etc.) dentro de las 24 horas de la ocurrencia, indicando el lugar, fecha y hora del siniestro, así como las posibles causas que originaron el daño, si es factible.'),
                'Efectuar la denuncia policial en la comisaría del sector, dentro de las 24 horas de ocurrido el evento.',
                XXXXX_mid('Mantener informado a ', ' sobre el monto total y definitivo a que ascendieron las pérdidas, daños y/o cualquier variación que existiera con respecto al monto original reclamado.'),
            ],
            [
                'Copia Certificada de la Denuncia Policial.',
                'Sustento de la preexistencia de los bienes siniestrados (facturas y/o documentos contables).',
                'Presupuestos de reposición de cada uno de los equipos siniestrados. (no reparables)',
                'Inventario pre y post siniestros de los activos sustraídos. (en caso de robo)',
                'Presupuesto de reparación del Inmueble (en caso existan daños en el inmueble).',
                [r('En caso el ajustador del reclamo solicite información adicional, ésta deberá ser remitida primero a '), rB('{{ brokerName }}'), r(' para su evaluación y posterior entrega al ajustador.')],
            ],
            2
        ),

        // ── Item 9: Deshonestidad ─────────────────────────────────────────────
        ...wrapSection(9, [
            pSectionStart(),
            pHeading('Deshonestidad'),
            pEmpty(),                    // 1 nbsp above ¿Qué debo hacer?
            pTitleBody('¿Qué debo hacer?'),
            pEmpty(),
            pBullet([r('Tomar las medidas necesarias para aminorar las pérdidas. (Obrar en todo momento como si no tuvieran cobertura de seguro).')]),
            pEmpty(),
            pBullet(XXXXX_mid('Comunicarse con ', ' por la vía más rápida (Teléfono, mail, etc.) dentro de las 24 horas de la ocurrencia, indicando el lugar, fecha y hora del siniestro, así como las posibles causas que originaron el daño, si es factible.')),
            pEmpty(),
            pBullet([r('Efectuar la denuncia policial en la comisaría del sector, dentro de las 24 horas de ocurrido el evento.')]),
            pEmpty(),
            pBullet(XXXXX_mid('Mantener informado a ', ' sobre el monto total y definitivo a que ascendieron las pérdidas, daños y/o cualquier variación que existiera con respecto al monto original reclamado.')),
            pEmpty(),
            pEmpty(),
            pTitleBody('¿Qué documentos debo presentar para que atiendan el siniestro?'),
            pEmpty(),
            pTitleBody('Documentación Básica:'),
            pEmpty(),
            pSubBullet('Denuncia policial o a la Fiscalía, contra los que resulten responsables del ilícito.'),
            pSubBullet('Avances o Resultados de la investigación policial o fiscal.'),
            pSubBullet('Informe interno de la ocurrencia.'),
            pSubBullet('Auditoría que determine el monto de pérdida, con copia de los documentos contables que lo respalden.'),
            pSubBullet('De tener identificado al trabajador involucrado remitir File Personal que contenga:'),
            pSubSubBullet('Certificación y verificación de domicilio.'),
            pSubSubBullet('Verificación del DNI con la Reniec.'),
            pSubSubBullet('Certificado de Antecedentes Policiales y Penales.'),
            pSubSubBullet('Liquidación de Beneficios sociales (deberán ser retenidas o depositadas a nombre de la aseguradora).'),
            pSubSubBullet('Sustento de las últimas vacaciones tomadas por el deshonesto.'),
            pSubBullet('PDT 601 Declaración de Numero de trabajadores a SUNAT correspondiente al periodo del siniestro.'),
            pSubBullet('Sustentar el cumplimiento de las normas mínimas de control, como inventarios, cuadres de caja, etc.'),
            pSubBullet([r('En caso el ajustador del reclamo solicite información adicional, ésta deberá ser remitida primero a '), rB('{{ brokerName }}'), r(' para su evaluación y posterior entrega al ajustador.')]),
            ...nbspArr(2),
            ...closingBullets(),
        ]),

        // ── Item 10: Responsabilidad Civil ────────────────────────────────────
        ...wrapSection(10, [
            pSectionStart(),
            pHeading('Seguro de Responsabilidad Civil'),
            pEmpty(),                    // 1 nbsp above ¿Qué debo hacer?
            pTitleBody('¿Qué debo hacer?'),
            pEmpty(),
            pBullet(XXXXX_mid('Comunicarse con ', ' por la vía más rápida (Teléfono, mail, etc.) dentro de las 24 horas de la ocurrencia.')),
            pEmpty(),
            pBullet([r('En el caso de que se ocasione daños a propiedades de terceros, tomar las medidas necesarias para aminorar o limitar los daños.')]),
            pEmpty(),
            pBullet([r('En caso de daños personales a terceros, brindar la atención médica correspondiente, llevando al afectado a un Centro Médico, Clínica u Hospital más cercano, de igual forma, comunicarse de inmediato con '), rB('{{ brokerName }}'), r(' a fin de que los aseguradores tomen conocimiento del caso y se pueda contemplar la atención del mismo una vez activada la póliza de Responsabilidad Civil.')]),
            pEmpty(),
            pEmpty(),
            pTitleBody('¿Qué documentos debo presentar para que atiendan el siniestro?'),
            pEmpty(),
            pTitleBody('Documentación Básica:'),
            pEmpty(),
            pSubBullet('Carta de reclamo del tercero afectado.'),
            pSubBullet('Informe Técnico sobre las circunstancias del siniestro.'),
            pSubBullet('Informe de ocurrencia.'),
            pSubBullet('Relación detallada y valorizada al costo de los bienes dañados del tercero.'),
            pSubBullet([r('En caso el tercero demande al asegurado, entregar a '), rB('{{ brokerName }}'), r(' dicha demanda para que sea notificada a la Compañía de Seguros.')]),
            pSubBullet([r('Tan pronto se evalúe el monto de los daños a terceros, remitir a la oficina de '), rB('{{ brokerName }}'), r(' dicha información.')]),
            pSubBullet([r('En caso el ajustador del reclamo solicite información adicional, ésta deberá ser remitida primero a '), rB('{{ brokerName }}'), r(' para su evaluación y posterior entrega al ajustador.')]),
            pEmpty(),
            pEmpty(),
            pTitleBody('¿Cuál es el siguiente paso?'),
            pEmpty(),
            pBullet([r('Es importante tener en cuenta que la póliza de Responsabilidad Civil no es una cobertura de daño directo o indemnizatorio tan pronto se presente el reclamo. Esta póliza se activa únicamente cuando existe responsabilidad como causante de daños personales o materiales a un tercero producto de un accidente, según condiciones de la póliza y esencialmente cuando se inicia un reclamo formal o se abre un proceso civil en contra de la empresa. Su activación NO es inmediata y debe ser canalizada a través de un Ajustador de Seguros.')]),
            pEmpty(),
            pBullet([r('No se deberá de realizar transacciones ni reconocer indemnizaciones, ni responsabilidades sin conocimiento previo de la aseguradora, así como la autorización escrita de la aseguradora.')]),
            pEmpty(),
            pBullet([r('Una vez liquidado el reclamo por parte del ajustador, éste remitirá a '), rB('{{ brokerName }}'), r(' la transacción extrajudicial suscrita con la parte afectada, así como el convenio de ajuste, los cuales deberán ser devueltos con firmas legalizadas en el caso de las transacciones y firmado y sellado en el caso del convenio de ajuste, documentos con los cuales se dará por culminada la atención del caso.')]),
        ]),

        // ── Item 11: Transporte Nacional ──────────────────────────────────────
        ...buildTransportSection(11, 'Seguro de Transporte Nacional',
            [
                XXXXX_mid('Comunicarse con ', ' por la vía más rápida (Teléfono, mail, etc.) dentro de las 24 horas de la ocurrencia, indicando el lugar, fecha y hora del siniestro, así como evaluar los daños, aproximar la pérdida en cuanto a cantidades y/o valorización, e indicar el tipo de mercadería si es factible.'),
                'Cuando sea dudoso el estado en que se recibe la mercadería o cuando se recibe con pérdidas o daños evidentes, se debe dejar expresa constancia en los documentos de recepción de la mercadería.',
                'Es importante documentar toda la información posible sobre el siniestro, tomando fotografías y registrando los detalles importantes.',
                XXXXX_mid('En caso de Robo o Accidente de tránsito, efectuar la denuncia policial en la comisaría del sector, y remitir a ', ' copia certificada de dicha denuncia; deberá contener la descripción de la ocurrencia lo más detallada y exacta posible, así como los documentos en que amparan la carga y valorización aproximada de la pérdida.'),
            ],
            [
                'Denuncia policial (accidentes, robo) y/o informe de ocurrencia (daños).',
                'Documentos del vehículo (SOAT, tarjeta de propiedad, revisión técnica, permiso de circulación).',
                'Documentos personales del chofer y ayudante (DNI, brevete, antecedentes policiales, etc.).',
                'Dosaje etílico del chofer (en caso accidentes de tránsito).',
                'Guías de remisión de transportista y remitente.',
                'En caso de daños a maquinarias y/o equipos: Presupuesto de reparación (en caso exista posibilidad de reparar) o Presupuesto de reposición (en caso de rechazar las partes dañadas).',
                'Informe de control de calidad (en caso de mercaderías perecibles).',
                'Carta de reclamo al responsable del siniestro.',
                'Remitir copia de la factura comercial que acredite la pre existencia de los bienes.',
                [r('En caso el ajustador del reclamo solicite información adicional, ésta deberá ser remitida primero a '), rB('{{ brokerName }}'), r(' para su evaluación y posterior entrega al ajustador.')],
            ],
            2
        ),

        // ── Item 12: Importaciones ────────────────────────────────────────────
        ...buildTransportSection(12, 'Seguro de Importaciones',
            [
                XXXXX_mid('Comunicarse con ', ' por la vía más rápida (Teléfono, mail, etc.) dentro de las 24 horas de la ocurrencia, indicando el lugar, fecha y hora del siniestro, así como evaluar los daños, aproximar la pérdida en cuanto a cantidades y/o valorización, e indicar el tipo de mercadería si es factible.'),
                XXXXX_mid('Comunicar a ', ' todo faltante de bulto entero, así como instruir a su Agente de Aduanas a fin de cursar las cartas de reclamo correspondientes a la empresa naviera o aérea, según sea el caso, y confirmación de envío del proveedor.'),
                'Cuando sea dudoso el estado en que se recibe la mercadería o cuando se recibe con pérdidas o daños evidentes, se debe dejar expresa constancia en los documentos de recepción de la mercadería.',
                'Es importante documentar toda la información posible sobre el siniestro, tomando fotografías y registrando los detalles importantes.',
                XXXXX_mid('En caso de Robo o Accidente de tránsito, en el tramo Puerto / Almacén, efectuar la denuncia policial en la comisaría del sector, y remitir a ', ' copia certificada de dicha denuncia.'),
            ],
            [
                'Copia de la factura comercial de origen.',
                'Copia de la lista de contenido (Packing list).',
                'Copia del Conocimiento de Embarque o Guía aérea.',
                'Póliza de consumo (aplicación o certificado de seguros).',
                'Guía de remisión de remitente y transportista.',
                'Volante de despacho.',
                'Detalle valorizado del reclamo en Excel.',
                'DUA.',
                'Certificado de peso del Terminal Marítimo.',
                'Carta reclamo a la Compañía aérea, marítima y/o terrestre por mermas y/o faltantes.',
                'Respuesta de la Cía. aérea, marítima y/o terrestre, si lo hubiera.',
            ],
            0
        ),

        // ── Item 13: Vehículos (3 pages) ──────────────────────────────────────
        ...wrapSection(13, [
            pSectionStart(),
            pHeading('Seguro de Vehículos'),
            pEmpty(),                    // 1 nbsp above ¿Qué debo hacer?
            pTitleBody('¿Qué debo hacer?'),
            pBullet([r('Llamar de inmediato a la Central de Emergencia de la Compañía de Seguros, quienes enviarán un procurador al lugar del accidente o brindará la asesoría virtual según lo que corresponda de acuerdo con el tipo de evento declarado.')]),
            pEmpty(),                    // 1 nbsp above insurance companies
            new Paragraph({ children: [r('RIMAC\t\t\t411-1111', { bold: true })],    alignment: AlignmentType.CENTER, spacing: SP_ZERO }),
            new Paragraph({ children: [r('PACIFICO\t\t\t415-1515', { bold: true })],  alignment: AlignmentType.CENTER, spacing: SP_ZERO }),
            new Paragraph({ children: [r('MAPFRE\t\t\t213-7373', { bold: true })],    alignment: AlignmentType.CENTER, spacing: SP_ZERO }),
            new Paragraph({ children: [r('LA POSITIVA\t\t\t211-0211', { bold: true })],  alignment: AlignmentType.CENTER, spacing: SP_ZERO }),
            pEmpty(),                    // 1 nbsp below insurance companies
            pBullet([r('Presentarse de inmediato a la comisaría del sector a fin de efectuar la denuncia policial y someterse al dosaje etílico dentro de las cuatro horas siguientes de ocurrido el accidente de tránsito. Asimismo, cumplir con realizar el peritaje de daños, manifestación y/o cualquier otra diligencia que soliciten las autoridades.')]),
            pBullet(XXXXX_mid('Comunicarse con ', ' por la vía más rápida (Teléfono, mail, etc.) dentro de las 24 horas de la ocurrencia, indicando la placa del vehículo, el lugar, fecha y hora del siniestro, así como las posibles causas que originaron el daño.')),
            pEmpty(),
            pEmpty(),                    // 2 nbsp before ¿Qué documentos?
            pTitleBody('¿Qué documentos debo presentar para que atiendan el siniestro?'),
            pEmpty(),
            pSubtitleBody('En caso sea una pérdida total o robo total del vehículo:'),
            pSubBullet('Original de la tarjeta de propiedad.'),
            pSubBullet('Original del certificado SOAT.'),
            pSubBullet('Llaves del vehículo.'),
            pSubBullet('Copia de los DNI de los propietarios legales de la unidad.'),
            pSubBullet('Copia de la partida de matrimonio en caso de ser casados.'),
            pSubBullet('Copia de los DNI de los representantes legales del propietario del vehículo en caso de persona jurídica.'),
            pSubBullet('Copia de la vigencia de poder actualizada del representante legal de la empresa, donde se especifique las facultades para transferir los bienes muebles a nombre de la empresa propietaria.'),
            pSubBullet('Copia del RUC de la empresa en caso el propietario sea persona jurídica.'),
            pSubBullet('Factura por un monto simbólico de US$1.18 de la empresa propietaria del vehículo a favor de la aseguradora, por la venta de los restos del vehículo siniestrado.'),
            pSubBullet('Formato firmado de la aseguradora del Sistema de Prevención de Lavado de Activos.'),
            pSubBullet('Estado de cuenta del Impuesto Vehicular (SAT), cancelado a la fecha de indemnización.'),
            pSubBullet('Gravámenes municipales libre de afectación (Lima, Callao o provincia).'),
            pSubBullet('Gravamen policial libre de afectaciones.'),
            pSubBullet('Gravamen otorgado por la SUNARP libre de cualquier afectación.'),
            pSubBullet('Declaración jurada de actualización de datos, declarando la baja del vehículo para exonerarlo del pago del impuesto automotriz, por el siniestro de la pérdida total o robo total del vehículo.'),
            pEmpty(),                    // 1 nbsp before En caso sea una pérdida parcial
            pSubtitleBody('En caso sea una pérdida parcial:'),
            pSubBullet('Copia de la denuncia policial, peritaje de daños, resultado del dosaje etílico, fotografías, informe del operador de GPS y/o cualquier otro documento adicional que requiera el seguro.'),
            pSubBullet('Trasladar el vehículo siniestrado a un taller afiliado de la aseguradora para su reparación, indicando que no deberán iniciar los trabajos hasta que el técnico de la compañía de seguros apruebe el presupuesto correspondiente.'),
            pSubBullet('Para poder retirar el vehículo, una vez terminada su reparación, es necesario efectuar el pago de la franquicia o deducible correspondiente directamente al taller o a la aseguradora de ser el caso.'),
            pEmpty(),
            pEmpty(),                    // 2 nbsp before Recomendaciones
            pTitleBody('Recomendaciones:'),
            pBullet([r('En caso de existir daños personales, el primer paso a seguir será llevar al (los) herido(s) a la clínica u hospital más cercano y luego proceder de acuerdo con los puntos detallados anteriormente. En caso de atropello, buscar atención médica de inmediato así la persona atropellada no presente aparentemente ninguna lesión exterior. Según ley, la póliza Soat deberá ser la primera cobertura en activarse.')]),
            pEmpty(),
            pBullet([r('No aceptar ningún tipo de responsabilidades ni ofrecer pago alguno. Cualquier aceptación de reclamos, acuerdos o pactos transaccionales con terceros, sin autorización de la Compañía de Seguros, podría ser motivo para que ésta se libere de responsabilidades respecto al siniestro.')]),
            pEmpty(),
            pBullet(XXXXX_mid('En caso de que el vehículo quedara detenido después de un atropello o choque con lesiones, comunicar este hecho de inmediato a ', ' para coordinar con la aseguradora la asesoría legal para la posible libertad del vehículo.')),
            pEmpty(),
            pBullet(XXXXX_mid('De producirse algún siniestro en el cual sea necesario efectuar reparaciones, sugerimos realizadas en cualquier concesionario de la marca del vehículo siniestrado y/o en cualquier taller afiliado de la aseguradora. (', ' se abstiene de recomendar algún taller de reparaciones o factoría en especial).')),
            pEmpty(),
            pBullet([r('No prender el motor del vehículo siniestrado luego de haber sufrido un evento que pudiera involucrar daños en el motor o pérdida de fluidos a consecuencia de haberse volteado o haber sufrido impacto en la parte baja o frontal de la unidad. Se deberá recurrir a los servicios de una grúa.')]),
            pEmpty(),
            pEmpty(),                    // 2 nbsp before ¿Cuánto tiempo?
            pTitleBody('¿Cuánto tiempo demora la atención de mi siniestro?'),
            pBullet([r('Si el siniestro es un robo total se deberá esperar 30 días para que la Compañía de Seguros proceda a declarar la pérdida total del vehículo y para proceder con la indemnización se deberán entregar los documentos detallados anteriormente, así como la firma del acta de transferencia.')]),
            pEmpty(),
            pBullet([r('Si el siniestro es un daño parcial, el tiempo lo estima el taller de reparación en base a la magnitud de los daños del vehículo y el tiempo que demore su reparación y/o importación de repuestos.')]),
        ]),

    ]; // end bodyChildren
}

// ─────────────────────────────────────────────────────────────────────────────
// MAIN — assemble and write document
// ─────────────────────────────────────────────────────────────────────────────
async function buildDocument() {

    const coverChildren = buildCoverChildren();

    const doc = new Document({
        numbering: { config: NUMBERING_CONFIG },

        sections: [
            // ── Section 1: Cover ─────────────────────────────────────────────
            {
                properties: {
                    type: SectionType.NEXT_PAGE,
                    page: {
                        size: { width: PAGE_W, height: PAGE_H },
                        margin: { top: cm(2.54), bottom: cm(2.54), left: cm(1.9), right: cm(1.9) },
                    },
                },
                children: coverChildren,
            },
            // ── Section 2: Index ─────────────────────────────────────────────
            {
                properties: {
                    type: SectionType.NEXT_PAGE,
                    page: {
                        size: { width: PAGE_W, height: PAGE_H },
                        margin: { top: cm(5.10), bottom: cm(3.33), left: cm(2.54), right: cm(2.54) },
                    },
                },
                headers: { default: buildIndexHeader() },
                children: buildIndexChildren(),
            },
            // ── Section 3: Body ──────────────────────────────────────────────
            {
                properties: {
                    type: SectionType.NEXT_PAGE,
                    page: {
                        size: { width: PAGE_W, height: PAGE_H },
                        margin: { top: cm(2.54), bottom: cm(2.34), left: cm(1.9), right: cm(1.9) },
                        pageNumbers: { start: 1, formatType: NumberFormat.DECIMAL },
                    },
                },
                headers: { default: new Header({ children: [new Paragraph({ children: [] })] }) },
                footers: { default: buildBodyFooter() },
                children: buildBodyChildren(),
            },
        ],
    });

    // ── Post-process: inject background shape XML ─────────────────────────────
    // Packer.toBuffer produces a valid ZIP. adm-zip reads it, we patch
    // word/document.xml replacing the marker run with the wps:wsp shape XML,
    // then write the final ZIP.
    const AdmZip = require('adm-zip');

    const zipBuffer = await Packer.toBuffer(doc);
    const zip       = new AdmZip(zipBuffer);

    let docXml = zip.readAsText('word/document.xml');

    // The shape XML has no inline namespace redeclarations —
    // document.xml declares all prefixes at the root element.
    const shapeXml = makeBackgroundShapeXml();

    // Ensure xmlns:a is declared ONCE at the document root.
    //
    // When no ImageRun: docx omits xmlns:a entirely → add it at root.
    // When ImageRun present: docx adds xmlns:a inline on child elements
    //   (a:graphicFrameLocks, a:graphic) → remove those inline declarations
    //   and add it once at root instead.
    //
    // Having xmlns:a on child elements rather than root is legal XML but
    // Word is strict: it requires namespace declarations at the root level
    // when the same prefix is used across multiple drawing contexts.
    const NS_A = 'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"';
    // Find the end of the <w:document ...> opening tag (not the <?xml?> declaration).
    const wDocStart   = docXml.indexOf('<w:document ');
    const rootDeclEnd = docXml.indexOf('>', wDocStart);   // end of <w:document ...>
    let   rootPart    = docXml.slice(0, rootDeclEnd);
    let   bodyPart    = docXml.slice(rootDeclEnd);
    // Strip xmlns:a from all child elements in the body
    bodyPart = bodyPart.split(NS_A).join('');
    // Ensure xmlns:a appears exactly once in the <w:document> opening tag
    if (!rootPart.includes('xmlns:a=')) {
        docXml = rootPart + ' ' + NS_A + bodyPart;
    } else {
        docXml = rootPart + bodyPart;
    }

    const markerStart = docXml.indexOf('__BACKGROUND_SHAPE__');
    if (markerStart !== -1) {
        // Replace the entire <w:p>...</w:p> containing the marker.
        // This avoids nested <w:r> issues — shapeXml is a bare <w:drawing>
        // injected directly inside a fresh <w:p>.
        const pStart = docXml.lastIndexOf('<w:p>', markerStart);
        const pEnd   = docXml.indexOf('</w:p>', markerStart) + '</w:p>'.length;
        if (pStart !== -1 && pEnd > pStart) {
            const replacePara = '<w:p>'
                + '<w:pPr><w:spacing w:after="0" w:before="0" w:line="240" w:lineRule="auto"/></w:pPr>'
                + '<w:r>' + shapeXml + '</w:r>'
                + '</w:p>';
            docXml = docXml.slice(0, pStart) + replacePara + docXml.slice(pEnd);
            zip.updateFile('word/document.xml', Buffer.from(docXml, 'utf-8'));
            console.log('\u2705 Background shape injected successfully.');
        } else {
            console.warn('\u26a0\ufe0f  Could not find <w:p> for marker.');
        }
    } else {
        console.warn('\u26a0\ufe0f  Background shape marker not found.');
    }

    zip.writeZip('template_siniestros.docx');
    console.log('✅ template_siniestros.docx generated successfully.');
    console.log('⚠️  Replace XXXXX with the broker/corredor name before distributing.');
}

buildDocument().catch((err) => {
    console.error('❌ Error:', err);
    process.exit(1);
});
