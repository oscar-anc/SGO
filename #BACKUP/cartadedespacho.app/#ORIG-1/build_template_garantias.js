/**
 * build_template_garantias.js
 * ============================
 * Generates template_garantias.docx — Garantías Particulares annex.
 *
 * Requires: docx, adm-zip  →  npm install adm-zip
 * Run:      node build_template_garantias.js
 *
 * ── Strategy ──────────────────────────────────────────────────────────────
 * 1. Build cover section using the docx library (logo, title, companyName
 *    placeholder, navy background shape, footer with page numbers).
 * 2. Post-process the generated ZIP with adm-zip to inject clean XML assets:
 *      - word/styles.xml          (7 styles only: the ones we actually use)
 *      - word/numbering.xml       (3 numIds only: SectionStart, bullet, decimal)
 *      - word/_rels/numbering.xml.rels  (bullet image references)
 *      - word/media/image1.png / image2.png  (numPicBullet images for » chevron)
 * 3. Inject navy background shape XML into the cover paragraph.
 *
 * ── Styles in styles.xml ──────────────────────────────────────────────────
 * Required base styles (Word mandates these):
 *   Normal          — base of all styles
 *   ListParagraph   — base of SectionStart, Heading, TextBody
 *   Header          — page header container
 *   Footer          — page footer container
 *
 * Custom styles used at runtime by helpers.generateGuarantees():
 *   SectionStart    — auto-decimal counter (numId=1), 36pt #82BAFF,
 *                     pageBreakBefore, blue bottom border
 *   Heading         — Noto Sans bold 18pt, 0 spacing
 *   TextBody        — Noto Sans 11pt, justified, 0 spacing, numId=2 (chevron)
 *
 * ── Numbering in numbering.xml ────────────────────────────────────────────
 *   numId=1 → abstractNumId=8  decimal auto-counter (SectionStart)
 *   numId=2 → abstractNumId=2  » chevron bullet, Noto Sans 11pt,
 *                               left=227 hanging=227
 *   numId=3 → abstractNumId=3  decimal list %1., Noto Sans 11pt,
 *                               left=227 hanging=227 (same indent as chevron)
 *
 * ── Runtime usage (helpers.generateGuarantees) ────────────────────────────
 *   python-docx opens this file directly (no docxtpl/subdocuments).
 *   {companyName} is a single run — replaced via run.text search.
 *   Content section is cleared and rebuilt programmatically using the
 *   style IDs and numIds defined above.
 */

'use strict';

const fs = require('fs');

const {
    Document, Packer, Paragraph, TextRun, AlignmentType,
    Header, Footer, ImageRun,
    PageNumber, NumberFormat, SectionType, LineRuleType,
} = require('docx');

// =============================================================================
// SECTION 1 — EMBEDDED XML ASSETS
// Extracted from GARANTIAS_PARTICULARES.docx and cleaned:
//   - styles.xml:    reduced from 31 custom styles to 7 (only what we use)
//   - numbering.xml: reduced from 11 numIds to 3 (SectionStart, bullet, decimal)
// Images are base64-encoded bullet glyphs referenced by numPicBullet in
// numbering.xml. These must be present in word/media/ for Word to open the file.
// =============================================================================

