/**
 * Template Generator — Carta de Despacho
 *
 * Generates template.docx with Jinja2/docxtpl placeholders.
 * Simple sections use {{variable}} and {% if %} tags directly in text.
 * Complex table sections (multiple insured / financing) are placeholder
 * markers that helpers.py replaces with python-docx built subdocuments.
 *
 * A4, standard margins (2.5cm), Arial 10pt, es-PE
 *
 * DXA reference: 1 inch = 1440 DXA, 1 cm ≈ 567 DXA
 * A4 content width with 2.5cm margins: 11906 - (2 × 1417) = 9072 DXA
 */

"use strict";

const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  AlignmentType, WidthType, BorderStyle, ShadingType, VerticalAlign,
  SpaceType, TableLayoutType,
  Header, Footer, PageNumber,
  ImageRun,
  HorizontalPositionRelativeFrom, VerticalPositionRelativeFrom,
  TextWrappingType, TextWrappingSide,
} = require("docx");

// ─────────────────────────────────────────────────────────────────────────────
// CONSTANTS
// ─────────────────────────────────────────────────────────────────────────────

const FONT          = "Noto Sans";
const FONT_BLACK    = "Noto Sans Black"; // used for executive name in header
const SIZE          = 20;           // 10pt in half-points
const SIZE_BARCODE  = 36;           // 18pt for barcode font
const SIZE_HEADER   = 16;           // 8pt in half-points — header/footer text
const SIZE_NOTE     = 12;           // 6pt in half-points — closing note
const LANG          = { id: "es-PE" };
const PAGE_W        = 11906;        // A4 width in DXA
const MARGIN        = 1417;         // 2.5cm in DXA
const CONTENT_W     = PAGE_W - (2 * MARGIN); // 9072 DXA

// Brand colors
const COLOR_HEADER_BG   = "000F47";  // table header background
const COLOR_HEADER_TEXT = "CDECFF";  // table header text
const COLOR_BORDER      = "000F47";  // table border color
const COLOR_BLACK       = "000000";
const COLOR_LINK        = "2E74B5";  // hyperlink / email color in page header
const COLOR_WHITE       = "FFFFFF";  // white — used for inner header borders

// Table column widths (must sum to CONTENT_W = 9072)
// Policy table: RAMO | PÓLIZA | LIQUIDACIÓN | PRIMA NETA | PRIMA TOTAL
const COL_POLICY = [2000, 2000, 1800, 1636, 1636];

// Financing table: CUOTA N° | FECHA VENCIMIENTO | IMPORTE
const COL_FINANCING = [2200, 3672, 3200];

// Annex table: ANEXO | CONTENIDO
const COL_ANNEX = [1200, 7872];

// Signature table: left col | right col (equal halves)
const COL_SIG = [4536, 4536];

// ─────────────────────────────────────────────────────────────────────────────
// STYLE HELPERS
// Each helper returns props/children arrays for reuse across all tables.
// TO MODIFY STYLES: change the constants above or the helpers below.
// ─────────────────────────────────────────────────────────────────────────────

/** Standard paragraph spacing — no space after, single line */
const paraSpacing = { after: 0, line: 240, lineRule: "auto" };

/** Build a standard run with consistent font/size/lang */
function run(text, opts = {}) {
  return new TextRun({
    text,
    font: opts.font || FONT,
    size: opts.size || SIZE,
    bold:      opts.bold      || false,
    color:     opts.color     || COLOR_BLACK,
    underline: opts.underline || undefined,
    language:  LANG,
  });
}

/**
 * Build a paragraph with consistent spacing.
 * alignment defaults to JUSTIFY for body text — matching the document spec.
 * Pass AlignmentType.LEFT or CENTER explicitly where needed (tables, headers).
 */
function para(children, alignment = AlignmentType.JUSTIFIED) {
  return new Paragraph({
    alignment,
    spacing: paraSpacing,
    children: Array.isArray(children) ? children : [children],
  });
}

/** Empty paragraph — used as spacer between sections */
function emptyPara() {
  return para([run("")]);
}

/** Standard visible border for all sides */
function border(color = COLOR_BORDER) {
  return { style: BorderStyle.SINGLE, size: 4, color };
}

/** All four visible borders */
function allBorders(color = COLOR_BORDER) {
  const b = border(color);
  return { top: b, bottom: b, left: b, right: b };
}

/**
 * All four outer borders visible, inner horizontal and vertical borders white.
 * Used for table header rows to create a visual divider without visible inner lines.
 */
function headerRowBorders() {
  const outer = border(COLOR_BORDER);
  const inner = { style: BorderStyle.SINGLE, size: 4, color: COLOR_WHITE };
  return { top: outer, bottom: outer, left: outer, right: outer, insideH: inner, insideV: inner };
}

/** No borders (invisible) — used for signature table */
function noBorders() {
  const b = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
  return { top: b, bottom: b, left: b, right: b };
}

/**
 * Hidden bottom+left+right borders — used for the empty col 1 cell in policy TOTAL row.
 * Only top border is visible.
 */
function hiddenAllButTop() {
  const visible = border(COLOR_BORDER);
  const hidden  = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
  return { top: visible, right: hidden, bottom: hidden, left: hidden };
}

/**
 * Hidden bottom border only — used for the empty col 2 cell in policy TOTAL row.
 */
function hiddenBottom() {
  const visible = border(COLOR_BORDER);
  const hidden  = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
  return { top: visible, right: visible, bottom: hidden, left: visible };
}

/** Hidden bottom and left border — used for the empty TOTAL label cell in financing */
function hiddenBottomLeft() {
  const visible = border(COLOR_BORDER);
  const hidden  = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
  return { top: visible, right: visible, bottom: hidden, left: hidden };
}

/** Header cell shading */
const headerShading = { fill: COLOR_HEADER_BG, type: ShadingType.CLEAR };