// ── styles.xml ───────────────────────────────────────────────────────────────
// Contains: Normal, ListParagraph, Header, Footer, SectionStart, Heading, TextBody
const STYLES_XML = `<?xml version='1.0' encoding='UTF-8' standalone='yes'?>
<w:styles xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml" xmlns:w15="http://schemas.microsoft.com/office/word/2012/wordml" xmlns:w16cex="http://schemas.microsoft.com/office/word/2018/wordml/cex" xmlns:w16cid="http://schemas.microsoft.com/office/word/2016/wordml/cid" xmlns:w16="http://schemas.microsoft.com/office/word/2018/wordml" xmlns:w16du="http://schemas.microsoft.com/office/word/2023/wordml/word16du" xmlns:w16sdtdh="http://schemas.microsoft.com/office/word/2020/wordml/sdtdatahash" xmlns:w16sdtfl="http://schemas.microsoft.com/office/word/2024/wordml/sdtformatlock" xmlns:w16se="http://schemas.microsoft.com/office/word/2015/wordml/symex" mc:Ignorable="w14 w15 w16se w16cid w16 w16cex w16sdtdh w16sdtfl w16du"><w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:asciiTheme="minorHAnsi" w:eastAsiaTheme="minorEastAsia" w:hAnsiTheme="minorHAnsi" w:cstheme="minorBidi"/><w:kern w:val="2"/><w:sz w:val="24"/><w:szCs w:val="24"/><w:lang w:val="en-GB" w:eastAsia="ja-JP" w:bidi="ar-SA"/><w14:ligatures w14:val="standardContextual"/></w:rPr></w:rPrDefault><w:pPrDefault><w:pPr><w:spacing w:after="160" w:line="278" w:lineRule="auto"/></w:pPr></w:pPrDefault></w:docDefaults><w:latentStyles w:defLockedState="0" w:defUIPriority="99" w:defSemiHidden="0" w:defUnhideWhenUsed="0" w:defQFormat="0" w:count="376"><w:lsdException w:name="Normal" w:uiPriority="0" w:qFormat="1"/><w:lsdException w:name="heading 1" w:uiPriority="9" w:qFormat="1"/><w:lsdException w:name="heading 2" w:semiHidden="1" w:uiPriority="9" w:unhideWhenUsed="1" w:qFormat="1"/><w:lsdException w:name="heading 3" w:semiHidden="1" w:uiPriority="9" w:unhideWhenUsed="1" w:qFormat="1"/><w:lsdException w:name="heading 4" w:semiHidden="1" w:uiPriority="9" w:unhideWhenUsed="1" w:qFormat="1"/><w:lsdException w:name="heading 5" w:semiHidden="1" w:uiPriority="9" w:unhideWhenUsed="1" w:qFormat="1"/><w:lsdException w:name="heading 6" w:semiHidden="1" w:uiPriority="9" w:unhideWhenUsed="1" w:qFormat="1"/><w:lsdException w:name="heading 7" w:semiHidden="1" w:uiPriority="9" w:unhideWhenUsed="1" w:qFormat="1"/><w:lsdException w:name="heading 8" w:semiHidden="1" w:uiPriority="9" w:unhideWhenUsed="1" w:qFormat="1"/><w:lsdException w:name="heading 9" w:semiHidden="1" w:uiPriority="9" w:unhideWhenUsed="1" w:qFormat="1"/><w:lsdException w:name="index 1" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="index 2" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="index 3" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="index 4" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="index 5" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="index 6" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="index 7" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="index 8" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="index 9" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="toc 1" w:semiHidden="1" w:uiPriority="39" w:unhideWhenUsed="1"/><w:lsdException w:name="toc 2" w:semiHidden="1" w:uiPriority="39" w:unhideWhenUsed="1"/><w:lsdException w:name="toc 3" w:semiHidden="1" w:uiPriority="39" w:unhideWhenUsed="1"/><w:lsdException w:name="toc 4" w:semiHidden="1" w:uiPriority="39" w:unhideWhenUsed="1"/><w:lsdException w:name="toc 5" w:semiHidden="1" w:uiPriority="39" w:unhideWhenUsed="1"/><w:lsdException w:name="toc 6" w:semiHidden="1" w:uiPriority="39" w:unhideWhenUsed="1"/><w:lsdException w:name="toc 7" w:semiHidden="1" w:uiPriority="39" w:unhideWhenUsed="1"/><w:lsdException w:name="toc 8" w:semiHidden="1" w:uiPriority="39" w:unhideWhenUsed="1"/><w:lsdException w:name="toc 9" w:semiHidden="1" w:uiPriority="39" w:unhideWhenUsed="1"/><w:lsdException w:name="Normal Indent" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="footnote text" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="annotation text" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="header" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="footer" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="index heading" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="caption" w:semiHidden="1" w:uiPriority="35" w:unhideWhenUsed="1" w:qFormat="1"/><w:lsdException w:name="table of figures" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="envelope address" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="envelope return" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="footnote reference" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="annotation reference" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="line number" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="page number" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="endnote reference" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="endnote text" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="table of authorities" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="macro" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="toa heading" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="List" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="List Bullet" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="List Number" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="List 2" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="List 3" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="List 4" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="List 5" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="List Bullet 2" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="List Bullet 3" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="List Bullet 4" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="List Bullet 5" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="List Number 2" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="List Number 3" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="List Number 4" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="List Number 5" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Title" w:uiPriority="10" w:qFormat="1"/><w:lsdException w:name="Closing" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Signature" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Default Paragraph Font" w:semiHidden="1" w:uiPriority="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Body Text" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Body Text Indent" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="List Continue" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="List Continue 2" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="List Continue 3" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="List Continue 4" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="List Continue 5" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Message Header" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Subtitle" w:uiPriority="11" w:qFormat="1"/><w:lsdException w:name="Salutation" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Date" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Body Text First Indent" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Body Text First Indent 2" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Note Heading" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Body Text 2" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Body Text 3" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Body Text Indent 2" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Body Text Indent 3" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Block Text" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Hyperlink" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="FollowedHyperlink" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Strong" w:uiPriority="22" w:qFormat="1"/><w:lsdException w:name="Emphasis" w:uiPriority="20" w:qFormat="1"/><w:lsdException w:name="Document Map" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Plain Text" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="E-mail Signature" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="HTML Top of Form" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="HTML Bottom of Form" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Normal (Web)" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="HTML Acronym" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="HTML Address" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="HTML Cite" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="HTML Code" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="HTML Definition" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="HTML Keyboard" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="HTML Preformatted" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="HTML Sample" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="HTML Typewriter" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="HTML Variable" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Normal Table" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="annotation subject" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="No List" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Outline List 1" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Outline List 2" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Outline List 3" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Table Simple 1" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Table Simple 2" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Table Simple 3" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Table Classic 1" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Table Classic 2" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Table Classic 3" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Table Classic 4" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Table Colorful 1" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Table Colorful 2" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Table Colorful 3" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Table Columns 1" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Table Columns 2" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Table Columns 3" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Table Columns 4" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Table Columns 5" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Table Grid 1" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Table Grid 2" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Table Grid 3" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Table Grid 4" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Table Grid 5" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Table Grid 6" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Table Grid 7" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Table Grid 8" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Table List 1" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Table List 2" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Table List 3" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Table List 4" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Table List 5" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Table List 6" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Table List 7" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Table List 8" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Table 3D effects 1" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Table 3D effects 2" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Table 3D effects 3" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Table Contemporary" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Table Elegant" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Table Professional" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Table Subtle 1" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Table Subtle 2" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Table Web 1" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Table Web 2" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Table Web 3" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Balloon Text" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Table Grid" w:uiPriority="39"/><w:lsdException w:name="Table Theme" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Placeholder Text" w:semiHidden="1"/><w:lsdException w:name="No Spacing" w:uiPriority="1" w:qFormat="1"/><w:lsdException w:name="Light Shading" w:uiPriority="60"/><w:lsdException w:name="Light List" w:uiPriority="61"/><w:lsdException w:name="Light Grid" w:uiPriority="62"/><w:lsdException w:name="Medium Shading 1" w:uiPriority="63"/><w:lsdException w:name="Medium Shading 2" w:uiPriority="64"/><w:lsdException w:name="Medium List 1" w:uiPriority="65"/><w:lsdException w:name="Medium List 2" w:uiPriority="66"/><w:lsdException w:name="Medium Grid 1" w:uiPriority="67"/><w:lsdException w:name="Medium Grid 2" w:uiPriority="68"/><w:lsdException w:name="Medium Grid 3" w:uiPriority="69"/><w:lsdException w:name="Dark List" w:uiPriority="70"/><w:lsdException w:name="Colorful Shading" w:uiPriority="71"/><w:lsdException w:name="Colorful List" w:uiPriority="72"/><w:lsdException w:name="Colorful Grid" w:uiPriority="73"/><w:lsdException w:name="Light Shading Accent 1" w:uiPriority="60"/><w:lsdException w:name="Light List Accent 1" w:uiPriority="61"/><w:lsdException w:name="Light Grid Accent 1" w:uiPriority="62"/><w:lsdException w:name="Medium Shading 1 Accent 1" w:uiPriority="63"/><w:lsdException w:name="Medium Shading 2 Accent 1" w:uiPriority="64"/><w:lsdException w:name="Medium List 1 Accent 1" w:uiPriority="65"/><w:lsdException w:name="Revision" w:semiHidden="1"/><w:lsdException w:name="List Paragraph" w:uiPriority="34" w:qFormat="1"/><w:lsdException w:name="Quote" w:uiPriority="29" w:qFormat="1"/><w:lsdException w:name="Intense Quote" w:uiPriority="30" w:qFormat="1"/><w:lsdException w:name="Medium List 2 Accent 1" w:uiPriority="66"/><w:lsdException w:name="Medium Grid 1 Accent 1" w:uiPriority="67"/><w:lsdException w:name="Medium Grid 2 Accent 1" w:uiPriority="68"/><w:lsdException w:name="Medium Grid 3 Accent 1" w:uiPriority="69"/><w:lsdException w:name="Dark List Accent 1" w:uiPriority="70"/><w:lsdException w:name="Colorful Shading Accent 1" w:uiPriority="71"/><w:lsdException w:name="Colorful List Accent 1" w:uiPriority="72"/><w:lsdException w:name="Colorful Grid Accent 1" w:uiPriority="73"/><w:lsdException w:name="Light Shading Accent 2" w:uiPriority="60"/><w:lsdException w:name="Light List Accent 2" w:uiPriority="61"/><w:lsdException w:name="Light Grid Accent 2" w:uiPriority="62"/><w:lsdException w:name="Medium Shading 1 Accent 2" w:uiPriority="63"/><w:lsdException w:name="Medium Shading 2 Accent 2" w:uiPriority="64"/><w:lsdException w:name="Medium List 1 Accent 2" w:uiPriority="65"/><w:lsdException w:name="Medium List 2 Accent 2" w:uiPriority="66"/><w:lsdException w:name="Medium Grid 1 Accent 2" w:uiPriority="67"/><w:lsdException w:name="Medium Grid 2 Accent 2" w:uiPriority="68"/><w:lsdException w:name="Medium Grid 3 Accent 2" w:uiPriority="69"/><w:lsdException w:name="Dark List Accent 2" w:uiPriority="70"/><w:lsdException w:name="Colorful Shading Accent 2" w:uiPriority="71"/><w:lsdException w:name="Colorful List Accent 2" w:uiPriority="72"/><w:lsdException w:name="Colorful Grid Accent 2" w:uiPriority="73"/><w:lsdException w:name="Light Shading Accent 3" w:uiPriority="60"/><w:lsdException w:name="Light List Accent 3" w:uiPriority="61"/><w:lsdException w:name="Light Grid Accent 3" w:uiPriority="62"/><w:lsdException w:name="Medium Shading 1 Accent 3" w:uiPriority="63"/><w:lsdException w:name="Medium Shading 2 Accent 3" w:uiPriority="64"/><w:lsdException w:name="Medium List 1 Accent 3" w:uiPriority="65"/><w:lsdException w:name="Medium List 2 Accent 3" w:uiPriority="66"/><w:lsdException w:name="Medium Grid 1 Accent 3" w:uiPriority="67"/><w:lsdException w:name="Medium Grid 2 Accent 3" w:uiPriority="68"/><w:lsdException w:name="Medium Grid 3 Accent 3" w:uiPriority="69"/><w:lsdException w:name="Dark List Accent 3" w:uiPriority="70"/><w:lsdException w:name="Colorful Shading Accent 3" w:uiPriority="71"/><w:lsdException w:name="Colorful List Accent 3" w:uiPriority="72"/><w:lsdException w:name="Colorful Grid Accent 3" w:uiPriority="73"/><w:lsdException w:name="Light Shading Accent 4" w:uiPriority="60"/><w:lsdException w:name="Light List Accent 4" w:uiPriority="61"/><w:lsdException w:name="Light Grid Accent 4" w:uiPriority="62"/><w:lsdException w:name="Medium Shading 1 Accent 4" w:uiPriority="63"/><w:lsdException w:name="Medium Shading 2 Accent 4" w:uiPriority="64"/><w:lsdException w:name="Medium List 1 Accent 4" w:uiPriority="65"/><w:lsdException w:name="Medium List 2 Accent 4" w:uiPriority="66"/><w:lsdException w:name="Medium Grid 1 Accent 4" w:uiPriority="67"/><w:lsdException w:name="Medium Grid 2 Accent 4" w:uiPriority="68"/><w:lsdException w:name="Medium Grid 3 Accent 4" w:uiPriority="69"/><w:lsdException w:name="Dark List Accent 4" w:uiPriority="70"/><w:lsdException w:name="Colorful Shading Accent 4" w:uiPriority="71"/><w:lsdException w:name="Colorful List Accent 4" w:uiPriority="72"/><w:lsdException w:name="Colorful Grid Accent 4" w:uiPriority="73"/><w:lsdException w:name="Light Shading Accent 5" w:uiPriority="60"/><w:lsdException w:name="Light List Accent 5" w:uiPriority="61"/><w:lsdException w:name="Light Grid Accent 5" w:uiPriority="62"/><w:lsdException w:name="Medium Shading 1 Accent 5" w:uiPriority="63"/><w:lsdException w:name="Medium Shading 2 Accent 5" w:uiPriority="64"/><w:lsdException w:name="Medium List 1 Accent 5" w:uiPriority="65"/><w:lsdException w:name="Medium List 2 Accent 5" w:uiPriority="66"/><w:lsdException w:name="Medium Grid 1 Accent 5" w:uiPriority="67"/><w:lsdException w:name="Medium Grid 2 Accent 5" w:uiPriority="68"/><w:lsdException w:name="Medium Grid 3 Accent 5" w:uiPriority="69"/><w:lsdException w:name="Dark List Accent 5" w:uiPriority="70"/><w:lsdException w:name="Colorful Shading Accent 5" w:uiPriority="71"/><w:lsdException w:name="Colorful List Accent 5" w:uiPriority="72"/><w:lsdException w:name="Colorful Grid Accent 5" w:uiPriority="73"/><w:lsdException w:name="Light Shading Accent 6" w:uiPriority="60"/><w:lsdException w:name="Light List Accent 6" w:uiPriority="61"/><w:lsdException w:name="Light Grid Accent 6" w:uiPriority="62"/><w:lsdException w:name="Medium Shading 1 Accent 6" w:uiPriority="63"/><w:lsdException w:name="Medium Shading 2 Accent 6" w:uiPriority="64"/><w:lsdException w:name="Medium List 1 Accent 6" w:uiPriority="65"/><w:lsdException w:name="Medium List 2 Accent 6" w:uiPriority="66"/><w:lsdException w:name="Medium Grid 1 Accent 6" w:uiPriority="67"/><w:lsdException w:name="Medium Grid 2 Accent 6" w:uiPriority="68"/><w:lsdException w:name="Medium Grid 3 Accent 6" w:uiPriority="69"/><w:lsdException w:name="Dark List Accent 6" w:uiPriority="70"/><w:lsdException w:name="Colorful Shading Accent 6" w:uiPriority="71"/><w:lsdException w:name="Colorful List Accent 6" w:uiPriority="72"/><w:lsdException w:name="Colorful Grid Accent 6" w:uiPriority="73"/><w:lsdException w:name="Subtle Emphasis" w:uiPriority="19" w:qFormat="1"/><w:lsdException w:name="Intense Emphasis" w:uiPriority="21" w:qFormat="1"/><w:lsdException w:name="Subtle Reference" w:uiPriority="31" w:qFormat="1"/><w:lsdException w:name="Intense Reference" w:uiPriority="32" w:qFormat="1"/><w:lsdException w:name="Book Title" w:uiPriority="33" w:qFormat="1"/><w:lsdException w:name="Bibliography" w:semiHidden="1" w:uiPriority="37" w:unhideWhenUsed="1"/><w:lsdException w:name="TOC Heading" w:semiHidden="1" w:uiPriority="39" w:unhideWhenUsed="1" w:qFormat="1"/><w:lsdException w:name="Plain Table 1" w:uiPriority="41"/><w:lsdException w:name="Plain Table 2" w:uiPriority="42"/><w:lsdException w:name="Plain Table 3" w:uiPriority="43"/><w:lsdException w:name="Plain Table 4" w:uiPriority="44"/><w:lsdException w:name="Plain Table 5" w:uiPriority="45"/><w:lsdException w:name="Grid Table Light" w:uiPriority="40"/><w:lsdException w:name="Grid Table 1 Light" w:uiPriority="46"/><w:lsdException w:name="Grid Table 2" w:uiPriority="47"/><w:lsdException w:name="Grid Table 3" w:uiPriority="48"/><w:lsdException w:name="Grid Table 4" w:uiPriority="49"/><w:lsdException w:name="Grid Table 5 Dark" w:uiPriority="50"/><w:lsdException w:name="Grid Table 6 Colorful" w:uiPriority="51"/><w:lsdException w:name="Grid Table 7 Colorful" w:uiPriority="52"/><w:lsdException w:name="Grid Table 1 Light Accent 1" w:uiPriority="46"/><w:lsdException w:name="Grid Table 2 Accent 1" w:uiPriority="47"/><w:lsdException w:name="Grid Table 3 Accent 1" w:uiPriority="48"/><w:lsdException w:name="Grid Table 4 Accent 1" w:uiPriority="49"/><w:lsdException w:name="Grid Table 5 Dark Accent 1" w:uiPriority="50"/><w:lsdException w:name="Grid Table 6 Colorful Accent 1" w:uiPriority="51"/><w:lsdException w:name="Grid Table 7 Colorful Accent 1" w:uiPriority="52"/><w:lsdException w:name="Grid Table 1 Light Accent 2" w:uiPriority="46"/><w:lsdException w:name="Grid Table 2 Accent 2" w:uiPriority="47"/><w:lsdException w:name="Grid Table 3 Accent 2" w:uiPriority="48"/><w:lsdException w:name="Grid Table 4 Accent 2" w:uiPriority="49"/><w:lsdException w:name="Grid Table 5 Dark Accent 2" w:uiPriority="50"/><w:lsdException w:name="Grid Table 6 Colorful Accent 2" w:uiPriority="51"/><w:lsdException w:name="Grid Table 7 Colorful Accent 2" w:uiPriority="52"/><w:lsdException w:name="Grid Table 1 Light Accent 3" w:uiPriority="46"/><w:lsdException w:name="Grid Table 2 Accent 3" w:uiPriority="47"/><w:lsdException w:name="Grid Table 3 Accent 3" w:uiPriority="48"/><w:lsdException w:name="Grid Table 4 Accent 3" w:uiPriority="49"/><w:lsdException w:name="Grid Table 5 Dark Accent 3" w:uiPriority="50"/><w:lsdException w:name="Grid Table 6 Colorful Accent 3" w:uiPriority="51"/><w:lsdException w:name="Grid Table 7 Colorful Accent 3" w:uiPriority="52"/><w:lsdException w:name="Grid Table 1 Light Accent 4" w:uiPriority="46"/><w:lsdException w:name="Grid Table 2 Accent 4" w:uiPriority="47"/><w:lsdException w:name="Grid Table 3 Accent 4" w:uiPriority="48"/><w:lsdException w:name="Grid Table 4 Accent 4" w:uiPriority="49"/><w:lsdException w:name="Grid Table 5 Dark Accent 4" w:uiPriority="50"/><w:lsdException w:name="Grid Table 6 Colorful Accent 4" w:uiPriority="51"/><w:lsdException w:name="Grid Table 7 Colorful Accent 4" w:uiPriority="52"/><w:lsdException w:name="Grid Table 1 Light Accent 5" w:uiPriority="46"/><w:lsdException w:name="Grid Table 2 Accent 5" w:uiPriority="47"/><w:lsdException w:name="Grid Table 3 Accent 5" w:uiPriority="48"/><w:lsdException w:name="Grid Table 4 Accent 5" w:uiPriority="49"/><w:lsdException w:name="Grid Table 5 Dark Accent 5" w:uiPriority="50"/><w:lsdException w:name="Grid Table 6 Colorful Accent 5" w:uiPriority="51"/><w:lsdException w:name="Grid Table 7 Colorful Accent 5" w:uiPriority="52"/><w:lsdException w:name="Grid Table 1 Light Accent 6" w:uiPriority="46"/><w:lsdException w:name="Grid Table 2 Accent 6" w:uiPriority="47"/><w:lsdException w:name="Grid Table 3 Accent 6" w:uiPriority="48"/><w:lsdException w:name="Grid Table 4 Accent 6" w:uiPriority="49"/><w:lsdException w:name="Grid Table 5 Dark Accent 6" w:uiPriority="50"/><w:lsdException w:name="Grid Table 6 Colorful Accent 6" w:uiPriority="51"/><w:lsdException w:name="Grid Table 7 Colorful Accent 6" w:uiPriority="52"/><w:lsdException w:name="List Table 1 Light" w:uiPriority="46"/><w:lsdException w:name="List Table 2" w:uiPriority="47"/><w:lsdException w:name="List Table 3" w:uiPriority="48"/><w:lsdException w:name="List Table 4" w:uiPriority="49"/><w:lsdException w:name="List Table 5 Dark" w:uiPriority="50"/><w:lsdException w:name="List Table 6 Colorful" w:uiPriority="51"/><w:lsdException w:name="List Table 7 Colorful" w:uiPriority="52"/><w:lsdException w:name="List Table 1 Light Accent 1" w:uiPriority="46"/><w:lsdException w:name="List Table 2 Accent 1" w:uiPriority="47"/><w:lsdException w:name="List Table 3 Accent 1" w:uiPriority="48"/><w:lsdException w:name="List Table 4 Accent 1" w:uiPriority="49"/><w:lsdException w:name="List Table 5 Dark Accent 1" w:uiPriority="50"/><w:lsdException w:name="List Table 6 Colorful Accent 1" w:uiPriority="51"/><w:lsdException w:name="List Table 7 Colorful Accent 1" w:uiPriority="52"/><w:lsdException w:name="List Table 1 Light Accent 2" w:uiPriority="46"/><w:lsdException w:name="List Table 2 Accent 2" w:uiPriority="47"/><w:lsdException w:name="List Table 3 Accent 2" w:uiPriority="48"/><w:lsdException w:name="List Table 4 Accent 2" w:uiPriority="49"/><w:lsdException w:name="List Table 5 Dark Accent 2" w:uiPriority="50"/><w:lsdException w:name="List Table 6 Colorful Accent 2" w:uiPriority="51"/><w:lsdException w:name="List Table 7 Colorful Accent 2" w:uiPriority="52"/><w:lsdException w:name="List Table 1 Light Accent 3" w:uiPriority="46"/><w:lsdException w:name="List Table 2 Accent 3" w:uiPriority="47"/><w:lsdException w:name="List Table 3 Accent 3" w:uiPriority="48"/><w:lsdException w:name="List Table 4 Accent 3" w:uiPriority="49"/><w:lsdException w:name="List Table 5 Dark Accent 3" w:uiPriority="50"/><w:lsdException w:name="List Table 6 Colorful Accent 3" w:uiPriority="51"/><w:lsdException w:name="List Table 7 Colorful Accent 3" w:uiPriority="52"/><w:lsdException w:name="List Table 1 Light Accent 4" w:uiPriority="46"/><w:lsdException w:name="List Table 2 Accent 4" w:uiPriority="47"/><w:lsdException w:name="List Table 3 Accent 4" w:uiPriority="48"/><w:lsdException w:name="List Table 4 Accent 4" w:uiPriority="49"/><w:lsdException w:name="List Table 5 Dark Accent 4" w:uiPriority="50"/><w:lsdException w:name="List Table 6 Colorful Accent 4" w:uiPriority="51"/><w:lsdException w:name="List Table 7 Colorful Accent 4" w:uiPriority="52"/><w:lsdException w:name="List Table 1 Light Accent 5" w:uiPriority="46"/><w:lsdException w:name="List Table 2 Accent 5" w:uiPriority="47"/><w:lsdException w:name="List Table 3 Accent 5" w:uiPriority="48"/><w:lsdException w:name="List Table 4 Accent 5" w:uiPriority="49"/><w:lsdException w:name="List Table 5 Dark Accent 5" w:uiPriority="50"/><w:lsdException w:name="List Table 6 Colorful Accent 5" w:uiPriority="51"/><w:lsdException w:name="List Table 7 Colorful Accent 5" w:uiPriority="52"/><w:lsdException w:name="List Table 1 Light Accent 6" w:uiPriority="46"/><w:lsdException w:name="List Table 2 Accent 6" w:uiPriority="47"/><w:lsdException w:name="List Table 3 Accent 6" w:uiPriority="48"/><w:lsdException w:name="List Table 4 Accent 6" w:uiPriority="49"/><w:lsdException w:name="List Table 5 Dark Accent 6" w:uiPriority="50"/><w:lsdException w:name="List Table 6 Colorful Accent 6" w:uiPriority="51"/><w:lsdException w:name="List Table 7 Colorful Accent 6" w:uiPriority="52"/><w:lsdException w:name="Mention" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Smart Hyperlink" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Hashtag" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Unresolved Mention" w:semiHidden="1" w:unhideWhenUsed="1"/><w:lsdException w:name="Smart Link" w:semiHidden="1" w:unhideWhenUsed="1"/></w:latentStyles><w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:qFormat/></w:style><w:style w:type="paragraph" w:styleId="ListParagraph"><w:name w:val="List Paragraph"/><w:aliases w:val="Text Paragraph"/><w:basedOn w:val="Normal"/><w:uiPriority w:val="34"/><w:qFormat/><w:rsid w:val="00B226D6"/><w:pPr><w:ind w:left="720"/><w:contextualSpacing/></w:pPr><w:rPr><w:rFonts w:ascii="Noto Sans" w:hAnsi="Noto Sans"/><w:color w:val="000000" w:themeColor="text1"/><w:sz w:val="22"/></w:rPr></w:style><w:style w:type="paragraph" w:styleId="Header"><w:name w:val="header"/><w:basedOn w:val="Normal"/><w:link w:val="HeaderChar"/><w:uiPriority w:val="99"/><w:unhideWhenUsed/><w:rsid w:val="004A2D9D"/><w:pPr><w:tabs><w:tab w:val="center" w:pos="4513"/><w:tab w:val="right" w:pos="9026"/></w:tabs><w:spacing w:after="0" w:line="240" w:lineRule="auto"/></w:pPr></w:style><w:style w:type="paragraph" w:styleId="Footer"><w:name w:val="footer"/><w:basedOn w:val="Normal"/><w:link w:val="FooterChar"/><w:uiPriority w:val="99"/><w:unhideWhenUsed/><w:rsid w:val="004A2D9D"/><w:pPr><w:tabs><w:tab w:val="center" w:pos="4513"/><w:tab w:val="right" w:pos="9026"/></w:tabs><w:spacing w:after="0" w:line="240" w:lineRule="auto"/></w:pPr></w:style><w:style w:type="paragraph" w:customStyle="1" w:styleId="SectionStart"><w:name w:val="Section Start"/><w:basedOn w:val="ListParagraph"/><w:next w:val="Normal"/><w:rsid w:val="00E95A81"/><w:pPr><w:keepNext/><w:pageBreakBefore/><w:numPr><w:numId w:val="1"/></w:numPr><w:pBdr><w:bottom w:val="single" w:sz="12" w:space="1" w:color="82BAFF"/></w:pBdr><w:tabs><w:tab w:val="left" w:pos="0"/></w:tabs><w:spacing w:after="380" w:line="240" w:lineRule="auto"/><w:ind w:left="0" w:firstLine="0"/><w:contextualSpacing w:val="0"/></w:pPr><w:rPr><w:rFonts w:cs="Noto Sans"/><w:color w:val="82BAFF"/><w:kern w:val="0"/><w:sz w:val="72"/><w:szCs w:val="22"/><w:lang w:val="es-PE"/><w14:ligatures w14:val="none"/></w:rPr></w:style><w:style w:type="paragraph" w:customStyle="1" w:styleId="Heading"><w:name w:val="Heading"/><w:next w:val="Normal"/><w:qFormat/><w:rsid w:val="00550D77"/><w:pPr><w:spacing w:after="0" w:line="240" w:lineRule="auto"/><w:outlineLvl w:val="0"/></w:pPr><w:rPr><w:rFonts w:ascii="Noto Sans" w:hAnsi="Noto Sans" w:cs="Noto Sans"/><w:b/><w:color w:val="000F47"/><w:sz w:val="36"/><w:szCs w:val="36"/></w:rPr></w:style><w:style w:type="paragraph" w:customStyle="1" w:styleId="TextBody"><w:name w:val="Text Body"/><w:basedOn w:val="Normal"/><w:qFormat/><w:rsid w:val="00B226D6"/><w:pPr><w:jc w:val="both"/><w:spacing w:before="0" w:after="120" w:line="240" w:lineRule="auto"/><w:ind w:left="0" w:hanging="0"/></w:pPr><w:rPr><w:rFonts w:cs="Noto Sans"/><w:szCs w:val="22"/><w:lang w:val="es-PE"/></w:rPr></w:style><w:style w:type="paragraph" w:customStyle="1" w:styleId="BulletBody">
  <w:name w:val="Bullet Body"/>
  <w:basedOn w:val="Normal"/>
  <w:qFormat/>
  <w:pPr>
    <w:numPr>
      <w:numId w:val="2"/>
    </w:numPr>
    <w:spacing w:before="0" w:after="120" w:line="240" w:lineRule="auto"/>
    <w:ind w:left="567" w:hanging="227"/>
    <w:jc w:val="both"/>
    <w:contextualSpacing w:val="0"/>
  </w:pPr>
  <w:rPr>
    <w:rFonts w:ascii="Noto Sans" w:hAnsi="Noto Sans"/>
    <w:sz w:val="22"/>
  </w:rPr>
</w:style><w:style w:type="paragraph" w:customStyle="1" w:styleId="IndentedBody">
  <w:name w:val="Indented Body"/>
  <w:basedOn w:val="Normal"/>
  <w:qFormat/>
  <w:pPr>
    <w:spacing w:before="0" w:after="120" w:line="240" w:lineRule="auto"/>
    <w:ind w:left="567" w:hanging="0"/>
    <w:jc w:val="both"/>
  </w:pPr>
  <w:rPr>
    <w:rFonts w:ascii="Noto Sans" w:hAnsi="Noto Sans"/>
    <w:sz w:val="22"/>
  </w:rPr>
</w:style></w:styles>`;

// ── numbering.xml ─────────────────────────────────────────────────────────────
// numId=1 (SectionStart decimal), numId=2 (» chevron), numId=3 (decimal list)
const NUMBERING_XML = `<?xml version='1.0' encoding='UTF-8' standalone='yes'?>
<w:numbering xmlns:wpc="http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas" xmlns:cx="http://schemas.microsoft.com/office/drawing/2014/chartex" xmlns:cx1="http://schemas.microsoft.com/office/drawing/2015/9/8/chartex" xmlns:cx2="http://schemas.microsoft.com/office/drawing/2015/10/21/chartex" xmlns:cx3="http://schemas.microsoft.com/office/drawing/2016/5/9/chartex" xmlns:cx4="http://schemas.microsoft.com/office/drawing/2016/5/10/chartex" xmlns:cx5="http://schemas.microsoft.com/office/drawing/2016/5/11/chartex" xmlns:cx6="http://schemas.microsoft.com/office/drawing/2016/5/12/chartex" xmlns:cx7="http://schemas.microsoft.com/office/drawing/2016/5/13/chartex" xmlns:cx8="http://schemas.microsoft.com/office/drawing/2016/5/14/chartex" xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" xmlns:aink="http://schemas.microsoft.com/office/drawing/2016/ink" xmlns:am3d="http://schemas.microsoft.com/office/drawing/2017/model3d" xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:oel="http://schemas.microsoft.com/office/2019/extlst" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:wp14="http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing" xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" xmlns:w10="urn:schemas-microsoft-com:office:word" xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml" xmlns:w15="http://schemas.microsoft.com/office/word/2012/wordml" xmlns:w16cex="http://schemas.microsoft.com/office/word/2018/wordml/cex" xmlns:w16cid="http://schemas.microsoft.com/office/word/2016/wordml/cid" xmlns:w16="http://schemas.microsoft.com/office/word/2018/wordml" xmlns:w16du="http://schemas.microsoft.com/office/word/2023/wordml/word16du" xmlns:w16sdtdh="http://schemas.microsoft.com/office/word/2020/wordml/sdtdatahash" xmlns:w16sdtfl="http://schemas.microsoft.com/office/word/2024/wordml/sdtformatlock" xmlns:w16se="http://schemas.microsoft.com/office/word/2015/wordml/symex" xmlns:wpg="http://schemas.microsoft.com/office/word/2010/wordprocessingGroup" xmlns:wpi="http://schemas.microsoft.com/office/word/2010/wordprocessingInk" xmlns:wne="http://schemas.microsoft.com/office/word/2006/wordml" xmlns:wps="http://schemas.microsoft.com/office/word/2010/wordprocessingShape"><w:abstractNum w:abstractNumId="8" w15:restartNumberingAfterBreak="0"><w:nsid w:val="5E331BD6"/><w:multiLevelType w:val="multilevel"/><w:tmpl w:val="E100370E"/><w:lvl w:ilvl="0"><w:start w:val="1"/><w:numFmt w:val="decimal"/><w:pStyle w:val="SectionStart"/><w:lvlText w:val="%1"/><w:lvlJc w:val="left"/><w:pPr><w:ind w:left="360" w:hanging="360"/></w:pPr><w:rPr><w:rFonts w:hint="default"/><w:b/><w:bCs/><w:color w:val="82BAFF"/><w:kern w:val="0"/><w:sz w:val="72"/><w14:ligatures w14:val="none"/></w:rPr></w:lvl><w:lvl w:ilvl="1"><w:start w:val="1"/><w:numFmt w:val="lowerLetter"/><w:lvlText w:val="%2."/><w:lvlJc w:val="left"/><w:pPr><w:ind w:left="1080" w:hanging="360"/></w:pPr><w:rPr><w:rFonts w:hint="default"/></w:rPr></w:lvl><w:lvl w:ilvl="2"><w:start w:val="1"/><w:numFmt w:val="lowerRoman"/><w:lvlText w:val="%3."/><w:lvlJc w:val="right"/><w:pPr><w:ind w:left="1800" w:hanging="180"/></w:pPr><w:rPr><w:rFonts w:hint="default"/></w:rPr></w:lvl><w:lvl w:ilvl="3"><w:start w:val="1"/><w:numFmt w:val="decimal"/><w:lvlText w:val="%4."/><w:lvlJc w:val="left"/><w:pPr><w:ind w:left="2520" w:hanging="360"/></w:pPr><w:rPr><w:rFonts w:hint="default"/></w:rPr></w:lvl><w:lvl w:ilvl="4"><w:start w:val="1"/><w:numFmt w:val="lowerLetter"/><w:lvlText w:val="%5."/><w:lvlJc w:val="left"/><w:pPr><w:ind w:left="3240" w:hanging="360"/></w:pPr><w:rPr><w:rFonts w:hint="default"/></w:rPr></w:lvl><w:lvl w:ilvl="5"><w:start w:val="1"/><w:numFmt w:val="lowerRoman"/><w:lvlText w:val="%6."/><w:lvlJc w:val="right"/><w:pPr><w:ind w:left="3960" w:hanging="180"/></w:pPr><w:rPr><w:rFonts w:hint="default"/></w:rPr></w:lvl><w:lvl w:ilvl="6"><w:start w:val="1"/><w:numFmt w:val="decimal"/><w:lvlText w:val="%7."/><w:lvlJc w:val="left"/><w:pPr><w:ind w:left="4680" w:hanging="360"/></w:pPr><w:rPr><w:rFonts w:hint="default"/></w:rPr></w:lvl><w:lvl w:ilvl="7"><w:start w:val="1"/><w:numFmt w:val="lowerLetter"/><w:lvlText w:val="%8."/><w:lvlJc w:val="left"/><w:pPr><w:ind w:left="5400" w:hanging="360"/></w:pPr><w:rPr><w:rFonts w:hint="default"/></w:rPr></w:lvl><w:lvl w:ilvl="8"><w:start w:val="1"/><w:numFmt w:val="lowerRoman"/><w:lvlText w:val="%9."/><w:lvlJc w:val="right"/><w:pPr><w:ind w:left="6120" w:hanging="180"/></w:pPr><w:rPr><w:rFonts w:hint="default"/></w:rPr></w:lvl></w:abstractNum><w:abstractNum w:abstractNumId="2" w15:restartNumberingAfterBreak="0"><w:nsid w:val="27826D54"/><w:multiLevelType w:val="hybridMultilevel"/><w:tmpl w:val="FCC6F90A"/><w:lvl w:ilvl="0" w:tplc="BCC8B988"><w:start w:val="1"/><w:numFmt w:val="bullet"/><w:pStyle w:val="TextBody"/><w:lvlText w:val="»"/><w:lvlJc w:val="left"/><w:pPr/><w:rPr><w:rFonts w:ascii="Noto Sans" w:hAnsi="Noto Sans" w:hint="default"/><w:b/><w:bCs/><w:color w:val="auto"/></w:rPr></w:lvl><w:lvl w:ilvl="1" w:tplc="08090003" w:tentative="1"><w:start w:val="1"/><w:numFmt w:val="bullet"/><w:lvlText w:val="o"/><w:lvlJc w:val="left"/><w:pPr><w:ind w:left="1440" w:hanging="360"/></w:pPr><w:rPr><w:rFonts w:ascii="Courier New" w:hAnsi="Courier New" w:cs="Courier New" w:hint="default"/></w:rPr></w:lvl><w:lvl w:ilvl="2" w:tplc="08090005" w:tentative="1"><w:start w:val="1"/><w:numFmt w:val="bullet"/><w:lvlText w:val=""/><w:lvlJc w:val="left"/><w:pPr><w:ind w:left="2160" w:hanging="360"/></w:pPr><w:rPr><w:rFonts w:ascii="Wingdings" w:hAnsi="Wingdings" w:hint="default"/></w:rPr></w:lvl><w:lvl w:ilvl="3" w:tplc="08090001" w:tentative="1"><w:start w:val="1"/><w:numFmt w:val="bullet"/><w:lvlText w:val=""/><w:lvlJc w:val="left"/><w:pPr><w:ind w:left="2880" w:hanging="360"/></w:pPr><w:rPr><w:rFonts w:ascii="Symbol" w:hAnsi="Symbol" w:hint="default"/></w:rPr></w:lvl><w:lvl w:ilvl="4" w:tplc="08090003" w:tentative="1"><w:start w:val="1"/><w:numFmt w:val="bullet"/><w:lvlText w:val="o"/><w:lvlJc w:val="left"/><w:pPr><w:ind w:left="3600" w:hanging="360"/></w:pPr><w:rPr><w:rFonts w:ascii="Courier New" w:hAnsi="Courier New" w:cs="Courier New" w:hint="default"/></w:rPr></w:lvl><w:lvl w:ilvl="5" w:tplc="08090005" w:tentative="1"><w:start w:val="1"/><w:numFmt w:val="bullet"/><w:lvlText w:val=""/><w:lvlJc w:val="left"/><w:pPr><w:ind w:left="4320" w:hanging="360"/></w:pPr><w:rPr><w:rFonts w:ascii="Wingdings" w:hAnsi="Wingdings" w:hint="default"/></w:rPr></w:lvl><w:lvl w:ilvl="6" w:tplc="08090001" w:tentative="1"><w:start w:val="1"/><w:numFmt w:val="bullet"/><w:lvlText w:val=""/><w:lvlJc w:val="left"/><w:pPr><w:ind w:left="5040" w:hanging="360"/></w:pPr><w:rPr><w:rFonts w:ascii="Symbol" w:hAnsi="Symbol" w:hint="default"/></w:rPr></w:lvl><w:lvl w:ilvl="7" w:tplc="08090003" w:tentative="1"><w:start w:val="1"/><w:numFmt w:val="bullet"/><w:lvlText w:val="o"/><w:lvlJc w:val="left"/><w:pPr><w:ind w:left="5760" w:hanging="360"/></w:pPr><w:rPr><w:rFonts w:ascii="Courier New" w:hAnsi="Courier New" w:cs="Courier New" w:hint="default"/></w:rPr></w:lvl><w:lvl w:ilvl="8" w:tplc="08090005" w:tentative="1"><w:start w:val="1"/><w:numFmt w:val="bullet"/><w:lvlText w:val=""/><w:lvlJc w:val="left"/><w:pPr><w:ind w:left="6480" w:hanging="360"/></w:pPr><w:rPr><w:rFonts w:ascii="Wingdings" w:hAnsi="Wingdings" w:hint="default"/></w:rPr></w:lvl></w:abstractNum><w:num w:numId="1"><w:abstractNumId w:val="8"/></w:num><w:num w:numId="2"><w:abstractNumId w:val="2"/></w:num></w:numbering>`;