/** White cell shading */
const whiteShading = { fill: "FFFFFF", type: ShadingType.CLEAR };

// Cell padding — top/bottom 140 DXA (≈2.5mm) gives harmonious row height.
// Left/right 120 DXA (≈2.1mm) keeps content away from borders.
// Sync this value with CELL_MARGIN_TB in helpers.py.
const cellMargins = { top: 110, bottom: 110, left: 120, right: 120 };

/** Build a header cell with blue background and navy text */
function headerCell(text, width, opts = {}) {
  return new TableCell({
    width:   { size: width, type: WidthType.DXA },
    borders: allBorders(),
    shading: headerShading,
    margins: cellMargins,
    verticalAlign: VerticalAlign.CENTER,
    columnSpan: opts.span || 1,
    children: [para(
      [run(text.toUpperCase(), { bold: true, color: COLOR_HEADER_TEXT })],
      AlignmentType.CENTER
    )],
  });
}

/** Build a plain data cell */
function dataCell(text, width, alignment = AlignmentType.CENTER, opts = {}) {
  return new TableCell({
    width:   { size: width, type: WidthType.DXA },
    borders: opts.borders || allBorders(),
    shading: whiteShading,
    margins: cellMargins,
    verticalAlign: VerticalAlign.CENTER,
    children: [para(
      [run(text.toUpperCase(), { bold: opts.bold || false })],
      alignment
    )],
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// TABLE BUILDERS
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Build the policy table header row.
 * Used in all policy table variants.
 */
function policyHeaderRow(currency) {
  return new TableRow({ children: [
    headerCell("RAMO",                              COL_POLICY[0]),
    headerCell("PÓLIZA",                            COL_POLICY[1]),
    headerCell("{{liquidacionHeader}}",             COL_POLICY[2]),
    headerCell(`PRIMA NETA ${currency}`,            COL_POLICY[3]),
    headerCell(`PRIMA TOTAL ${currency}`,           COL_POLICY[4]),
  ]});
}

/**
 * Build a single policy data row.
 * Prima Neta and Prima Total are right-aligned per spec.
 */
function policyDataRow(ramo, numero, recibo, prima, total) {
  return new TableRow({ children: [
    dataCell(ramo,   COL_POLICY[0], AlignmentType.CENTER),
    dataCell(numero, COL_POLICY[1], AlignmentType.CENTER),
    dataCell(recibo, COL_POLICY[2], AlignmentType.CENTER),
    dataCell(prima,  COL_POLICY[3], AlignmentType.RIGHT),
    dataCell(total,  COL_POLICY[4], AlignmentType.RIGHT),
  ]});
}

/**
 * Build the TOTAL summary row for the policy table.
 * Col 1: empty, no left/right/bottom borders.
 * Col 2: empty, no bottom border.
 * Col 3: "TOTAL" bold centered.
 * Col 4: sum of Prima Neta, bold right-aligned.
 * Col 5: sum of Prima Total, bold right-aligned.
 * Only shown when there is more than 1 policy row.
 */
function policyTotalRow(sumaPrimaNeta, sumaPrimaTotal) {
  return new TableRow({ children: [
    // Col 1 — empty, no left/right/bottom borders
    new TableCell({
      width:   { size: COL_POLICY[0], type: WidthType.DXA },
      borders: hiddenAllButTop(),
      shading: whiteShading,
      margins: cellMargins,
      children: [para([run("")])],
    }),
    // Col 2 — empty, no bottom border
    new TableCell({
      width:   { size: COL_POLICY[1], type: WidthType.DXA },
      borders: hiddenBottom(),
      shading: whiteShading,
      margins: cellMargins,
      children: [para([run("")])],
    }),
    // Col 3 — TOTAL label
    dataCell("TOTAL", COL_POLICY[2], AlignmentType.CENTER, { bold: true }),
    // Col 4 — Prima Neta sum
    dataCell(sumaPrimaNeta, COL_POLICY[3], AlignmentType.RIGHT, { bold: true }),
    // Col 5 — Prima Total sum
    dataCell(sumaPrimaTotal, COL_POLICY[4], AlignmentType.RIGHT, { bold: true }),
  ]});
}

/**
 * Build a full-width merged header row for insured name.
 * Used when multipleClients is active.
 */
function insuredNameRow(name) {
  return new TableRow({ children: [
    new TableCell({
      width:      { size: CONTENT_W, type: WidthType.DXA },
      borders:    allBorders(),
      shading:    headerShading,
      margins:    cellMargins,
      columnSpan: 5,
      children:   [para(
        [run(name.toUpperCase(), { bold: true, color: COLOR_HEADER_TEXT })],
        AlignmentType.CENTER
      )],
    }),
  ]});
}

/**
 * Build a policy table for a single insured.
 * polizas: array of {POLIZA_RAMO, POLIZA_NUMERO, POLIZA_RECIBO, POLIZA_PRIMA, POLIZA_PRIMA_TOTAL}
 */
function buildPolicyTable(polizas, currency, insuredName = null) {
  const rows = [];

  // Optional insured name header row (only for multiple insured case)
  if (insuredName) {
    rows.push(insuredNameRow(insuredName));
  }

  // Fixed column header
  rows.push(policyHeaderRow(currency));

  // One data row per policy
  for (const p of polizas) {
    rows.push(policyDataRow(
      p.POLIZA_RAMO        || "",
      p.POLIZA_NUMERO      || "",
      p.POLIZA_RECIBO      || "",
      p.POLIZA_PRIMA       || "",
      p.POLIZA_PRIMA_TOTAL || "",
    ));
  }

  // Total row — only when more than 1 policy
  if (polizas.length > 1) {
    rows.push(policyTotalRow(
      "{{sumaPrimaNeta}}",
      "{{sumaPrimaTotal}}"
    ));
  }

  return new Table({
    width:        { size: CONTENT_W, type: WidthType.DXA },
    columnWidths: COL_POLICY,
    layout:       TableLayoutType.FIXED,
    rows,
  });
}

/**
 * Build the financing table header row.
 */
function financingHeaderRow(currency, title = null) {
  const rows = [];

  // Optional title row (insured name or branch name)
  if (title) {
    rows.push(new TableRow({ children: [
      new TableCell({
        width:      { size: CONTENT_W, type: WidthType.DXA },
        borders:    allBorders(),
        shading:    headerShading,
        margins:    cellMargins,
        columnSpan: 3,
        children:   [para(
          [run(title.toUpperCase(), { bold: true, color: COLOR_HEADER_TEXT })],
          AlignmentType.CENTER
        )],
      }),
    ]}));
  }

  rows.push(new TableRow({ children: [
    headerCell("CUOTA",              COL_FINANCING[0]),
    headerCell("FECHA DE VENCIMIENTO", COL_FINANCING[1]),
    headerCell(`IMPORTE ${currency}`, COL_FINANCING[2]),
  ]}));

  return rows;
}

/**
 * Build a financing quota data row.
 */
function quotaDataRow(nro, vencimiento, importe) {
  return new TableRow({ children: [
    dataCell(nro,         COL_FINANCING[0], AlignmentType.CENTER),
    dataCell(vencimiento, COL_FINANCING[1], AlignmentType.CENTER),
    dataCell(importe,     COL_FINANCING[2], AlignmentType.CENTER),
  ]});
}

/**
 * Build the TOTAL row for financing table.
 * Left cell has hidden bottom+left borders (empty label cell per spec).
 * Right cell shows the total amount in bold.
 */
function totalRow(total, currency) {
  return new TableRow({ children: [
    // Empty cell — bottom and left borders hidden per spec
    new TableCell({
      width:   { size: COL_FINANCING[0], type: WidthType.DXA },
      borders: hiddenBottomLeft(),
      shading: whiteShading,
      margins: cellMargins,
      children: [para([run("")])],
    }),
    // TOTAL label cell
    dataCell("TOTAL", COL_FINANCING[1], AlignmentType.CENTER, { bold: true }),
    // Total amount cell
    dataCell(total, COL_FINANCING[2], AlignmentType.CENTER, { bold: true }),
  ]});
}

/**
 * Build a complete financing table for a set of quotas.
 * title: optional string shown as merged header row (insured name or branch)
 * subtotal: optional second title (branch name for Case 4 Individual)
 */
function buildFinancingTable(cuotas, total, currency, title = null, subtitle = null) {
  const rows = [];

  // Title rows (insured name and/or branch name)
  const headerRows = financingHeaderRow(currency, title);
  if (subtitle) {
    // Insert branch subtitle between title and column headers
    const subRow = new TableRow({ children: [
      new TableCell({
        width:      { size: CONTENT_W, type: WidthType.DXA },
        borders:    allBorders(),
        shading:    headerShading,
        margins:    cellMargins,
        columnSpan: 3,
        children:   [para(
          [run(subtitle.toUpperCase(), { bold: true, color: COLOR_HEADER_TEXT })],
          AlignmentType.CENTER
        )],
      }),
    ]});
    rows.push(headerRows[0]);  // title row
    rows.push(subRow);          // subtitle row
    rows.push(headerRows[1]);   // column headers
  } else {
    rows.push(...headerRows);
  }

  // Quota data rows
  for (const q of cuotas) {
    rows.push(quotaDataRow(
      String(q.nro         || ""),
      q.vencimiento || "",
      q.importe     || "",
    ));
  }

  // Total row
  rows.push(totalRow(total || "0.00", currency));

  return new Table({
    width:        { size: CONTENT_W, type: WidthType.DXA },
    columnWidths: COL_FINANCING,
    layout:       TableLayoutType.FIXED,
    rows,
  });
}

/**
 * Build the annexes table.
 * anexos: array of {NUMERO, CONTENIDO}
 */
function buildAnnexTable(anexos) {
  const rows = [];

  // Header row
  rows.push(new TableRow({ children: [
    new TableCell({
      width:   { size: COL_ANNEX[0], type: WidthType.DXA },
      borders: allBorders(),
      shading: headerShading,
      margins: cellMargins,
      children: [para(
        [run("Anexo", { bold: true, color: COLOR_HEADER_TEXT })],
        AlignmentType.CENTER
      )],
    }),
    new TableCell({
      width:   { size: COL_ANNEX[1], type: WidthType.DXA },
      borders: allBorders(),
      shading: headerShading,
      margins: cellMargins,
      children: [para(
        [run("Contenido", { bold: true, color: COLOR_HEADER_TEXT })],
        AlignmentType.CENTER
      )],
    }),
  ]}));

  // Data rows — Anexo centered, Contenido left-aligned
  for (const a of (anexos || [])) {
    rows.push(new TableRow({ children: [
      dataCell(a.NUMERO   || "", COL_ANNEX[0], AlignmentType.CENTER),
      new TableCell({
        width:   { size: COL_ANNEX[1], type: WidthType.DXA },
        borders: allBorders(),
        shading: whiteShading,
        margins: cellMargins,
        children: [para([run(a.CONTENIDO || "")], AlignmentType.LEFT)],
      }),
    ]}));
  }

  return new Table({
    width:        { size: CONTENT_W, type: WidthType.DXA },
    columnWidths: COL_ANNEX,
    layout:       TableLayoutType.FIXED,
    rows,
  });
}

/**
 * Build the signature table.
 * Two equal columns: unit leader | executive
 * Row 1: signature image placeholders
 * Row 2: name + title
 */
function buildSignatureTable() {
  return new Table({
    width:        { size: CONTENT_W, type: WidthType.DXA },
    columnWidths: COL_SIG,
    layout:       TableLayoutType.FIXED,
    rows: [
      // Row 1 — signature image placeholders
      new TableRow({ children: [
        new TableCell({
          width:   { size: COL_SIG[0], type: WidthType.DXA },
          borders: noBorders(),
          margins: cellMargins,
          children: [para(
            [run("{{unitLeaderSignature}}", { bold: true })],
            AlignmentType.CENTER
          )],
        }),
        new TableCell({
          width:   { size: COL_SIG[1], type: WidthType.DXA },
          borders: noBorders(),
          margins: cellMargins,
          children: [para(
            [run("{{executiveSignature}}", { bold: true })],
            AlignmentType.CENTER
          )],
        }),
      ]}),
      // Row 2 — name and title
      new TableRow({ children: [
        new TableCell({
          width:   { size: COL_SIG[0], type: WidthType.DXA },
          borders: noBorders(),
          margins: cellMargins,
          children: [
            para([run("{{unitLeader}}", { bold: true })],          AlignmentType.CENTER),
            para([run("GERENTE DE UNIDAD", { bold: true })],       AlignmentType.CENTER),
          ],
        }),
        new TableCell({
          width:   { size: COL_SIG[1], type: WidthType.DXA },
          borders: noBorders(),
          margins: cellMargins,
          children: [
            para([run("{{executiveName}}", { bold: true })],      AlignmentType.CENTER),
            para([run("EJECUTIVO(A) DE UNIDAD", { bold: true })], AlignmentType.CENTER),
          ],
        }),
      ]}),
    ],
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// PAGE HEADER
// Appears on the first page only (titlePage + default headers).
// Contains executive contact info pulled from pageUnit.py variables.
// Font: Arial 8pt throughout. executiveName uses Arial Black.
// Email line: colored (#2E74B5), underlined. Plain styled text — no live hyperlink
// (docxtpl cannot template hyperlink URLs stored in Word relationships XML).
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Build a single header paragraph with consistent 8pt spacing.
 * alignment defaults to LEFT for all header lines.
 */
function headerPara(children, alignment = AlignmentType.LEFT) {
  return new Paragraph({
    alignment,
    // No space after — header lines are tightly stacked
    spacing: { after: 0, line: 240, lineRule: "auto" },
    children: Array.isArray(children) ? children : [children],
  });
}

/**
 * Build a TextRun at 8pt (SIZE_HEADER = 16 half-points).
 * Accepts same opts as the main run() helper.
 */
function headerRun(text, opts = {}) {
  return new TextRun({
    text,
    font:      opts.font  || FONT,
    size:      SIZE_HEADER,           // always 8pt in header
    bold:      opts.bold  || false,
    color:     opts.color || COLOR_BLACK,
    underline: opts.underline || undefined,
    language:  LANG,
  });
}

/**
 * Build the first-page header section.
 *
 * Layout: the logo image floats absolutely on the left side of the header.
 * The text block sits to the right with a left indent of 10.2cm so it
 * does not overlap the image area.
 *
 * Image spec (all measurements converted to EMU: 1cm = 360000 EMU):
 *   Position:  0.2cm right of Column  →  72000 EMU horizontal
 *              0.02cm below Paragraph →   7200 EMU vertical
 *   Wrap:      "Delante del texto"    →  TextWrappingType.NONE, behindDocument: false
 *   Margins:   left/right 0.32cm     → 115200 EMU each
 *   Size:      4.48cm × 0.98cm       → 1612800 × 352800 EMU
 *   Source:    imgs/logo.png (relative to working directory at runtime)
 *
 * Text indent: 10.2cm → 5783 DXA (left indent on every header paragraph)
 *
 * Lines:
 *   1. {{executiveName}}      — Arial Black, 8pt, bold, UPPERCASE in header only
 *   2. {{executivePosition}}  — Arial, 8pt
 *   3. (empty line)
 *   4-6. XXX                  — placeholders
 *   7. {{executiveMobile}}
 *   8. {{executivePhone}}
 *   9. {{executiveEmail}}     — colored #2E74B5, underlined (plain text, no hyperlink)
 *  10. XXX                    — colored #2E74B5 placeholder, underlined
 */

// Left indent for all header text paragraphs in DXA (10.2cm × 567 = 5783)
const HEADER_TEXT_INDENT = 5783;

/**
 * Build a header paragraph with the standard 10.2cm left indent.
 * The indent pushes the text block to the right of the logo image.
 */
function headerParaIndented(children, alignment = AlignmentType.LEFT) {
  return new Paragraph({
    alignment,
    spacing: { after: 0, line: 240, lineRule: "auto" },
    indent:  { left: HEADER_TEXT_INDENT },   // 10.2cm left indent
    children: Array.isArray(children) ? children : [children],
  });
}

function buildFirstPageHeader() {
  // Load logo image from the imgs/ folder relative to the current working
  // directory. At runtime (app.py launch), cwd is the project root, so
  // "imgs/logo.png" resolves correctly.
  const logoBuffer = fs.readFileSync("imgs/logo_midnight.png");

  // Floating logo image — positioned absolutely, "in front of text" wrap
  const logoImage = new ImageRun({
    type: "png",
    data: logoBuffer,
    transformation: {
      width:  Math.round(4.48 * 360000 / 9144),  // EMU → points for docx-js: px at 96dpi
      height: Math.round(0.98 * 360000 / 9144),
    },
    // docx-js ImageRun uses EMU directly for floating layout
    floating: {
      horizontalPosition: {
        relative: HorizontalPositionRelativeFrom.COLUMN,
        offset:   0,        // 0cm → 0 EMU
      },
      verticalPosition: {
        relative: VerticalPositionRelativeFrom.PARAGRAPH,
        offset:   432000,   // 1.2cm → 432000 EMU
      },
      // "Delante del texto" — image sits in front, no text wrap around it
      wrap: {
        type: TextWrappingType.NONE,
        side: TextWrappingSide.BOTH_SIDES,
      },
      margins: {
        left:  115200,  // 0.32cm → 115200 EMU
        right: 115200,
        top:   0,
        bottom: 0,
      },
      // Explicit size in EMU for the floating anchor
      allowOverlap:    true,
      behindDocument:  false,
      lockAnchor:      false,
    },
  });

  return new Header({
    children: [
      // Anchor paragraph for the floating image.
      // The image floats independently; this paragraph just holds the anchor
      // so Word knows which paragraph the image is attached to.
      // It also carries the left indent so that even the anchor line is indented.
      // executiveName is uppercased here via Jinja2 filter — header only.
      new Paragraph({
        alignment: AlignmentType.LEFT,
        spacing:   { after: 0, line: 240, lineRule: "auto" },
        indent:    { left: HEADER_TEXT_INDENT },
        children: [
          logoImage,
          // Line 1 text inline with the anchor — executive name, Arial Black 8pt
          // Uppercase applied via Jinja2 upper filter for header display only
          headerRun("{{executiveName|upper}}", { font: FONT_BLACK, bold: true }),
        ],
      }),

      // Line 2 — executive position
      headerParaIndented([headerRun("{{executivePosition}}")]),

      // Line 3 — empty spacer
      headerParaIndented([headerRun("")]),

      // Lines 4-6 — placeholder text (company info to be defined later)
      headerParaIndented([headerRun("Marsh Peru S.A.C. Corredores de Seguros")]),
      headerParaIndented([headerRun("Calle Las Orquídeas, 675, Piso 15")]),
      headerParaIndented([headerRun("San Isidro, Lima 27 - Peru")]),

      // Line 7 — mobile phone
      headerParaIndented([headerRun("{{executiveMobile}}")]),

      // Line 8 — office phone
      headerParaIndented([headerRun("{{executivePhone}}")]),

      // Line 9 — email as styled text (color + underline).
      // A real mailto: hyperlink cannot be templated via docxtpl because Word stores
      // hyperlink URLs in the relationships XML which docxtpl does not process.
      // Visual result is identical: blue (#2E74B5) underlined text.
      headerParaIndented([
        new TextRun({
          text:      "{{executiveEmail}}",
          font:      FONT,
          size:      SIZE_HEADER,
          color:     COLOR_LINK,
          underline: { type: "single" },
          language:  LANG,
        }),
      ]),

      // Line 10 — colored placeholder (website / social / web address), underlined
      headerParaIndented([headerRun("www.marsh.com.pe", { color: COLOR_LINK, underline: { type: "single" } })]),

      // Line 11 — empty spacer
      headerParaIndented([headerRun("")]),
    ],
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// PAGE FOOTER
// "Página X de X" — only the numbers are bold, the rest is normal weight.
// Centered, 8pt, appears on all pages.
// ─────────────────────────────────────────────────────────────────────────────

function buildFooter() {
  return new Footer({
    children: [
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing:   { after: 0, line: 240, lineRule: "auto" },
        children: [
          // "Página " — normal weight
          new TextRun({ text: "Página ", font: FONT, size: SIZE_HEADER, language: LANG }),

          // Current page number — bold
          new TextRun({
            children: [PageNumber.CURRENT],
            font: FONT, size: SIZE_HEADER, bold: true, language: LANG,
          }),

          // " de " — normal weight
          new TextRun({ text: " de ", font: FONT, size: SIZE_HEADER, language: LANG }),

          // Total pages — bold
          new TextRun({
            children: [PageNumber.TOTAL_PAGES],
            font: FONT, size: SIZE_HEADER, bold: true, language: LANG,
          }),
        ],
      }),
    ],
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// JINJA2 PLACEHOLDER PARAGRAPHS
// These paragraphs contain Jinja2 tags that docxtpl processes at render time.
// helpers.py replaces the {{subdoc_*}} markers with python-docx built tables.
// ─────────────────────────────────────────────────────────────────────────────

/** A paragraph containing a raw Jinja2 tag (if/endif/for/endfor) */
function jinjaTag(tag) {
  return new Paragraph({
    spacing: paraSpacing,
    children: [new TextRun({ text: tag, font: FONT, size: SIZE, language: LANG })],
  });
}

/** A paragraph with a Jinja2 variable placeholder */
function jinjaVar(expression, opts = {}) {
  return para(
    [run(`{{${expression}}}`, opts)],
    opts.alignment || AlignmentType.LEFT
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// DOCUMENT BODY SECTIONS
// Each function returns an array of Paragraph/Table elements.
// ─────────────────────────────────────────────────────────────────────────────

function sectionHeader() {
  return [
    // OPE number — bold 10pt, left-aligned (not justified)
    para([run("OPE. {{letterNumber}}", { bold: true })], AlignmentType.LEFT),
    // Barcode — uses Code128A font, larger size, left-aligned
    new Paragraph({
      alignment: AlignmentType.LEFT,
      spacing: paraSpacing,
      children: [new TextRun({
        text: "{{barcode}}", font: "Code128A",
        size: SIZE_BARCODE, bold: true, language: LANG,
      })],
    }),
    emptyPara(),
    para([run("San Isidro, {{FECHA}}")], AlignmentType.LEFT),
    emptyPara(),
    para([run("Señores")], AlignmentType.LEFT),
    para([run("{{companyName}}", { bold: true })], AlignmentType.LEFT),
    para([run("{{address}}", { bold: true })], AlignmentType.LEFT),
    para([run("Presente. –")], AlignmentType.LEFT),
    emptyPara(),
    para([
      run("ATENCIÓN      :   ", { bold: true }),
      run("{{contactName}}", { bold: true }),
    ], AlignmentType.LEFT),
  ];
}

/**
 * Reference line and intro paragraph.
 * Uses Jinja2 conditions for letterType and multiplePolicies.
 * The reference text changes but the intro body text is common.
 * All body paragraphs are justified; reference lines are left-aligned.
 */
function sectionReference() {
  return [
    // Emisión — Una Póliza
    jinjaTag(`{%p if letterType == "Emision" and multiplePolicies == "Una Poliza" %}`),
    para([
      run("REFERENCIA   :   ", { bold: true }),
      run("EMISIÓN PÓLIZA {{POLIZA_RAMO}}", { bold: true, underline: { type: "single" } }),
    ], AlignmentType.LEFT),
    emptyPara(),
    para([run("Estimados señores:")], AlignmentType.LEFT),
    emptyPara(),
    para([
      run("Por medio de la presente adjuntamos la emisión de su póliza para el período " +
          "{{POLIZA_INICIO}} al {{POLIZA_FIN}}, emitida por "),
      run("{{POLIZA_ASEGURADORA}}", { bold: true }),
      run(" según se detalla a continuación:"),
    ]),
    jinjaTag(`{%p endif %}`),

    // Emisión — Varias Pólizas
    jinjaTag(`{%p if letterType == "Emision" and multiplePolicies == "Varias Polizas" %}`),
    para([
      run("REFERENCIA   :   ", { bold: true }),
      run("EMISIÓN PROGRAMA DE SEGUROS", { bold: true, underline: { type: "single" } }),
    ], AlignmentType.LEFT),
    emptyPara(),
    para([run("Estimados señores:")], AlignmentType.LEFT),
    emptyPara(),
    para([
      run("Por medio de la presente adjuntamos la emisión de sus pólizas que conforman " +
          "su programa de seguros para el período {{POLIZA_INICIO}} al {{POLIZA_FIN}}, emitidas por "),
      run("{{POLIZA_ASEGURADORA}}", { bold: true }),
      run(" según se detalla a continuación:"),
    ]),
    jinjaTag(`{%p endif %}`),

    // Renovación — Una Póliza
    jinjaTag(`{%p if letterType == "Renovacion" and multiplePolicies == "Una Poliza" %}`),
    para([
      run("REFERENCIA   :   ", { bold: true }),
      run("RENOVACIÓN PÓLIZA {{POLIZA_RAMO}}", { bold: true, underline: { type: "single" } }),
    ], AlignmentType.LEFT),
    emptyPara(),
    para([run("Estimados señores:")], AlignmentType.LEFT),
    emptyPara(),
    para([
      run("Por medio de la presente adjuntamos la renovación de su póliza para el período " +
          "{{POLIZA_INICIO}} al {{POLIZA_FIN}}, emitida por "),
      run("{{POLIZA_ASEGURADORA}}", { bold: true }),
      run(" según se detalla a continuación:"),
    ]),
    jinjaTag(`{%p endif %}`),

    // Renovación — Varias Pólizas
    jinjaTag(`{%p if letterType == "Renovacion" and multiplePolicies == "Varias Polizas" %}`),
    para([
      run("REFERENCIA   :   ", { bold: true }),
      run("RENOVACIÓN PROGRAMA DE SEGUROS", { bold: true, underline: { type: "single" } }),
    ], AlignmentType.LEFT),
    emptyPara(),
    para([run("Estimados señores:")], AlignmentType.LEFT),
    emptyPara(),
    para([
      run("Por medio de la presente adjuntamos la renovación de sus pólizas que conforman " +
          "su programa de seguros para el período {{POLIZA_INICIO}} al {{POLIZA_FIN}}, emitidas por "),
      run("{{POLIZA_ASEGURADORA}}", { bold: true }),
      run(" según se detalla a continuación:"),
    ]),
    jinjaTag(`{%p endif %}`),

    emptyPara(),
  ];
}

/**
 * Policy tables section.
 * The actual table content is a subdocument marker {{subdocPolicyTables}}
 * that helpers.py replaces with the appropriate python-docx built tables.
 */
function sectionPolicyTables() {
  return [
    jinjaVar("subdocPolicyTables"),
    emptyPara(),
  ];
}

/**
 * Financing section — only rendered when hasPayment == "Si".
 * Table content is a subdocument marker {{subdocFinancingTables}}.
 */
function sectionFinancing() {
  return [
    jinjaTag(`{%p if hasPayment == "Si" %}`),
    emptyPara(),
    para([
      run("Asimismo, adjuntamos los convenios de pago con el financiamiento " +
          "con fecha del primer vencimiento el {{firstDueDate}}"),
    ]),
    emptyPara(),
    jinjaVar("subdocFinancingTables"),
    emptyPara(),
    jinjaTag(`{%p endif %}`),
  ];
}

function sectionFixedBody() {
  return [
    para([run(
      "Agradeceremos proceder con el pago de la prima antes de su vencimiento " +
      "según las liquidaciones que se adjuntan."
    )]),
    emptyPara(),
    para([run(
      "Les recordamos que, según el Reglamento de Pago de Primas, Resolución SBS 225-2006 " +
      "y la Ley del Contrato de Seguros, Ley 29946, la demora y/o falta de pago ocasiona la " +
      "suspensión de la cobertura, la retención de indemnizaciones por siniestros, cargos por " +
      "mora y podría generar un reporte de deuda a las centrales de riesgo por parte de la aseguradora."
    )]),
    emptyPara(),
    para([run(
      "De conformidad con lo dispuesto en el Art. 341 de la Ley General del Sistema " +
      "Financiero y de Seguros Nro. 26702, apreciaremos nos devuelvan una copia de las " +
      "pólizas firmadas y selladas por ustedes para hacerlas llegar a la compañía de seguros."
    )]),
    emptyPara(),
    para([run("Tomar nota de la información incluida en los siguientes Anexos:")], AlignmentType.LEFT),
    emptyPara(),
  ];
}

/**
 * Annex table section.
 * The actual table is built as a python-docx subdocument in helpers.py
 * and injected here via {{subdocAnnexTable}}, eliminating all {% tr %} tags
 * from the template to avoid docxtpl 'unknown tag tr' errors.
 */
function sectionAnnexTable() {
  return [
    jinjaVar("subdocAnnexTable"),
    emptyPara(),
  ];
}

function sectionAnnexNote() {
  return [
    para([run(
      "Cabe precisar, que en los anexos adjuntos hemos resumido las principales condiciones y " +
      "garantías; sin embargo, es importante y necesario que procedan a leer detenidamente los " +
      "condicionados, cláusulas, coberturas, garantías y exclusiones indicadas en cada una de " +
      "sus pólizas, a fin de verificar que su riesgo está acorde con las exigencias de los " +
      "contratos de seguro."
    )]),
    emptyPara(),
  ];
}

function sectionEndorsement() {
  return [
    // Only Simple shows the inline paragraph — Detallado uses its own PageAnnex card
    jinjaTag(`{%p if endorsementType == "Simple" %}`),
    para([
      run("Asimismo, adjuntamos endoso de cesión de derechos, bajo la póliza de "),
      run("{{ENDOSO_RAMO}}", { bold: true }),
      run(", a favor de "),
      run("{{ENDOSO_BENEFICIARIO}}", { bold: true }),
      run("."),
    ]),
    emptyPara(),
    jinjaTag(`{%p endif %}`),
  ];
}

function sectionLegalBody() {
  return [
    para([
      run(
        "Estamos a su disposición para reunirnos y revisar en forma conjunta cada una de las " +
        "garantías detalladas. De existir otras medidas de seguridad que reemplacen o mejoren " +
        "las indicadas o alguna condición que no se ajusta a su negocio, deberán informarnos " +
        "para conversarlo y negociarlo con la aseguradora. Es importante tener en cuenta que " +
        "las aseguradoras, incluyendo "
      ),
      run("{{POLIZA_ASEGURADORA}}", { bold: true }),
      run(
        " están siendo muy exigentes en el cumplimiento de las medidas de seguridad exigidas " +
        "y su incumplimiento libera a la Aseguradora de toda responsabilidad frente al siniestro."
      ),
    ]),
    emptyPara(),
    para([
      run("Finalmente, el proceso de colocación de las pólizas ha sido efectuado por "),
      run("{{brokerName}}", { bold: true }),
      run(" en función a la información proporcionada por "),
      run("{{companyName}}", { bold: true }),
      run(" por lo que "),
      run("{{brokerName}}", { bold: true }),
      run(
        " no asume responsabilidad alguna frente a cualquier daño o perjuicio " +
        "que pueda sufrir el contratante, asegurado y/o beneficiario de la póliza como " +
        "consecuencia de la inexactitud de la información proporcionada, la veracidad y " +
        "oportunidad de esta."
      ),
    ]),
    emptyPara(),
  ];
}

/**
 * LOL section.
 * Sin Definir: both paragraphs shown as plain text (no variables).
 * General: first paragraph only.
 * Fijo: second paragraph with lolAmountValue and currency.
 */
function sectionLOL() {
  const lolGeneralRuns = [
    run("En ningún caso "), run("{{brokerName}}", { bold: true }),
    run(", el contratante, asegurado o beneficiario de la(s) póliza(s) " +
    "adjunta(s) al presente documento serán responsables por cualquier daño, directo y/o " +
    "indirecto y/o sanción y/o por cualquier pérdida de ganancias (lucro cesante) que surjan " +
    "de o en relación con cualquier servicio prestado por "), run("{{brokerName}}", { bold: true }),
    run(" o sus afiliadas. La responsabilidad total de "), run("{{brokerName}}", { bold: true }),
    run(", sus afiliadas y de sus respectivos empleados hacia el " +
    "contratante, asegurado o beneficiario que surja o se relacione con la prestación de los " +
    "Servicios, no excederá de los ingresos percibidos por "), run("{{brokerName}}", { bold: true }),
    run(" derivados exclusivamente de la póliza que ocasione el perjuicio."),
  ];

  const lolFijoPreRuns = [
    run("En ningún caso "), run("{{brokerName}}", { bold: true }),
    run(", el contratante, asegurado o beneficiario de la(s) póliza(s) " +
    "adjunta(s) al presente documento serán responsables por cualquier daño, directo y/o " +
    "indirecto y/o sanción y/o por cualquier pérdida de ganancias (lucro cesante) que surjan " +
    "de o en relación con cualquier servicio prestado por "), run("{{brokerName}}", { bold: true }),
    run(" o sus afiliadas. La responsabilidad total de "), run("{{brokerName}}", { bold: true }),
    run(", sus afiliadas y de sus respectivos empleados hacia el " +
    "contratante, asegurado o beneficiario de la(s) póliza(s) adjunta(s) al presente " +
    "documento que surja o se relacione con la prestación de los Servicios, no excederá de "),
  ];

  const lolMultinacionalRuns = [
    run("En ningún caso "), run("{{brokerName}}", { bold: true }),
    run(", el contratante, asegurado o beneficiario de la póliza adjunta al presente " +
    "documento serán responsables por cualquier daño, directo y/o indirecto y/o sanción " +
    "y/o por cualquier pérdida de ganancias (lucro cesante) que surjan de o en relación " +
    "con cualquier servicio prestado por "), run("{{brokerName}}", { bold: true }),
    run(" o sus afiliadas. La responsabilidad total de "), run("{{brokerName}}", { bold: true }),
    run(" PERU, sus afiliadas y de sus respectivos empleados hacia el contratante, asegurado " +
    "o beneficiario de la póliza adjunta al presente documento que surja o se relacione con " +
    "la prestación de los Servicios, no excederá de acuerdo con lo negociado por la Oficina Productora."),
  ];

  return [
    // Sin Definir: both paragraphs as plain text
    jinjaTag(`{%p if lolAmountType == "Sin Definir" %}`),
    para(lolGeneralRuns),
    emptyPara(),
    para([...lolFijoPreRuns, run("{{currency}} {{lolAmountValue}}.")]),
    emptyPara(),
    jinjaTag(`{%p endif %}`),

    // General: first paragraph only
    jinjaTag(`{%p if lolAmountType == "General" %}`),
    para(lolGeneralRuns),
    emptyPara(),
    jinjaTag(`{%p endif %}`),

    // Fijo: second paragraph with amount variable
    jinjaTag(`{%p if lolAmountType == "Fijo" %}`),
    para([...lolFijoPreRuns, run("{{currency}} {{lolAmountValue}}.")]),
    emptyPara(),
    jinjaTag(`{%p endif %}`),

    // Multinacional: fixed paragraph — no variables except brokerName
    jinjaTag(`{%p if lolAmountType == "Multinacional" %}`),
    para(lolMultinacionalRuns),
    emptyPara(),
    jinjaTag(`{%p endif %}`),
  ];
}

function sectionClosing() {
  return [
    para([run(
      "Para mitigar el impacto de la inflación, tomar en cuenta que es muy importante que " +
      "revise el valor declarado de sus activos/exposiciones de riesgo durante el periodo de " +
      "vigencia de la póliza y no solamente en el proceso de renovación."
    )]),
    emptyPara(),
    para([
      run("{{brokerName}}", { bold: true }),
      run(
        " puede incluir, de manera no identificable, información relativa a su programa de " +
        "seguros para realizar análisis comparativos (benchmarking), modelado, ofertas de " +
        "análisis de datos y de seguros."
      ),
    ]),
    emptyPara(),
    para([run(
      "En caso de algún reclamo*, por favor comunicarse a los siguientes puntos de contactos:"
    )]),
    emptyPara(),
    // Contact list — 1cm left indent (567 DXA) to visually separate from body text
    new Paragraph({ alignment: AlignmentType.LEFT, spacing: paraSpacing,
      indent: { left: 567 },
      children: [
        run("–   Correo electrónico: "),
        new TextRun({ text: "Reclamos.Marsh.Peru@marsh.com", font: FONT, color: COLOR_LINK, underline: { type: "single" }, language: LANG }),
      ] }),
    new Paragraph({ alignment: AlignmentType.LEFT, spacing: paraSpacing,
      indent: { left: 567 },
      children: [run("–   Central telefónica: (01) 604 1000")] }),
    new Paragraph({ alignment: AlignmentType.LEFT, spacing: paraSpacing,
      indent: { left: 567 },
      children: [run("–   Mesa de partes: Oficina Principal – Las Orquídeas 675, Piso 15, San Isidro, Lima, Perú")] }),
    emptyPara(),
    para([run(
      "*Se define como reclamo a la comunicación en la que se manifiesta la insatisfacción " +
      "con la operación de la aseguradora y/o corredor de seguros, producto o servicio " +
      "recibido o por el incumplimiento de las obligaciones contempladas en los contratos o " +
      "en el marco normativo vigente, o manifestando la presunta afectación de su legítimo " +
      "interés, según la Resolución SBS Nro. 04036."
    )]),
    emptyPara(),
    para([run("Cordialmente,")], AlignmentType.LEFT),
    emptyPara(),
    buildSignatureTable(),
    emptyPara(),

    // Closing note — 6pt throughout.
    // Only "Nota:" is bold; the rest is regular weight.
    // SIZE_NOTE = 12 half-points = 6pt
    new Paragraph({
      alignment: AlignmentType.JUSTIFIED,
      spacing:   paraSpacing,
      children: [
        new TextRun({ text: "Nota: ", font: FONT, size: SIZE_NOTE, bold: true,  language: LANG }),
        new TextRun({
          text: "La Aseguradora que ha emitido la(s) póliza(s) adjunta(s) está regulada en el " +
                "Perú por la Superintendencia de Banca, Seguros y AFP y debe cumplir con todas las " +
                "leyes, regulaciones, condiciones para hacer negocios en el país incluyendo requisitos " +
                "de solvencia. Si usted está interesado en recibir mayor información sobre un " +
                "Asegurador o Aseguradores en particular, incluyendo la información sobre su fortaleza " +
                "y seguridad financiera, por favor póngase en contacto con su Ejecutivo de Cuentas " +
                "quien gustoso le brindará la información adicional que ustedes puedan requerir.",
          font: FONT, size: SIZE_NOTE, bold: false, language: LANG,
        }),
      ],
    }),
  ];
}

// ─────────────────────────────────────────────────────────────────────────────
// DOCUMENT ASSEMBLY
// ─────────────────────────────────────────────────────────────────────────────

const children = [
  ...sectionHeader(),
  ...sectionReference(),
  ...sectionPolicyTables(),
  ...sectionFinancing(),
  ...sectionFixedBody(),
  ...sectionAnnexTable(),
  ...sectionAnnexNote(),
  ...sectionEndorsement(),
  ...sectionLegalBody(),
  ...sectionLOL(),
  ...sectionClosing(),
];

const doc = new Document({
  styles: {
    default: {
      document: {
        run: { font: FONT, size: SIZE, language: LANG },
        paragraph: { spacing: paraSpacing },
      },
    },
  },
  sections: [{
    properties: {
      // titlePage: true makes Word use the `first` header for page 1
      // and the `default` header for all subsequent pages.
      // We only provide a `first` header (executive contact block) and
      // a `default` footer (page numbers). Pages 2+ have no header.
      titlePage: true,
      page: {
        size:   { width: 11906, height: 16838 },       // A4 in DXA
        margin: { top: MARGIN, right: MARGIN, bottom: MARGIN, left: MARGIN },
      },
    },
    // Header only on page 1 — uses `first` slot because titlePage: true
    headers: {
      first: buildFirstPageHeader(),
    },
    // Footer on all pages (page number)
    footers: {
      default: buildFooter(),
      // Also set first footer so page 1 gets the page number too
      first:   buildFooter(),
    },
    children,
  }],
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("template.docx", buffer);
  console.log("template.docx generated successfully");
});