// ── numbering.xml.rels ────────────────────────────────────────────────────────
// Maps rId1/rId2 to bullet images image1.png and image2.png
const NUMBERING_RELS_XML = `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/image2.png"/><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/image1.png"/></Relationships>`;

// ── Bullet glyph images (base64 PNG) ─────────────────────────────────────────
// image1.png → right-pointing double chevron (»), used by numId=2
// image2.png → small dot glyph, referenced by numPicBullet definition
const IMAGE1_B64 = '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AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADgs/sH6ZGu9PJXyeMAAAAASUVORK5CYII=';
const IMAGE2_B64 = 'iVBORw0KGgoAAAANSUhEUgAAAA8AAAAPCAMAAAAMCGV4AAAAAXNSR0IArs4c6QAAAMxQTFRF//fYwMDA/9AT/9Qn/9g7/99iAAAAUlH/eHj/jIv/n57/xcX///Cw//PEBQT/LCv///TE//jY/++w//PF/+iJ//Cx/9ra/7+//7Gx/6Oj/4eH/3l5/9c7/+Bi/8/P/7Oz/6am/5iX/8TE/6in/5qa/4yM/3Fw/2Ji/62t/5GS/4SD/3V2/1pa/0xM/6Ki/4aG/3h3/2pq/05O/0FA/5aW/3p6/21t/15f/9AUn5//xsX/eXf/i4v//+iK/+eJeXj/eHf/UlL/LCr/Kyv/WLUWNgAAAAxjbVBQSkNtcDA3MTICAQEGiroUzgAAAAJ0Uk5T/wDltzBKAAAAgklEQVQYlV3PPQuCAAAEUB/UmGPg0tDUFA1GRj8/ISpwa2pqiHALBJUkaSj7uu3BDXcEP9G533xMlAvVhacXe1GeZDqDJOu5fjlstdd3n7BWCMSwj+SLQ1MITMFRRXy3MQGnOLXcUhqDS5yC0gjnr71DUMzXkp3Z5rV/oFrdZMr/Pw/btSokYKUFFgAAAABJRU5ErkJggg==';

// =============================================================================
// SECTION 2 — DOCUMENT CONSTANTS
// =============================================================================

const FONT       = 'Noto Sans';
const FONT_MARSH = 'Marsh Serif';   // cover title only

// Sizes in half-points (docx internal unit). pt × 2.
const SZ_10 = 21;   // 10.5pt — footer
const SZ_11 = 22;   // 11pt   — body text
const SZ_18 = 36;   // 18pt   — companyName on cover
const SZ_32 = 64;   // 32pt   — cover title

// Colors (hex without #)
const WHITE = 'FFFFFF';
const NAVY  = '000F47';
const BLACK = '000000';

// Unit converters
const cm  = (n) => Math.round(n * 567);    // cm → DXA (twips)
const EMU = (n) => Math.round(n * 360000); // cm → EMU

// Page size — Letter
const PAGE_W = 12240;
const PAGE_H  = 15840;

// Zero spacing shorthand
const SP_ZERO = { before: 0, after: 0, line: 240, lineRule: LineRuleType.AUTO };

// =============================================================================
// SECTION 3 — HELPERS
// =============================================================================

// Load logo from imgs/logo_sky.png — same path used by build_template.js
// and build_template_siniestros.js. Returns null if file not found (logo
// paragraph is skipped gracefully).
function getLogoBuffer() {
    try { return fs.readFileSync('imgs/logo_sky.png'); } catch (_) { return null; }
}

// Standard text run — Noto Sans 11pt black by default
function r(text, opts = {}) {
    return new TextRun({
        text,
        font:  opts.font  ?? FONT,
        size:  opts.size  ?? SZ_11,
        bold:  opts.bold  ?? false,
        color: opts.color ?? BLACK,
        caps:  opts.caps  ?? false,
    });
}
// White run (cover page text)
function rW(text, opts = {})  { return r(text, { ...opts, color: WHITE }); }
// White bold run (cover page title)
function rWB(text, opts = {}) { return r(text, { ...opts, color: WHITE, bold: true }); }

// Empty paragraph using NBSP ( ) with explicit Noto Sans 11pt.
// Empty string ('') causes Word to fall back to Times New Roman — NBSP prevents this.
function pEmpty(color = BLACK) {
    return new Paragraph({
        children: [new TextRun({ text: '\u00A0', font: FONT, size: SZ_11, color })],
        spacing:  SP_ZERO,
    });
}

// Navy full-page background shape — anchored behind all content.
// Injected as raw XML in post-process because the docx library does not
// support anchored drawing shapes natively.
function makeBackgroundShapeXml() {
    return '<w:drawing>'
        + '<wp:anchor distT="0" distB="0" distL="114300" distR="114300"'
        + ' simplePos="0" relativeHeight="251659264" behindDoc="1"'
        + ' locked="0" layoutInCell="1" allowOverlap="1"'
        + ' wp14:anchorId="32ADB19F" wp14:editId="3EC6DC68">'
        + '<wp:simplePos x="0" y="0"/>'
        + '<wp:positionH relativeFrom="page"><wp:align>center</wp:align></wp:positionH>'
        + '<wp:positionV relativeFrom="page"><wp:align>center</wp:align></wp:positionV>'
        + `<wp:extent cx="${EMU(21.59)}" cy="${EMU(27.94)}"/>`
        + '<wp:effectExtent l="0" t="0" r="0" b="0"/>'
        + '<wp:wrapNone/>'
        + '<wp:docPr id="9001" name="Rectangle Background"/>'
        + '<wp:cNvGraphicFramePr/>'
        + '<a:graphic>'
        + '<a:graphicData uri="http://schemas.microsoft.com/office/word/2010/wordprocessingShape">'
        + '<wps:wsp><wps:cNvSpPr/>'
        + '<wps:spPr>'
        + `<a:xfrm><a:off x="0" y="0"/><a:ext cx="${EMU(21.59)}" cy="${EMU(27.94)}"/></a:xfrm>`
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
        + '</wps:bodyPr></wps:wsp></a:graphicData></a:graphic></wp:anchor></w:drawing>';
}

// =============================================================================
// SECTION 4 — COVER (Section 1)
// Navy background, logo, title "GARANTÍAS PARTICULARES", {companyName}
// =============================================================================

function buildCoverChildren() {
    const logoBuffer = getLogoBuffer();
    const children   = [];

    // First paragraph holds the background shape marker text.
    // The marker is replaced with the actual shape XML in the post-process step.
    children.push(new Paragraph({
        children: [new TextRun({ text: '__BACKGROUND_SHAPE__', size: 2, color: WHITE })],
        spacing:  SP_ZERO,
    }));

    // Two empty lines before logo
    children.push(pEmpty(WHITE));
    children.push(pEmpty(WHITE));

    // Logo — 201×44px (5.31cm × 1.16cm at 96dpi), left-aligned
    if (logoBuffer) {
        children.push(new Paragraph({
            children: [new ImageRun({
                type: 'png', data: logoBuffer,
                transformation: { width: 201, height: 44 },
            })],
            alignment: AlignmentType.LEFT,
            spacing:   SP_ZERO,
        }));
    }

    // 10 empty lines after logo (vertical centering on cover)
    for (let i = 0; i < 10; i++) children.push(pEmpty(WHITE));

    // Title: "GARANTÍAS PARTICULARES" in Marsh Serif 32pt bold white allCaps
    children.push(new Paragraph({
        children:  [rWB('Garantías Particulares', { font: FONT_MARSH, size: SZ_32, caps: true })],
        alignment: AlignmentType.LEFT,
        spacing:   SP_ZERO,
    }));

    // 6 empty lines after title
    for (let i = 0; i < 6; i++) children.push(pEmpty(WHITE));

    // {companyName} placeholder — Noto Sans 18pt white.
    // Stored as a single run so python-docx can find and replace it reliably.
    children.push(new Paragraph({
        children:  [rW('{{companyName}}', { size: SZ_18 })],
        alignment: AlignmentType.LEFT,
        spacing:   SP_ZERO,
    }));

    return children;
}

// =============================================================================
// SECTION 5 — CONTENT SECTION (Section 2)
// Contains a single placeholder paragraph that python-docx removes before
// rebuilding all content programmatically using the injected styles/numbering.
// Footer: "Página X de Y" right-aligned, page count restarts from 1.
// =============================================================================

function buildContentFooter() {
    return new Footer({
        children: [new Paragraph({
            children: [
                r('Página ', { size: SZ_10 }),
                new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: SZ_10, bold: true }),
                r(' de ', { size: SZ_10 }),
                new TextRun({ children: [PageNumber.TOTAL_PAGES], font: FONT, size: SZ_10, bold: true }),
            ],
            alignment: AlignmentType.RIGHT,
            spacing:   SP_ZERO,
        })],
    });
}

function buildContentChildren() {
    // Single NBSP paragraph — serves as the section boundary that python-docx
    // detects via the w:sectPr in the preceding paragraph's pPr.
    // All content after this paragraph is cleared and rebuilt at runtime.
    return [new Paragraph({
        children: [new TextRun({ text: '\u00A0', font: FONT, size: SZ_11 })],
        spacing:  SP_ZERO,
    })];
}

// =============================================================================
// SECTION 6 — MAIN: assemble document, post-process ZIP, write file
// =============================================================================

async function buildDocument() {

    // Build document structure with docx library (cover + empty content section)
    const doc = new Document({
        // No NUMBERING_CONFIG here — numbering is injected via the clean
        // numbering.xml embedded above, replacing the auto-generated one.
        sections: [
            // Cover section — navy background, logo, title, companyName
            {
                properties: {
                    type: SectionType.NEXT_PAGE,
                    page: {
                        size:   { width: PAGE_W, height: PAGE_H },
                        margin: { top: cm(2.54), bottom: cm(2.54), left: cm(1.9), right: cm(1.9) },
                    },
                },
                children: buildCoverChildren(),
            },
            // Content section — placeholder only, rebuilt by python-docx at runtime
            {
                properties: {
                    type: SectionType.NEXT_PAGE,
                    page: {
                        size:        { width: PAGE_W, height: PAGE_H },
                        margin:      { top: cm(2.54), bottom: cm(2.34), left: cm(1.9), right: cm(1.9) },
                        pageNumbers: { start: 1, formatType: NumberFormat.DECIMAL },
                    },
                },
                headers:  { default: new Header({ children: [new Paragraph({ children: [] })] }) },
                footers:  { default: buildContentFooter() },
                children: buildContentChildren(),
            },
        ],
    });

    const AdmZip    = require('adm-zip');
    const zipBuffer = await Packer.toBuffer(doc);
    const zip       = new AdmZip(zipBuffer);

    // ── Inject navy background shape into cover paragraph ─────────────────────
    // The docx library cannot produce anchored drawing shapes natively.
    // We replace the marker text '__BACKGROUND_SHAPE__' with the raw wps:wsp XML.
    // The xmlns:a namespace must be declared at the w:document root — not inline
    // on child elements — to avoid Word rejecting the file on open.
    let docXml = zip.readAsText('word/document.xml');

    const NS_A      = 'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"';
    const wDocStart = docXml.indexOf('<w:document ');
    const rootEnd   = docXml.indexOf('>', wDocStart);
    if (!docXml.slice(wDocStart, rootEnd + 1).includes(NS_A)) {
        docXml = docXml.slice(0, rootEnd) + ' ' + NS_A + docXml.slice(rootEnd);
    }

    docXml = docXml.replace(
        new RegExp(
            '<w:r\\b[^>]*>(?:<w:rPr>[^<]*(?:<[^/][^>]*/>|<[^>]+>[^<]*<\\/[^>]+>)*<\\/w:rPr>)?'
            + '<w:t[^>]*>__BACKGROUND_SHAPE__<\\/w:t><\\/w:r>'
        ),
        makeBackgroundShapeXml()
    );
    zip.updateFile('word/document.xml', Buffer.from(docXml, 'utf8'));

    // ── Replace auto-generated XML assets with clean versions ─────────────────
    // styles.xml: 7 styles (Normal, ListParagraph, Header, Footer,
    //             SectionStart, Heading, TextBody)
    zip.updateFile('word/styles.xml', Buffer.from(STYLES_XML, 'utf8'));

    // numbering.xml: 3 numIds only
    //   numId=1 → decimal (SectionStart internal counter)
    //   numId=2 → » chevron bullet, Noto Sans, left=227 hanging=227
    //   numId=3 → decimal list %1., Noto Sans, left=227 hanging=227
    zip.updateFile('word/numbering.xml', Buffer.from(NUMBERING_XML, 'utf8'));

    // numbering.xml.rels: maps rId1/rId2 to bullet glyph images
    try { zip.updateFile('word/_rels/numbering.xml.rels', Buffer.from(NUMBERING_RELS_XML, 'utf8')); }
    catch (_) { zip.addFile('word/_rels/numbering.xml.rels', Buffer.from(NUMBERING_RELS_XML, 'utf8')); }

    // Bullet glyph images — required by numPicBullet references in numbering.xml
    const img1 = Buffer.from(IMAGE1_B64, 'base64');
    const img2 = Buffer.from(IMAGE2_B64, 'base64');
    try { zip.updateFile('word/media/image1.png', img1); } catch (_) { zip.addFile('word/media/image1.png', img1); }
    try { zip.updateFile('word/media/image2.png', img2); } catch (_) { zip.addFile('word/media/image2.png', img2); }

    // ── Write final file ──────────────────────────────────────────────────────
    fs.writeFileSync('template_garantias.docx', zip.toBuffer());
    console.log('✓ Written: template_garantias.docx');
    console.log('  Styles (9):    Normal, ListParagraph, Header, Footer, SectionStart, Heading, TextBody, BulletBody, IndentedBody');
    console.log('  Numbering (2): numId=1 (SectionStart), numId=2 (» chevron bullet)');
}

buildDocument().catch(err => { console.error('Build failed:', err); process.exit(1); });
