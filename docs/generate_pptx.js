const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const {
  FaRobot, FaBrain, FaChartLine, FaCogs, FaShieldAlt,
  FaUsers, FaLightbulb, FaRocket, FaCheckCircle, FaStar,
  FaLayerGroup, FaNetworkWired, FaDatabase, FaCode,
  FaClipboardList, FaBullseye, FaArrowRight
} = require("react-icons/fa");

// ─────────────────────────────────────────────
// Color Palette — Midnight Tech
// ─────────────────────────────────────────────
const C = {
  bgDark:    "0A1628",
  bgCard:    "1E293B",
  bgMid:     "0F1D32",
  primary:   "0EA5E9",  // electric blue
  accent:    "06B6D4",  // cyan
  accent2:   "8B5CF6",  // purple
  accent3:   "10B981",  // emerald
  accent4:   "F59E0B",  // amber
  accent5:   "EF4444",  // red
  white:     "FFFFFF",
  textLight: "CBD5E1",
  textMuted: "64748B",
  textDim:   "475569",
  lineColor: "334155",
  starGold:  "FBBF24",
};

// ─────────────────────────────────────────────
// Icon helper
// ─────────────────────────────────────────────
function renderIconSvg(Icon, color, size = 256) {
  return ReactDOMServer.renderToStaticMarkup(
    React.createElement(Icon, { color, size: String(size) })
  );
}
async function iconB64(Icon, color, size = 256) {
  const svg = renderIconSvg(Icon, color, size);
  const buf = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + buf.toString("base64");
}

// Helpers
const mkShadow = () => ({ type: "outer", blur: 6, offset: 2, angle: 135, color: "000000", opacity: 0.3 });

// ─────────────────────────────────────────────
// Main
// ─────────────────────────────────────────────
async function main() {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_16x9";
  pres.author = "Lysander";
  pres.title = "AI Team System Report";

  // Pre-render icons
  const icons = {
    robot:    await iconB64(FaRobot,        "#" + C.primary),
    brain:    await iconB64(FaBrain,         "#" + C.accent),
    chart:    await iconB64(FaChartLine,     "#" + C.accent3),
    cogs:     await iconB64(FaCogs,          "#" + C.primary),
    shield:   await iconB64(FaShieldAlt,     "#" + C.accent2),
    users:    await iconB64(FaUsers,         "#" + C.primary),
    bulb:     await iconB64(FaLightbulb,     "#" + C.accent4),
    rocket:   await iconB64(FaRocket,        "#" + C.accent),
    check:    await iconB64(FaCheckCircle,   "#" + C.accent3),
    star:     await iconB64(FaStar,          "#" + C.starGold),
    layers:   await iconB64(FaLayerGroup,    "#" + C.accent2),
    network:  await iconB64(FaNetworkWired,  "#" + C.primary),
    db:       await iconB64(FaDatabase,      "#" + C.accent),
    code:     await iconB64(FaCode,          "#" + C.accent3),
    clipboard:await iconB64(FaClipboardList, "#" + C.accent4),
    target:   await iconB64(FaBullseye,      "#" + C.accent5),
    arrow:    await iconB64(FaArrowRight,    "#" + C.primary),
  };

  // ═══════════════════════════════════════════
  // SLIDE 1 — Cover
  // ═══════════════════════════════════════════
  {
    const s = pres.addSlide();
    s.background = { color: C.bgDark };
    // Top accent line
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.04, fill: { color: C.primary } });
    // Icon
    s.addImage({ data: icons.brain, x: 4.5, y: 0.7, w: 1, h: 1 });
    // Title
    s.addText("AI \u56E2\u961F\u534F\u4F5C\u4F53\u7CFB \u00D7 Obsidian \u7B2C\u4E8C\u5927\u8111", {
      x: 0.5, y: 1.9, w: 9, h: 1, fontSize: 36, fontFace: "Calibri",
      color: C.white, bold: true, align: "center", margin: 0
    });
    s.addText("\u6784\u5EFA AI Native \u7EC4\u7EC7\u7684\u5DE5\u7A0B\u5B9E\u8DF5\u4E0E\u6218\u7565\u4EF7\u503C\u8BC4\u4F30", {
      x: 0.5, y: 2.85, w: 9, h: 0.6, fontSize: 18, fontFace: "Calibri",
      color: C.textLight, align: "center", margin: 0
    });
    // Separator line
    s.addShape(pres.shapes.LINE, { x: 3.5, y: 3.6, w: 3, h: 0, line: { color: C.primary, width: 1.5 } });
    // Meta info
    s.addText([
      { text: "\u5206\u6790\u6846\u67B6\uFF1AMcKinsey Rewired  |  Gartner Hype Cycle  |  Deloitte Agentic AI Strategy", options: { breakLine: true, fontSize: 12, color: C.textMuted } },
      { text: "\u7F16\u5236\u56E2\u961F\uFF1AGraphify \u667A\u56CA\u56E2 + \u5185\u5BB9\u8FD0\u8425\u56E2\u961F  |  2026\u5E744\u6708", options: { fontSize: 12, color: C.textMuted } }
    ], { x: 0.5, y: 4.1, w: 9, h: 0.9, align: "center" });
    // Bottom bar
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 5.325, w: 10, h: 0.3, fill: { color: C.primary, transparency: 15 } });
  }

  // ═══════════════════════════════════════════
  // SLIDE 2 — Executive Summary
  // ═══════════════════════════════════════════
  {
    const s = pres.addSlide();
    s.background = { color: C.bgDark };
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.04, fill: { color: C.primary } });
    s.addText("EXECUTIVE SUMMARY", {
      x: 0.6, y: 0.25, w: 5, h: 0.5, fontSize: 11, fontFace: "Calibri",
      color: C.primary, bold: true, charSpacing: 4, margin: 0
    });
    s.addText("\u6838\u5FC3\u7ED3\u8BBA", {
      x: 0.6, y: 0.65, w: 8, h: 0.55, fontSize: 28, fontFace: "Calibri",
      color: C.white, bold: true, margin: 0
    });

    // Three conclusion cards
    const cards = [
      { icon: icons.chart,  title: "Gartner \u5B9A\u4F4D",  body: "\u5DF2\u8DF3\u8FC7\u6982\u5FF5\u9A8C\u8BC1\u9636\u6BB5\uFF0C\u8FDB\u5165\u53EF\u5DE5\u7A0B\u5316\u843D\u5730\u7684\u5B9E\u8DF5\u533A\u95F4", color: C.primary },
      { icon: icons.check,  title: "McKinsey \u8BC4\u4F30",  body: "\u5728\u201CAI \u4EF7\u503C\u6700\u5F3A\u9884\u6D4B\u56E0\u5B50\u201D\u5DE5\u4F5C\u6D41\u91CD\u6784\u7EF4\u5EA6\u5F97\u5206\u6700\u9AD8", color: C.accent3 },
      { icon: icons.rocket,  title: "Deloitte \u5BF9\u6807",  body: "\u4F53\u7CFB\u6210\u719F\u5EA6\u5DF2\u8D85\u8FC7 89% \u7684\u53D7\u8BBF\u4F01\u4E1A", color: C.accent },
    ];
    cards.forEach((c, i) => {
      const y = 1.5 + i * 1.2;
      s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y, w: 8.8, h: 1.0, fill: { color: C.bgCard }, shadow: mkShadow() });
      s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y, w: 0.06, h: 1.0, fill: { color: c.color } });
      s.addImage({ data: c.icon, x: 1.0, y: y + 0.22, w: 0.55, h: 0.55 });
      s.addText(c.title, { x: 1.8, y: y + 0.08, w: 7, h: 0.4, fontSize: 16, fontFace: "Calibri", color: C.white, bold: true, margin: 0 });
      s.addText(c.body, { x: 1.8, y: y + 0.48, w: 7, h: 0.4, fontSize: 13, fontFace: "Calibri", color: C.textLight, margin: 0 });
    });

    // Bottom highlight
    s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: 4.95, w: 8.8, h: 0.45, fill: { color: C.primary, transparency: 85 } });
    s.addText("\u2601\uFE0F  29 \u4F4D AI \u4E13\u5BB6  |  6 \u4E2A\u804C\u80FD\u56E2\u961F  |  4 \u7EA7\u51B3\u7B56\u4F53\u7CFB  |  \u4EE3\u7801\u5316\u6CBB\u7406  |  2 \u5206\u949F\u63A5\u5165", {
      x: 0.8, y: 4.97, w: 8.4, h: 0.4, fontSize: 12, fontFace: "Calibri", color: C.textLight, align: "center", margin: 0
    });
  }

  // ═══════════════════════════════════════════
  // SLIDE 3 — Market Data
  // ═══════════════════════════════════════════
  {
    const s = pres.addSlide();
    s.background = { color: C.bgDark };
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.04, fill: { color: C.primary } });
    s.addText("CHAPTER 01", { x: 0.6, y: 0.25, w: 3, h: 0.4, fontSize: 11, fontFace: "Calibri", color: C.primary, bold: true, charSpacing: 4, margin: 0 });
    s.addText("\u884C\u4E1A\u5750\u6807\uFF1A\u5168\u7403 AI Agent \u5E02\u573A\u683C\u5C40", { x: 0.6, y: 0.6, w: 8, h: 0.55, fontSize: 26, fontFace: "Calibri", color: C.white, bold: true, margin: 0 });

    // Bar chart
    s.addChart(pres.charts.BAR, [{
      name: "\u5E02\u573A\u89C4\u6A21 (\u5341\u4EBF\u7F8E\u5143)",
      labels: ["2025", "2026E", "2027E", "2028E", "2030E"],
      values: [7.84, 11.5, 16.8, 24.6, 52.62]
    }], {
      x: 0.5, y: 1.35, w: 5.2, h: 3.3, barDir: "col",
      chartColors: [C.primary],
      chartArea: { fill: { color: C.bgCard }, roundedCorners: true },
      catAxisLabelColor: C.textMuted, catAxisLabelFontSize: 10,
      valAxisLabelColor: C.textMuted, valAxisLabelFontSize: 9,
      valGridLine: { color: C.lineColor, size: 0.5 },
      catGridLine: { style: "none" },
      showValue: true, dataLabelColor: C.white, dataLabelFontSize: 10,
      dataLabelPosition: "outEnd",
      showLegend: false,
      showTitle: true, title: "AI Agent \u5E02\u573A\u89C4\u6A21\u9884\u6D4B", titleColor: C.textLight, titleFontSize: 12,
    });
    s.addText("CAGR 46.3%", {
      x: 3.5, y: 4.7, w: 2, h: 0.4, fontSize: 14, fontFace: "Calibri", color: C.accent4, bold: true, align: "center", margin: 0
    });

    // Key metrics on right side
    const metrics = [
      { label: "\u4F01\u4E1A\u5E94\u7528\u5D4C\u5165 Agent", val: "5%\u21924 0%", sub: "Gartner 2025\u21922026 \u9884\u6D4B" },
      { label: "\u751F\u4EA7\u73AF\u5883\u4F7F\u7528 Agent", val: "11%", sub: "Deloitte 2026 \u8C03\u67E5" },
      { label: "Agent \u9879\u76EE\u53D6\u6D88\u7387", val: "40%+", sub: "Gartner 2027 \u9884\u6D4B" },
      { label: "\u771F\u5B9E Agent \u4F9B\u5E94\u5546", val: "\u2248130\u5BB6", sub: "vs \u6570\u5343\u5BB6 Agent Washing" },
    ];
    metrics.forEach((m, i) => {
      const y = 1.4 + i * 1.0;
      s.addShape(pres.shapes.RECTANGLE, { x: 6.1, y, w: 3.5, h: 0.85, fill: { color: C.bgCard }, shadow: mkShadow() });
      s.addText(m.val, { x: 6.3, y: y + 0.05, w: 3.1, h: 0.35, fontSize: 20, fontFace: "Calibri", color: C.primary, bold: true, margin: 0 });
      s.addText(m.label, { x: 6.3, y: y + 0.35, w: 3.1, h: 0.25, fontSize: 11, fontFace: "Calibri", color: C.white, margin: 0 });
      s.addText(m.sub, { x: 6.3, y: y + 0.58, w: 3.1, h: 0.2, fontSize: 9, fontFace: "Calibri", color: C.textMuted, margin: 0 });
    });

    s.addText("\u6570\u636E\u6765\u6E90: Gartner, Deloitte, OneReach.ai", { x: 0.5, y: 5.2, w: 9, h: 0.3, fontSize: 9, fontFace: "Calibri", color: C.textDim, margin: 0 });
  }

  // ═══════════════════════════════════════════
  // SLIDE 4 — Maturity Ladder
  // ═══════════════════════════════════════════
  {
    const s = pres.addSlide();
    s.background = { color: C.bgDark };
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.04, fill: { color: C.primary } });
    s.addText("CHAPTER 01", { x: 0.6, y: 0.25, w: 3, h: 0.4, fontSize: 11, fontFace: "Calibri", color: C.primary, bold: true, charSpacing: 4, margin: 0 });
    s.addText("AI Agent \u6210\u719F\u5EA6\u9636\u68AF\uFF1A\u6211\u4EEC\u5728\u54EA", { x: 0.6, y: 0.6, w: 8, h: 0.55, fontSize: 26, fontFace: "Calibri", color: C.white, bold: true, margin: 0 });

    const levels = [
      { lv: "Level 5", name: "\u81EA\u4E3B AI \u7EC4\u7EC7",   desc: "\u7406\u8BBA\u63A2\u7D22 | Mechanize \u7B49",    pct: "< 0.1%", color: C.textDim, barW: 1.5, highlight: false },
      { lv: "Level 4", name: "\u591A Agent \u7F16\u6392",       desc: "Cognition/Devin 25% PRs",     pct: "< 1%",   color: C.accent2, barW: 2.5, highlight: false },
      { lv: "Level 3", name: "Agent \u4F53\u7CFB\u5316",       desc: "\u51B3\u7B56\u4EE3\u7801\u5316 + \u77E5\u8BC6\u6C89\u6DC0",  pct: "\u2248 2%",  color: C.primary, barW: 4.0, highlight: true },
      { lv: "Level 2", name: "\u56E2\u961F\u5171\u4EAB Prompt", desc: "Prompt \u5E93 / \u6A21\u677F\u5316",        pct: "\u2248 8%",  color: C.accent, barW: 5.5, highlight: false },
      { lv: "Level 1", name: "\u4E2A\u4EBA\u4F7F\u7528 AI",    desc: "ChatGPT / Copilot",           pct: "90%",    color: C.textMuted, barW: 8.0, highlight: false },
    ];
    levels.forEach((l, i) => {
      const y = 1.45 + i * 0.82;
      // Level label
      s.addText(l.lv, { x: 0.6, y, w: 0.9, h: 0.35, fontSize: 11, fontFace: "Calibri", color: l.highlight ? C.primary : C.textMuted, bold: true, margin: 0 });
      // Bar
      s.addShape(pres.shapes.RECTANGLE, { x: 1.6, y: y + 0.02, w: l.barW, h: 0.3, fill: { color: l.highlight ? C.primary : l.color, transparency: l.highlight ? 0 : 60 } });
      // Name
      s.addText(l.name, { x: 1.8, y: y - 0.02, w: 3, h: 0.35, fontSize: 13, fontFace: "Calibri", color: C.white, bold: l.highlight, margin: 0 });
      // Description
      s.addText(l.desc, { x: 1.8, y: y + 0.28, w: 4, h: 0.3, fontSize: 10, fontFace: "Calibri", color: C.textMuted, margin: 0 });
      // Percentage
      s.addText(l.pct, { x: 8.5, y, w: 1.2, h: 0.35, fontSize: 12, fontFace: "Calibri", color: l.highlight ? C.primary : C.textMuted, bold: l.highlight, align: "right", margin: 0 });

      if (l.highlight) {
        s.addText("\u2605 \u672C\u9879\u76EE\u5F53\u524D\u4F4D\u7F6E", { x: 6.0, y: y + 0.0, w: 2.3, h: 0.35, fontSize: 11, fontFace: "Calibri", color: C.starGold, bold: true, margin: 0 });
      }
    });

    // Bottom insight
    s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: 5.0, w: 8.8, h: 0.45, fill: { color: C.primary, transparency: 85 } });
    s.addText("\u5168\u7403\u4F01\u4E1A\u524D 2% \u7684\u5148\u884C\u8005\u7FA4\u4F53  |  Gartner: \u4EC5\u7EA6 130 \u5BB6\u4F9B\u5E94\u5546\u5177\u5907\u771F\u6B63 Agent \u80FD\u529B", {
      x: 0.8, y: 5.03, w: 8.4, h: 0.4, fontSize: 12, fontFace: "Calibri", color: C.textLight, align: "center", margin: 0
    });
  }

  // ═══════════════════════════════════════════
  // SLIDE 5 — System Architecture: 4-Layer Org
  // ═══════════════════════════════════════════
  {
    const s = pres.addSlide();
    s.background = { color: C.bgDark };
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.04, fill: { color: C.primary } });
    s.addText("CHAPTER 02", { x: 0.6, y: 0.25, w: 3, h: 0.4, fontSize: 11, fontFace: "Calibri", color: C.primary, bold: true, charSpacing: 4, margin: 0 });
    s.addText("\u56DB\u5C42\u7EC4\u7EC7\u67B6\u6784", { x: 0.6, y: 0.6, w: 8, h: 0.55, fontSize: 26, fontFace: "Calibri", color: C.white, bold: true, margin: 0 });

    // Layer 1 - President
    s.addShape(pres.shapes.RECTANGLE, { x: 3.0, y: 1.3, w: 4.0, h: 0.7, fill: { color: C.accent4, transparency: 20 }, shadow: mkShadow() });
    s.addShape(pres.shapes.RECTANGLE, { x: 3.0, y: 1.3, w: 0.06, h: 0.7, fill: { color: C.accent4 } });
    s.addText("\u603B\u88C1\uFF08\u7528\u6237\uFF09", { x: 3.2, y: 1.32, w: 1.6, h: 0.32, fontSize: 14, fontFace: "Calibri", color: C.white, bold: true, margin: 0 });
    s.addText("\u6700\u9AD8\u51B3\u7B56\u8005 \u00B7 \u6218\u7565\u5B9A\u5411", { x: 3.2, y: 1.6, w: 3, h: 0.3, fontSize: 11, fontFace: "Calibri", color: C.textLight, margin: 0 });
    // Arrow
    s.addShape(pres.shapes.LINE, { x: 5.0, y: 2.0, w: 0, h: 0.3, line: { color: C.textMuted, width: 1.5 } });

    // Layer 2 - Lysander CEO
    s.addShape(pres.shapes.RECTANGLE, { x: 2.5, y: 2.3, w: 5.0, h: 0.7, fill: { color: C.primary, transparency: 20 }, shadow: mkShadow() });
    s.addShape(pres.shapes.RECTANGLE, { x: 2.5, y: 2.3, w: 0.06, h: 0.7, fill: { color: C.primary } });
    s.addText("Lysander CEO (AI)", { x: 2.7, y: 2.32, w: 2.5, h: 0.32, fontSize: 14, fontFace: "Calibri", color: C.white, bold: true, margin: 0 });
    s.addText("\u65E5\u5E38\u7BA1\u7406 \u00B7 \u4EFB\u52A1\u5206\u89E3 \u00B7 \u51B3\u7B56\u8DEF\u7531 \u00B7 \u7ED3\u679C\u6C47\u603B", { x: 2.7, y: 2.6, w: 4.5, h: 0.3, fontSize: 11, fontFace: "Calibri", color: C.textLight, margin: 0 });
    // Arrow
    s.addShape(pres.shapes.LINE, { x: 5.0, y: 3.0, w: 0, h: 0.3, line: { color: C.textMuted, width: 1.5 } });

    // Layer 3 - Think tank
    s.addShape(pres.shapes.RECTANGLE, { x: 2.0, y: 3.3, w: 6.0, h: 0.7, fill: { color: C.accent2, transparency: 20 }, shadow: mkShadow() });
    s.addShape(pres.shapes.RECTANGLE, { x: 2.0, y: 3.3, w: 0.06, h: 0.7, fill: { color: C.accent2 } });
    s.addText("Graphify \u667A\u56CA\u56E2 (4\u4EBA)", { x: 2.2, y: 3.32, w: 3, h: 0.32, fontSize: 14, fontFace: "Calibri", color: C.white, bold: true, margin: 0 });
    s.addText("\u6218\u7565\u5206\u6790\u5E08 \u00B7 \u5173\u8054\u53D1\u73B0 \u00B7 \u8D8B\u52BF\u6D1E\u5BDF \u00B7 \u51B3\u7B56\u987E\u95EE", { x: 2.2, y: 3.6, w: 5.5, h: 0.3, fontSize: 11, fontFace: "Calibri", color: C.textLight, margin: 0 });
    // Arrow
    s.addShape(pres.shapes.LINE, { x: 5.0, y: 4.0, w: 0, h: 0.3, line: { color: C.textMuted, width: 1.5 } });

    // Layer 4 - Execution teams
    s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: 4.3, w: 8.8, h: 0.8, fill: { color: C.accent3, transparency: 20 }, shadow: mkShadow() });
    s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: 4.3, w: 0.06, h: 0.8, fill: { color: C.accent3 } });
    s.addText("5 \u5927\u6267\u884C\u56E2\u961F (25\u4EBA)", { x: 0.85, y: 4.32, w: 3, h: 0.35, fontSize: 14, fontFace: "Calibri", color: C.white, bold: true, margin: 0 });
    s.addText("Butler(7)  |  RD(5)  |  OBS(4)  |  Content_ops(4)  |  Stock(5)", { x: 0.85, y: 4.65, w: 8, h: 0.3, fontSize: 12, fontFace: "Calibri", color: C.textLight, margin: 0 });

    // Side note
    s.addText("\u5408\u8BA1 29 \u4F4D AI \u4E13\u5BB6", { x: 7.2, y: 1.35, w: 2.4, h: 0.5, fontSize: 18, fontFace: "Calibri", color: C.primary, bold: true, align: "center", margin: 0 });
  }

  // ═══════════════════════════════════════════
  // SLIDE 6 — 6 Teams Matrix
  // ═══════════════════════════════════════════
  {
    const s = pres.addSlide();
    s.background = { color: C.bgDark };
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.04, fill: { color: C.primary } });
    s.addText("CHAPTER 02", { x: 0.6, y: 0.25, w: 3, h: 0.4, fontSize: 11, fontFace: "Calibri", color: C.primary, bold: true, charSpacing: 4, margin: 0 });
    s.addText("\u516D\u5927\u56E2\u961F\u804C\u80FD\u77E9\u9635", { x: 0.6, y: 0.6, w: 8, h: 0.55, fontSize: 26, fontFace: "Calibri", color: C.white, bold: true, margin: 0 });

    const teams = [
      { name: "Graphify \u667A\u56CA\u56E2", num: "4\u4EBA", desc: "\u6218\u7565\u5206\u6790\u3001\u51B3\u7B56\u652F\u6301\u3001\u8D8B\u52BF\u6D1E\u5BDF", icon: icons.brain, color: C.accent2 },
      { name: "Butler \u56E2\u961F", num: "7\u4EBA", desc: "\u9879\u76EE\u4EA4\u4ED8\u3001IoT\u3001PMO\u3001UAT", icon: icons.cogs, color: C.primary },
      { name: "RD \u7814\u53D1\u56E2\u961F", num: "5\u4EBA", desc: "\u7CFB\u7EDF\u67B6\u6784\u3001\u5168\u6808\u5F00\u53D1\u3001DevOps", icon: icons.code, color: C.accent3 },
      { name: "OBS \u77E5\u8BC6\u7BA1\u7406", num: "4\u4EBA", desc: "\u77E5\u8BC6\u6C89\u6DC0\u3001\u68C0\u7D22\u3001\u8D28\u91CF\u5BA1\u6838", icon: icons.db, color: C.accent },
      { name: "Content_ops", num: "4\u4EBA", desc: "\u535A\u5BA2\u3001\u516C\u4F17\u53F7\u3001\u89C6\u89C9\u8BBE\u8BA1", icon: icons.clipboard, color: C.accent4 },
      { name: "Stock \u80A1\u7968\u9879\u76EE", num: "5\u4EBA", desc: "A\u80A1\u8D8B\u52BF\u4EA4\u6613\u7CFB\u7EDF", icon: icons.chart, color: C.accent5 },
    ];

    // 2x3 grid
    teams.forEach((t, i) => {
      const col = i % 3;
      const row = Math.floor(i / 3);
      const x = 0.5 + col * 3.1;
      const y = 1.35 + row * 2.0;

      s.addShape(pres.shapes.RECTANGLE, { x, y, w: 2.9, h: 1.75, fill: { color: C.bgCard }, shadow: mkShadow() });
      s.addShape(pres.shapes.RECTANGLE, { x, y, w: 2.9, h: 0.05, fill: { color: t.color } });
      s.addImage({ data: t.icon, x: x + 0.2, y: y + 0.25, w: 0.4, h: 0.4 });
      s.addText(t.name, { x: x + 0.7, y: y + 0.2, w: 2.0, h: 0.3, fontSize: 13, fontFace: "Calibri", color: C.white, bold: true, margin: 0 });
      s.addText(t.num, { x: x + 0.7, y: y + 0.48, w: 2.0, h: 0.25, fontSize: 11, fontFace: "Calibri", color: t.color, margin: 0 });
      s.addText(t.desc, { x: x + 0.2, y: y + 0.85, w: 2.5, h: 0.7, fontSize: 11, fontFace: "Calibri", color: C.textLight, margin: 0 });
    });
  }

  // ═══════════════════════════════════════════
  // SLIDE 7 — Tech Architecture (3 layers)
  // ═══════════════════════════════════════════
  {
    const s = pres.addSlide();
    s.background = { color: C.bgDark };
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.04, fill: { color: C.primary } });
    s.addText("CHAPTER 02", { x: 0.6, y: 0.25, w: 3, h: 0.4, fontSize: 11, fontFace: "Calibri", color: C.primary, bold: true, charSpacing: 4, margin: 0 });
    s.addText("\u6838\u5FC3\u6280\u672F\u67B6\u6784\uFF1A\u4E09\u5C42\u6A21\u578B", { x: 0.6, y: 0.6, w: 8, h: 0.55, fontSize: 26, fontFace: "Calibri", color: C.white, bold: true, margin: 0 });

    const layers = [
      { title: "\u6570\u636E\u5C42 \u2014 Obsidian Vault", desc: "\u552F\u4E00\u6570\u636E\u6E90 \u00B7 29 \u5F20\u4EBA\u5458\u5361\u7247 \u00B7 \u672C\u5730 Markdown \u00B7 \u96F6\u9501\u5B9A", color: C.accent, y: 1.3, icon: icons.db },
      { title: "\u914D\u7F6E\u5C42 \u2014 YAML \u96C6\u7FA4", desc: "organization.yaml + decision_rules + *_experts.yaml + decision_log.json", color: C.accent2, y: 2.7, icon: icons.cogs },
      { title: "\u6267\u884C\u5C42 \u2014 Claude Code", desc: "CLAUDE.md \u52A0\u8F7D \u00B7 decision_check() \u00B7 assemble_team() \u00B7 execution_chain", color: C.primary, y: 4.1, icon: icons.rocket },
    ];
    layers.forEach((l) => {
      s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: l.y, w: 8.8, h: 1.15, fill: { color: C.bgCard }, shadow: mkShadow() });
      s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: l.y, w: 0.06, h: 1.15, fill: { color: l.color } });
      s.addImage({ data: l.icon, x: 1.0, y: l.y + 0.3, w: 0.55, h: 0.55 });
      s.addText(l.title, { x: 1.8, y: l.y + 0.15, w: 7, h: 0.4, fontSize: 16, fontFace: "Calibri", color: C.white, bold: true, margin: 0 });
      s.addText(l.desc, { x: 1.8, y: l.y + 0.6, w: 7, h: 0.4, fontSize: 12, fontFace: "Calibri", color: C.textLight, margin: 0 });
    });

    // Arrows between layers
    s.addShape(pres.shapes.LINE, { x: 5.0, y: 2.45, w: 0, h: 0.25, line: { color: C.textMuted, width: 1.5 } });
    s.addText("hr_watcher.py", { x: 5.2, y: 2.42, w: 2, h: 0.3, fontSize: 9, fontFace: "Calibri", color: C.textMuted, italic: true, margin: 0 });
    s.addShape(pres.shapes.LINE, { x: 5.0, y: 3.85, w: 0, h: 0.25, line: { color: C.textMuted, width: 1.5 } });
    s.addText("hr_base.py", { x: 5.2, y: 3.82, w: 2, h: 0.3, fontSize: 9, fontFace: "Calibri", color: C.textMuted, italic: true, margin: 0 });
  }

  // ═══════════════════════════════════════════
  // SLIDE 8 — McKinsey Rewired Evaluation
  // ═══════════════════════════════════════════
  {
    const s = pres.addSlide();
    s.background = { color: C.bgDark };
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.04, fill: { color: C.primary } });
    s.addText("CHAPTER 03", { x: 0.6, y: 0.25, w: 3, h: 0.4, fontSize: 11, fontFace: "Calibri", color: C.primary, bold: true, charSpacing: 4, margin: 0 });
    s.addText("McKinsey Rewired \u6846\u67B6\u8BC4\u4F30", { x: 0.6, y: 0.6, w: 8, h: 0.55, fontSize: 26, fontFace: "Calibri", color: C.white, bold: true, margin: 0 });

    const dims = [
      { name: "Strategy",        score: 4, label: "\u2605\u2605\u2605\u2605\u2606" },
      { name: "Talent",           score: 5, label: "\u2605\u2605\u2605\u2605\u2605" },
      { name: "Operating Model",  score: 5, label: "\u2605\u2605\u2605\u2605\u2605" },
      { name: "Technology",       score: 4, label: "\u2605\u2605\u2605\u2605\u2606" },
      { name: "Data",             score: 4, label: "\u2605\u2605\u2605\u2605\u2606" },
      { name: "Adoption",         score: 3, label: "\u2605\u2605\u2605\u2606\u2606" },
    ];

    dims.forEach((d, i) => {
      const y = 1.4 + i * 0.6;
      s.addText(d.name, { x: 0.6, y, w: 2.0, h: 0.4, fontSize: 13, fontFace: "Calibri", color: C.textLight, bold: true, margin: 0 });
      // Score bar bg
      s.addShape(pres.shapes.RECTANGLE, { x: 2.8, y: y + 0.05, w: 5.0, h: 0.28, fill: { color: C.lineColor } });
      // Score bar fill
      const fillW = (d.score / 5) * 5.0;
      s.addShape(pres.shapes.RECTANGLE, { x: 2.8, y: y + 0.05, w: fillW, h: 0.28, fill: { color: d.score === 5 ? C.accent3 : C.primary } });
      // Stars
      s.addText(d.label, { x: 8.0, y, w: 1.5, h: 0.4, fontSize: 12, fontFace: "Calibri", color: C.starGold, margin: 0 });
    });

    // Key insight box
    s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: 5.0, w: 8.8, h: 0.5, fill: { color: C.primary, transparency: 85 } });
    s.addText("McKinsey: \"AI \u4EF7\u503C\u6700\u5F3A\u7684\u5355\u4E00\u9884\u6D4B\u56E0\u5B50 = \u7EC4\u7EC7\u662F\u5426\u4ECE\u6839\u672C\u4E0A\u91CD\u65B0\u8BBE\u8BA1\u4E86\u5DE5\u4F5C\u6D41\"", {
      x: 0.8, y: 5.02, w: 8.4, h: 0.45, fontSize: 12, fontFace: "Calibri", color: C.white, italic: true, align: "center", margin: 0
    });
  }

  // ═══════════════════════════════════════════
  // SLIDE 9 — Knowledge Cycle
  // ═══════════════════════════════════════════
  {
    const s = pres.addSlide();
    s.background = { color: C.bgDark };
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.04, fill: { color: C.primary } });
    s.addText("CHAPTER 03", { x: 0.6, y: 0.25, w: 3, h: 0.4, fontSize: 11, fontFace: "Calibri", color: C.primary, bold: true, charSpacing: 4, margin: 0 });
    s.addText("\u4E09\u5C42\u77E5\u8BC6\u5FAA\u73AF\u6A21\u578B", { x: 0.6, y: 0.6, w: 8, h: 0.55, fontSize: 26, fontFace: "Calibri", color: C.white, bold: true, margin: 0 });

    // 5 steps in circular flow — laid out as horizontal flow
    const steps = [
      { num: "\u2460", title: "\u6C89\u6DC0", desc: "\u4EBA\u7684\u7ECF\u9A8C\n\u2192 Obsidian", color: C.accent4 },
      { num: "\u2461", title: "\u7F16\u7801", desc: "Obsidian\n\u2192 YAML/CLAUDE", color: C.accent2 },
      { num: "\u2462", title: "\u6267\u884C", desc: "AI \u56E2\u961F\n\u77E5\u8BC6\u5E94\u7528", color: C.primary },
      { num: "\u2463", title: "\u5BA1\u8BA1", desc: "Harness\n\u51B3\u7B56\u5BA1\u8BA1", color: C.accent3 },
      { num: "\u2464", title: "\u8FED\u4EE3", desc: "\u66F4\u65B0\u5361\u7247\n\u56DE\u5230\u2460", color: C.accent },
    ];
    steps.forEach((st, i) => {
      const x = 0.4 + i * 1.9;
      const y = 1.5;
      // Circle-like box
      s.addShape(pres.shapes.OVAL, { x: x + 0.55, y, w: 0.9, h: 0.9, fill: { color: st.color, transparency: 20 } });
      s.addText(st.num, { x: x + 0.55, y: y + 0.05, w: 0.9, h: 0.8, fontSize: 24, fontFace: "Calibri", color: st.color, bold: true, align: "center", valign: "middle", margin: 0 });
      s.addText(st.title, { x: x + 0.15, y: y + 1.0, w: 1.7, h: 0.35, fontSize: 14, fontFace: "Calibri", color: C.white, bold: true, align: "center", margin: 0 });
      s.addText(st.desc, { x: x + 0.15, y: y + 1.35, w: 1.7, h: 0.6, fontSize: 11, fontFace: "Calibri", color: C.textLight, align: "center", margin: 0 });
      // Arrow between
      if (i < 4) {
        s.addImage({ data: icons.arrow, x: x + 1.75, y: y + 0.2, w: 0.35, h: 0.35 });
      }
    });

    // Bottom insight
    s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: 3.7, w: 8.8, h: 1.5, fill: { color: C.bgCard }, shadow: mkShadow() });
    s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: 3.7, w: 0.06, h: 1.5, fill: { color: C.accent3 } });
    s.addImage({ data: icons.bulb, x: 1.0, y: 3.95, w: 0.5, h: 0.5 });
    s.addText("\u6838\u5FC3\u6D1E\u5BDF", { x: 1.7, y: 3.85, w: 7, h: 0.4, fontSize: 16, fontFace: "Calibri", color: C.white, bold: true, margin: 0 });
    s.addText([
      { text: "\u77E5\u8BC6\u4ECE\u4E2A\u4EBA\u5927\u8111\u6D41\u5165\u7CFB\u7EDF\uFF0C\u901A\u8FC7\u7CFB\u7EDF\u653E\u5927\u540E\u56DE\u9988\u4E3A\u7EC4\u7EC7\u8D44\u4EA7\u3002", options: { breakLine: true, fontSize: 13, color: C.textLight } },
      { text: "\"AI \u539F\u751F\u4F01\u4E1A\u5C06 AI \u751F\u6210\u7684\u4E13\u6709\u6D1E\u5BDF\u4F5C\u4E3A\u8FD0\u8425\u526F\u4EA7\u54C1\u6C89\u6DC0\uFF0C\u8FD9\u4E9B\u6D1E\u5BDF\u662F\u7ADE\u4E89\u5BF9\u624B\u65E0\u6CD5\u590D\u5236\u7684\"", options: { fontSize: 12, color: C.textMuted, italic: true } },
    ], { x: 1.7, y: 4.25, w: 7.3, h: 0.85, margin: 0 });
  }

  // ═══════════════════════════════════════════
  // SLIDE 10 — Deloitte Benchmark
  // ═══════════════════════════════════════════
  {
    const s = pres.addSlide();
    s.background = { color: C.bgDark };
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.04, fill: { color: C.primary } });
    s.addText("CHAPTER 03", { x: 0.6, y: 0.25, w: 3, h: 0.4, fontSize: 11, fontFace: "Calibri", color: C.primary, bold: true, charSpacing: 4, margin: 0 });
    s.addText("Deloitte \u5168\u7403\u5BF9\u6807\u5206\u6790", { x: 0.6, y: 0.6, w: 8, h: 0.55, fontSize: 26, fontFace: "Calibri", color: C.white, bold: true, margin: 0 });

    // Horizontal bar comparison
    const benchmarks = [
      { label: "\u6709\u6B63\u5F0F Agent \u6218\u7565", ours: 100, avg: 23 },
      { label: "Agent \u751F\u4EA7\u73AF\u5883\u4F7F\u7528", ours: 100, avg: 11 },
      { label: "\u51B3\u7B56\u4F53\u7CFB\u6CBB\u7406\u6210\u719F", ours: 100, avg: 21 },
      { label: "\u5DE5\u4F5C\u6D41\u91CD\u65B0\u8BBE\u8BA1", ours: 100, avg: 33 },
    ];

    benchmarks.forEach((b, i) => {
      const y = 1.45 + i * 1.0;
      s.addText(b.label, { x: 0.6, y: y - 0.2, w: 3, h: 0.3, fontSize: 12, fontFace: "Calibri", color: C.textLight, margin: 0 });
      // Our bar
      s.addShape(pres.shapes.RECTANGLE, { x: 3.5, y, w: (b.ours / 100) * 5.5, h: 0.25, fill: { color: C.primary } });
      s.addText("\u672C\u4F53\u7CFB 100%", { x: 9.2, y: y - 0.05, w: 1.5, h: 0.3, fontSize: 10, fontFace: "Calibri", color: C.primary, margin: 0 });
      // Avg bar
      s.addShape(pres.shapes.RECTANGLE, { x: 3.5, y: y + 0.35, w: (b.avg / 100) * 5.5, h: 0.25, fill: { color: C.textDim } });
      s.addText("\u5168\u7403\u5747\u503C " + b.avg + "%", { x: 3.5 + (b.avg / 100) * 5.5 + 0.15, y: y + 0.3, w: 1.5, h: 0.3, fontSize: 10, fontFace: "Calibri", color: C.textMuted, margin: 0 });
    });

    s.addText("\u6570\u636E\u6765\u6E90: Deloitte State of AI in Enterprise 2026", { x: 0.5, y: 5.2, w: 9, h: 0.3, fontSize: 9, fontFace: "Calibri", color: C.textDim, margin: 0 });
  }

  // ═══════════════════════════════════════════
  // SLIDE 11 — Innovation 1&2
  // ═══════════════════════════════════════════
  {
    const s = pres.addSlide();
    s.background = { color: C.bgDark };
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.04, fill: { color: C.primary } });
    s.addText("CHAPTER 04", { x: 0.6, y: 0.25, w: 3, h: 0.4, fontSize: 11, fontFace: "Calibri", color: C.primary, bold: true, charSpacing: 4, margin: 0 });
    s.addText("\u4E94\u5927\u521B\u65B0\u8BBE\u8BA1 (1/2)", { x: 0.6, y: 0.6, w: 8, h: 0.55, fontSize: 26, fontFace: "Calibri", color: C.white, bold: true, margin: 0 });

    // Innovation 1
    s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 1.3, w: 4.4, h: 3.6, fill: { color: C.bgCard }, shadow: mkShadow() });
    s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 1.3, w: 4.4, h: 0.06, fill: { color: C.accent } });
    s.addImage({ data: icons.db, x: 0.8, y: 1.55, w: 0.45, h: 0.45 });
    s.addText("\u521B\u65B0\u4E00\uFF1AObsidian \u5373 Single Source of Truth", { x: 1.4, y: 1.5, w: 3.3, h: 0.5, fontSize: 14, fontFace: "Calibri", color: C.white, bold: true, margin: 0 });
    s.addText([
      { text: "\u4F20\u7EDF\u65B9\u5F0F", options: { bold: true, color: C.accent5, fontSize: 12, breakLine: true } },
      { text: "Confluence + Notion + Excel + Jira + \u90AE\u4EF6", options: { fontSize: 11, color: C.textMuted, breakLine: true } },
      { text: "\u2192 \u591A\u6E90\u51B2\u7A81\u3001\u7248\u672C\u5931\u63A7", options: { fontSize: 11, color: C.textMuted, breakLine: true } },
      { text: "", options: { breakLine: true, fontSize: 8 } },
      { text: "\u672C\u4F53\u7CFB", options: { bold: true, color: C.accent3, fontSize: 12, breakLine: true } },
      { text: "Obsidian \u552F\u4E00\u6570\u636E\u6E90", options: { fontSize: 11, color: C.textLight, breakLine: true } },
      { text: "\u2192 \u672C\u5730\u4F18\u5148 \u00B7 \u7EAF\u6587\u672C \u00B7 \u96F6\u9501\u5B9A", options: { fontSize: 11, color: C.textLight, breakLine: true } },
      { text: "", options: { breakLine: true, fontSize: 8 } },
      { text: "Obsidian 2026 \u5E74 150 \u4E07\u7528\u6237 (YoY +22%)", options: { fontSize: 11, color: C.accent, italic: true } },
    ], { x: 0.8, y: 2.15, w: 3.8, h: 2.6, margin: 0 });

    // Innovation 2
    s.addShape(pres.shapes.RECTANGLE, { x: 5.1, y: 1.3, w: 4.4, h: 3.6, fill: { color: C.bgCard }, shadow: mkShadow() });
    s.addShape(pres.shapes.RECTANGLE, { x: 5.1, y: 1.3, w: 4.4, h: 0.06, fill: { color: C.accent2 } });
    s.addImage({ data: icons.shield, x: 5.4, y: 1.55, w: 0.45, h: 0.45 });
    s.addText("\u521B\u65B0\u4E8C\uFF1A\u51B3\u7B56\u4EE3\u7801\u5316", { x: 6.0, y: 1.5, w: 3.3, h: 0.5, fontSize: 14, fontFace: "Calibri", color: C.white, bold: true, margin: 0 });
    s.addText([
      { text: "\u539F\u5219\u662F\u201C\u89C4\u5219\u201D\u800C\u975E\u201C\u5EFA\u8BAE\u201D", options: { bold: true, color: C.accent2, fontSize: 12, breakLine: true } },
      { text: "", options: { breakLine: true, fontSize: 6 } },
      { text: "decision_check() \u56DB\u7EA7\u8DEF\u7531\uFF1A", options: { fontSize: 11, color: C.textLight, breakLine: true } },
      { text: "  Level 1: \u5C0F\u95EE\u9898 \u2192 \u76F4\u63A5\u6267\u884C", options: { fontSize: 11, color: C.textLight, breakLine: true } },
      { text: "  Level 2: \u4EE3\u7801\u5BA1\u8BA1 \u2192 QA \u68C0\u67E5", options: { fontSize: 11, color: C.textLight, breakLine: true } },
      { text: "  Level 3: \u667A\u56CA\u56E2 \u2192 \u6DF1\u5EA6\u5206\u6790", options: { fontSize: 11, color: C.textLight, breakLine: true } },
      { text: "  Level 4: \u8D85\u6388\u6743 \u2192 \u4E0A\u62A5\u603B\u88C1", options: { fontSize: 11, color: C.textLight, breakLine: true } },
      { text: "", options: { breakLine: true, fontSize: 6 } },
      { text: "McKinsey: \u6CBB\u7406\u6210\u719F\u5EA6\u9886\u5148\u7EC4\u7EC7\u8BC4\u5206 2.6", options: { fontSize: 11, color: C.accent2, italic: true } },
    ], { x: 5.4, y: 2.15, w: 3.8, h: 2.6, margin: 0 });
  }

  // ═══════════════════════════════════════════
  // SLIDE 12 — Innovation 3-5
  // ═══════════════════════════════════════════
  {
    const s = pres.addSlide();
    s.background = { color: C.bgDark };
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.04, fill: { color: C.primary } });
    s.addText("CHAPTER 04", { x: 0.6, y: 0.25, w: 3, h: 0.4, fontSize: 11, fontFace: "Calibri", color: C.primary, bold: true, charSpacing: 4, margin: 0 });
    s.addText("\u4E94\u5927\u521B\u65B0\u8BBE\u8BA1 (2/2)", { x: 0.6, y: 0.6, w: 8, h: 0.55, fontSize: 26, fontFace: "Calibri", color: C.white, bold: true, margin: 0 });

    const innovations = [
      { title: "\u521B\u65B0\u4E09\uFF1AHarness \u9519\u8BEF\u81EA\u6108", desc: "pre_execution_check() \u62E6\u622A\n+ decision_log.json \u5BA1\u8BA1\u8FFD\u8E2A\n+ post_execution_evaluate() \u81EA\u52A8\u8BC4\u4F30\n+ \u53CD\u9988\u56DE\u8DEF\u66F4\u65B0\u5173\u952E\u8BCD\u6743\u91CD", icon: icons.shield, color: C.accent3 },
      { title: "\u521B\u65B0\u56DB\uFF1A\u96F6\u6469\u64E6\u56E2\u961F\u6269\u5C55", desc: "git clone + cd + claude\n\u603B\u8017\u65F6 < 2 \u5206\u949F\n\u65B0\u6210\u5458\u7B2C\u4E00\u5929\u7EE7\u627F\u5168\u90E8\u7EC4\u7EC7\u77E5\u8BC6\n\u884C\u4E1A\u5E73\u5747\u4E0A\u624B\u5468\u671F: 1-4 \u5468", icon: icons.users, color: C.primary },
      { title: "\u521B\u65B0\u4E94\uFF1A\u8F7B\u91CF\u7EA7 AI \u539F\u751F\u67B6\u6784", desc: "\u65E0\u670D\u52A1\u5668 \u00B7 \u65E0\u5411\u91CF\u6570\u636E\u5E93 \u00B7 \u65E0 RAG Pipeline\nMarkdown \u5373\u77E5\u8BC6\uFF0CYAML \u5373\u914D\u7F6E\nCLAUDE.md \u5373\u64CD\u4F5C\u7CFB\u7EDF\n\u90E8\u7F72\u590D\u6742\u5EA6: \u5206\u949F\u7EA7 vs \u884C\u4E1A\u5E73\u5747\u5929/\u5468", icon: icons.rocket, color: C.accent },
    ];

    innovations.forEach((inn, i) => {
      const y = 1.3 + i * 1.4;
      s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y, w: 9.0, h: 1.2, fill: { color: C.bgCard }, shadow: mkShadow() });
      s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y, w: 0.06, h: 1.2, fill: { color: inn.color } });
      s.addImage({ data: inn.icon, x: 0.85, y: y + 0.3, w: 0.5, h: 0.5 });
      s.addText(inn.title, { x: 1.6, y: y + 0.08, w: 4, h: 0.35, fontSize: 15, fontFace: "Calibri", color: C.white, bold: true, margin: 0 });
      s.addText(inn.desc, { x: 1.6, y: y + 0.4, w: 7.5, h: 0.75, fontSize: 11, fontFace: "Calibri", color: C.textLight, margin: 0 });
    });
  }

  // ═══════════════════════════════════════════
  // SLIDE 13 — Competitive Moat (4 layers) — REVISED
  // ═══════════════════════════════════════════
  {
    const s = pres.addSlide();
    s.background = { color: C.bgDark };
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.04, fill: { color: C.primary } });
    s.addText("CHAPTER 05", { x: 0.6, y: 0.25, w: 3, h: 0.4, fontSize: 11, fontFace: "Calibri", color: C.primary, bold: true, charSpacing: 4, margin: 0 });
    s.addText("AI Native \u7EC4\u7EC7\u62A4\u57CE\u6CB3\u6A21\u578B", { x: 0.6, y: 0.6, w: 8, h: 0.55, fontSize: 26, fontFace: "Calibri", color: C.white, bold: true, margin: 0 });

    const moats = [
      { layer: "\u7B2C\u4E00\u5C42", name: "\u5DE5\u5177\u6548\u7387", desc: "ChatGPT / Copilot / Claude \u7B49", barrier: "\u53EF\u88AB\u590D\u5236\uFF08\u4E00\u5468\u5185\uFF09", color: C.textMuted, w: 8.4 },
      { layer: "\u7B2C\u4E8C\u5C42", name: "\u6D41\u7A0B\u91CD\u6784", desc: "TASK_EXECUTION_CHAIN \u94FE\u5F0F\u81EA\u52A8\u6267\u884C", barrier: "\u4E2D\u7B49\u58C1\u5792\uFF081-3 \u4E2A\u6708\uFF09", color: C.accent, w: 7.2 },
      { layer: "\u7B2C\u4E09\u5C42", name: "\u77E5\u8BC6\u8D44\u4EA7\u5316", desc: "29 \u4E13\u5BB6\u5B9A\u4E49 + decision_log + \u4EBA\u5458\u5361\u7247", barrier: "\u9AD8\u58C1\u5792\uFF086-12 \u4E2A\u6708\uFF09", color: C.primary, w: 5.6 },
      { layer: "\u7B2C\u56DB\u5C42", name: "\u53CC\u98DE\u8F6E\u81EA\u8FDB\u5316", desc: "Harness Feedback Loop + hr_watcher \u8BB0\u5FC6\u540C\u6B65\u98DE\u8F6E", barrier: "\u6700\u5F3A\u58C1\u5792\uFF0812 \u4E2A\u6708+\uFF09\u2014 \u65F6\u95F4\u7684\u51FD\u6570\uFF0C\u65E0\u6CD5\u8D2D\u4E70", color: C.accent2, w: 3.8 },
    ];

    moats.forEach((m, i) => {
      const y = 1.25 + i * 0.9;
      const x = 0.6;
      s.addShape(pres.shapes.RECTANGLE, { x, y, w: m.w, h: 0.72, fill: { color: m.color, transparency: 75 } });
      s.addShape(pres.shapes.RECTANGLE, { x, y, w: 0.06, h: 0.72, fill: { color: m.color } });
      s.addText(m.layer, { x: x + 0.15, y: y + 0.02, w: 0.8, h: 0.3, fontSize: 10, fontFace: "Calibri", color: m.color, bold: true, margin: 0 });
      s.addText(m.name, { x: x + 0.95, y: y + 0.02, w: 2.5, h: 0.3, fontSize: 14, fontFace: "Calibri", color: C.white, bold: true, margin: 0 });
      s.addText(m.desc, { x: x + 0.95, y: y + 0.28, w: m.w - 1.2, h: 0.22, fontSize: 10, fontFace: "Calibri", color: C.textLight, margin: 0 });
      s.addText(m.barrier, { x: x + 0.95, y: y + 0.48, w: m.w - 1.2, h: 0.2, fontSize: 10, fontFace: "Calibri", color: m.color, italic: true, margin: 0 });
    });

    // Key stat - 44%
    s.addShape(pres.shapes.RECTANGLE, { x: 7.0, y: 1.25, w: 2.5, h: 1.35, fill: { color: C.bgCard }, shadow: mkShadow() });
    s.addText("44%", { x: 7.0, y: 1.3, w: 2.5, h: 0.55, fontSize: 36, fontFace: "Calibri", color: C.accent2, bold: true, align: "center", margin: 0 });
    s.addText("\u7B97\u6CD5\u9002\u5E94\u6027\u89E3\u91CA\u4E86\n44% \u957F\u671F\u7ADE\u4E89\u4F18\u52BF\u5DEE\u5F02", { x: 7.0, y: 1.85, w: 2.5, h: 0.55, fontSize: 10, fontFace: "Calibri", color: C.textLight, align: "center", margin: 0 });
    s.addText("Academy of Management Review", { x: 7.0, y: 2.35, w: 2.5, h: 0.2, fontSize: 8, fontFace: "Calibri", color: C.textDim, align: "center", margin: 0 });
  }

  // ═══════════════════════════════════════════
  // SLIDE 13b — Dual Flywheel Deep Dive (NEW)
  // ═══════════════════════════════════════════
  {
    const s = pres.addSlide();
    s.background = { color: C.bgDark };
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.04, fill: { color: C.primary } });
    s.addText("CHAPTER 05", { x: 0.6, y: 0.25, w: 3, h: 0.4, fontSize: 11, fontFace: "Calibri", color: C.primary, bold: true, charSpacing: 4, margin: 0 });
    s.addText("\u7B2C\u56DB\u5C42\u6DF1\u5165\uFF1A\u53CC\u98DE\u8F6E\u81EA\u8FDB\u5316\u673A\u5236", { x: 0.6, y: 0.6, w: 9, h: 0.55, fontSize: 26, fontFace: "Calibri", color: C.white, bold: true, margin: 0 });

    // ── Flywheel A: Harness Engineering ──
    s.addShape(pres.shapes.RECTANGLE, { x: 0.4, y: 1.25, w: 4.5, h: 4.0, fill: { color: C.bgCard }, shadow: mkShadow() });
    s.addShape(pres.shapes.RECTANGLE, { x: 0.4, y: 1.25, w: 4.5, h: 0.06, fill: { color: C.accent2 } });
    s.addText("\u98DE\u8F6E A\uFF1AHarness Engineering", { x: 0.65, y: 1.4, w: 4, h: 0.4, fontSize: 16, fontFace: "Calibri", color: C.accent2, bold: true, margin: 0 });
    s.addText("\u51B3\u7B56\u667A\u80FD Feedback Loop", { x: 0.65, y: 1.75, w: 4, h: 0.3, fontSize: 12, fontFace: "Calibri", color: C.textMuted, margin: 0 });

    // Flywheel A steps (circular)
    const fwA = [
      { num: "\u2460", label: "decision_check()", desc: "\u56DB\u7EA7\u51B3\u7B56\u8DEF\u7531", y: 2.2 },
      { num: "\u2461", label: "record_decision()", desc: "\u6BCF\u6B21\u51B3\u7B56\u81EA\u52A8\u8BB0\u5F55\u5230 decision_log.json", y: 2.7 },
      { num: "\u2462", label: "record_feedback()", desc: "\u6267\u884C\u7ED3\u679C\u53CD\u9988: correct / incorrect / intervened", y: 3.2 },
      { num: "\u2463", label: "_analyze_and_adjust()", desc: "\u8BEF\u5224\u5206\u6790 \u2192 \u81EA\u52A8\u8C03\u6574\u5173\u952E\u8BCD\u6743\u91CD", y: 3.7 },
      { num: "\u2464", label: "decision_check() \u2191", desc: "\u4E0B\u6B21\u51B3\u7B56\u66F4\u51C6\u786E \u2192 \u56DE\u5230\u2460", y: 4.2 },
    ];
    fwA.forEach((step) => {
      s.addText(step.num, { x: 0.65, y: step.y, w: 0.35, h: 0.35, fontSize: 14, fontFace: "Calibri", color: C.accent2, bold: true, margin: 0 });
      s.addText(step.label, { x: 1.05, y: step.y, w: 2.0, h: 0.22, fontSize: 11, fontFace: "Calibri", color: C.white, bold: true, margin: 0 });
      s.addText(step.desc, { x: 1.05, y: step.y + 0.22, w: 3.5, h: 0.22, fontSize: 10, fontFace: "Calibri", color: C.textLight, margin: 0 });
    });
    // Result text
    s.addText("\u7ED3\u679C\uFF1A\u7CFB\u7EDF\u8D8A\u7528\u8D8A\u7CBE\u51C6\uFF0C\u51B3\u7B56\u51C6\u786E\u7387\u6301\u7EED\u63D0\u5347", {
      x: 0.65, y: 4.75, w: 3.9, h: 0.35, fontSize: 10, fontFace: "Calibri", color: C.accent2, italic: true, margin: 0
    });

    // ── Flywheel B: hr_watcher + Memory Sync ──
    s.addShape(pres.shapes.RECTANGLE, { x: 5.1, y: 1.25, w: 4.5, h: 4.0, fill: { color: C.bgCard }, shadow: mkShadow() });
    s.addShape(pres.shapes.RECTANGLE, { x: 5.1, y: 1.25, w: 4.5, h: 0.06, fill: { color: C.accent3 } });
    s.addText("\u98DE\u8F6E B\uFF1Ahr_watcher + \u8BB0\u5FC6\u540C\u6B65", { x: 5.35, y: 1.4, w: 4, h: 0.4, fontSize: 16, fontFace: "Calibri", color: C.accent3, bold: true, margin: 0 });
    s.addText("\u77E5\u8BC6\u5B9E\u65F6\u540C\u6B65\u98DE\u8F6E", { x: 5.35, y: 1.75, w: 4, h: 0.3, fontSize: 12, fontFace: "Calibri", color: C.textMuted, margin: 0 });

    // Channel 1
    s.addText("\u901A\u9053 1\uFF1AHR \u77E5\u8BC6\u5E93\u540C\u6B65", { x: 5.35, y: 2.15, w: 4, h: 0.3, fontSize: 12, fontFace: "Calibri", color: C.white, bold: true, margin: 0 });
    const fwB1 = [
      { label: "Obsidian \u7F16\u8F91\u4EBA\u5458\u5361\u7247", y: 2.5 },
      { label: "HRDirHandler \u76D1\u63A7\u53D8\u66F4\uFF08\u9632\u6296 2s\uFF09", y: 2.8 },
      { label: "sync_all_teams() \u81EA\u52A8\u66F4\u65B0 YAML", y: 3.1 },
      { label: "AI \u56E2\u961F\u80FD\u529B\u5B9E\u65F6\u751F\u6548", y: 3.4 },
    ];
    fwB1.forEach((step, i) => {
      s.addText((i < 3 ? "\u2192 " : "\u2713 ") + step.label, { x: 5.55, y: step.y, w: 3.8, h: 0.25, fontSize: 10, fontFace: "Calibri", color: i < 3 ? C.textLight : C.accent3, margin: 0 });
    });

    // Channel 2
    s.addText("\u901A\u9053 2\uFF1AClaude \u8BB0\u5FC6\u540C\u6B65", { x: 5.35, y: 3.8, w: 4, h: 0.3, fontSize: 12, fontFace: "Calibri", color: C.white, bold: true, margin: 0 });
    const fwB2 = [
      { label: "Obsidian \u66F4\u65B0\u8BB0\u5FC6\u6587\u4EF6", y: 4.15 },
      { label: "ClaudeMemoryHandler \u76D1\u63A7\u53D8\u66F4", y: 4.45 },
      { label: "sync-claude-memory.sh \u2192 .claude/ \u76EE\u5F55", y: 4.75 },
    ];
    fwB2.forEach((step) => {
      s.addText("\u2192 " + step.label, { x: 5.55, y: step.y, w: 3.8, h: 0.25, fontSize: 10, fontFace: "Calibri", color: C.textLight, margin: 0 });
    });
    // Result
    s.addText("\u7ED3\u679C\uFF1A\u77E5\u8BC6\u7F16\u8F91\u5373\u523B\u751F\u6548\uFF0C\u96F6\u624B\u52A8\u540C\u6B65", {
      x: 5.35, y: 5.02, w: 3.9, h: 0.2, fontSize: 10, fontFace: "Calibri", color: C.accent3, italic: true, margin: 0
    });
  }

  // ═══════════════════════════════════════════
  // SLIDE 14 — Trend Signals
  // ═══════════════════════════════════════════
  {
    const s = pres.addSlide();
    s.background = { color: C.bgDark };
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.04, fill: { color: C.primary } });
    s.addText("CHAPTER 06", { x: 0.6, y: 0.25, w: 3, h: 0.4, fontSize: 11, fontFace: "Calibri", color: C.primary, bold: true, charSpacing: 4, margin: 0 });
    s.addText("AI Native \u8D8B\u52BF\u5C55\u671B", { x: 0.6, y: 0.6, w: 8, h: 0.55, fontSize: 26, fontFace: "Calibri", color: C.white, bold: true, margin: 0 });

    const signals = [
      { sig: "Claude Code Agent Teams \u53D1\u5E03", detail: "\u591A\u5B9E\u4F8B\u534F\u8C03\u539F\u8BED\uFF08\u5171\u4EAB\u4EFB\u52A1\u3001P2P \u6D88\u606F\uFF09", color: C.primary },
      { sig: "Anthropic Agent SDK \u53D1\u5E03", detail: "Claude 4.6 \u914D\u5957 SDK\uFF0C\u53EF\u5C06 hr_base.py \u5347\u7EA7\u4E3A SDK \u7EA7\u7F16\u6392", color: C.accent },
      { sig: "Cognition Devin 25% PRs", detail: "AI \u627F\u62C5\u516C\u53F8\u56DB\u5206\u4E4B\u4E00\u4EE3\u7801\u4EA7\u51FA\uFF0C\u9A8C\u8BC1\u201C\u8F85\u52A9\u2192\u4E3B\u529B\u201D\u53EF\u884C\u6027", color: C.accent3 },
      { sig: "Gartner 40% \u5D4C\u5165\u9884\u6D4B", detail: "\u4F01\u4E1A\u5E94\u7528 Agent \u5D4C\u5165\u7387\u4E00\u5E74 8 \u500D\u589E\u957F\uFF0C\u5148\u53D1\u7A97\u53E3\u6B63\u5728\u5173\u95ED", color: C.accent4 },
      { sig: "MIT Sloan Agentic Enterprise", detail: "\u8DE8\u804C\u80FD\u6CBB\u7406\u6210\u4E3A\u5FC5\u987B\uFF0C\u672C\u4F53\u7CFB\u51B3\u7B56\u4F53\u7CFB\u5DF2\u63D0\u524D\u6EE1\u8DB3", color: C.accent2 },
    ];

    signals.forEach((sg, i) => {
      const y = 1.3 + i * 0.82;
      s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y, w: 8.8, h: 0.68, fill: { color: C.bgCard } });
      s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y, w: 0.06, h: 0.68, fill: { color: sg.color } });
      s.addText(sg.sig, { x: 0.9, y: y + 0.02, w: 4, h: 0.3, fontSize: 13, fontFace: "Calibri", color: C.white, bold: true, margin: 0 });
      s.addText(sg.detail, { x: 0.9, y: y + 0.32, w: 8, h: 0.3, fontSize: 11, fontFace: "Calibri", color: C.textLight, margin: 0 });
    });
  }

  // ═══════════════════════════════════════════
  // SLIDE 15 — Roadmap
  // ═══════════════════════════════════════════
  {
    const s = pres.addSlide();
    s.background = { color: C.bgDark };
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.04, fill: { color: C.primary } });
    s.addText("CHAPTER 06", { x: 0.6, y: 0.25, w: 3, h: 0.4, fontSize: 11, fontFace: "Calibri", color: C.primary, bold: true, charSpacing: 4, margin: 0 });
    s.addText("\u6F14\u8FDB\u8DEF\u7EBF\u56FE", { x: 0.6, y: 0.6, w: 8, h: 0.55, fontSize: 26, fontFace: "Calibri", color: C.white, bold: true, margin: 0 });

    // Timeline line
    s.addShape(pres.shapes.LINE, { x: 0.8, y: 2.0, w: 8.4, h: 0, line: { color: C.primary, width: 2 } });

    // Phase markers
    const phases = [
      { x: 1.5, label: "2026 Q2", title: "\u5F53\u524D\u9636\u6BB5", items: "29 \u4E13\u5BB6\u4F53\u7CFB\n\u51B3\u7B56\u4EE3\u7801\u5316\n\u56E2\u961F\u63A8\u5E7F\n\u53CD\u9988\u6536\u96C6", color: C.primary, sub: "\u7EC4\u7EC7\u80FD\u529B\u6C89\u6DC0" },
      { x: 4.3, label: "2026 Q3-Q4", title: "\u6269\u5C55\u9636\u6BB5", items: "hr_watcher \u5B9E\u65F6\u540C\u6B65\nSOP \u77E5\u8BC6\u5E93\u8865\u5145\n\u51B3\u7B56\u51C6\u786E\u7387\u8C03\u4F18\nAgent Teams \u96C6\u6210", color: C.accent, sub: "\u7EC4\u7EC7\u6548\u7387\u653E\u5927" },
      { x: 7.1, label: "2027+", title: "\u81EA\u4E3B\u5316\u9636\u6BB5", items: "Agent \u81EA\u4E3B\u53D1\u73B0\u77E5\u8BC6\u7F3A\u53E3\n\u81EA\u4E3B\u8FED\u4EE3\u80FD\u529B\u5B9A\u4E49\n\u81EA\u4E3B\u7EC4\u5EFA\u4E34\u65F6\u9879\u76EE\u7EC4", color: C.accent2, sub: "\u7EC4\u7EC7\u81EA\u4E3B\u8FDB\u5316" },
    ];

    phases.forEach((p) => {
      // Dot on timeline
      s.addShape(pres.shapes.OVAL, { x: p.x + 0.55, y: 1.82, w: 0.35, h: 0.35, fill: { color: p.color } });
      // Label above
      s.addText(p.label, { x: p.x, y: 1.4, w: 1.5, h: 0.35, fontSize: 11, fontFace: "Calibri", color: p.color, bold: true, align: "center", margin: 0 });
      // Card below
      s.addShape(pres.shapes.RECTANGLE, { x: p.x - 0.2, y: 2.4, w: 2.8, h: 2.6, fill: { color: C.bgCard }, shadow: mkShadow() });
      s.addShape(pres.shapes.RECTANGLE, { x: p.x - 0.2, y: 2.4, w: 2.8, h: 0.05, fill: { color: p.color } });
      s.addText(p.title, { x: p.x, y: 2.55, w: 2.4, h: 0.35, fontSize: 14, fontFace: "Calibri", color: C.white, bold: true, margin: 0 });
      s.addText(p.items, { x: p.x, y: 2.95, w: 2.4, h: 1.3, fontSize: 11, fontFace: "Calibri", color: C.textLight, margin: 0 });
      s.addText(p.sub, { x: p.x, y: 4.4, w: 2.4, h: 0.3, fontSize: 11, fontFace: "Calibri", color: p.color, italic: true, margin: 0 });
    });
  }

  // ═══════════════════════════════════════════
  // SLIDE 16 — Comprehensive Rating
  // ═══════════════════════════════════════════
  {
    const s = pres.addSlide();
    s.background = { color: C.bgDark };
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.04, fill: { color: C.primary } });
    s.addText("CHAPTER 07", { x: 0.6, y: 0.25, w: 3, h: 0.4, fontSize: 11, fontFace: "Calibri", color: C.primary, bold: true, charSpacing: 4, margin: 0 });
    s.addText("\u7EFC\u5408\u8BC4\u7EA7", { x: 0.6, y: 0.6, w: 8, h: 0.55, fontSize: 26, fontFace: "Calibri", color: C.white, bold: true, margin: 0 });

    // Table header
    const headerRow = [
      { text: "\u8BC4\u4F30\u7EF4\u5EA6", options: { fill: { color: C.primary }, color: C.white, bold: true, fontSize: 12, align: "center" } },
      { text: "\u8BC4\u5206", options: { fill: { color: C.primary }, color: C.white, bold: true, fontSize: 12, align: "center" } },
      { text: "\u884C\u4E1A\u5206\u4F4D", options: { fill: { color: C.primary }, color: C.white, bold: true, fontSize: 12, align: "center" } },
    ];
    const rows = [
      ["\u6218\u7565\u4EF7\u503C", "\u2605\u2605\u2605\u2605\u2605", "Top 2%"],
      ["\u67B6\u6784\u5148\u8FDB\u6027", "\u2605\u2605\u2605\u2605\u2605", "Top 5%"],
      ["\u5DE5\u7A0B\u5B8C\u6574\u5EA6", "\u2605\u2605\u2605\u2605\u2606", "Top 10%"],
      ["\u53EF\u6269\u5C55\u6027", "\u2605\u2605\u2605\u2605\u2605", "Top 5%"],
      ["\u6CBB\u7406\u6210\u719F\u5EA6", "\u2605\u2605\u2605\u2605\u2606", "Top 5%"],
      ["\u56E2\u961F\u63A8\u5E7F\u5C31\u7EEA\u5EA6", "\u2605\u2605\u2605\u2605\u2606", "\u2014"],
      ["\u8D8B\u52BF\u5951\u5408\u5EA6", "\u2605\u2605\u2605\u2605\u2605", "\u2014"],
    ];

    const tableData = [headerRow];
    rows.forEach((r, i) => {
      const bgColor = i % 2 === 0 ? C.bgCard : C.bgMid;
      tableData.push([
        { text: r[0], options: { fill: { color: bgColor }, color: C.textLight, fontSize: 12 } },
        { text: r[1], options: { fill: { color: bgColor }, color: C.starGold, fontSize: 12, align: "center" } },
        { text: r[2], options: { fill: { color: bgColor }, color: C.primary, fontSize: 12, bold: true, align: "center" } },
      ]);
    });

    s.addTable(tableData, {
      x: 0.5, y: 1.2, w: 9.0,
      colW: [3.5, 3.0, 2.5],
      border: { pt: 0.5, color: C.lineColor },
      rowH: [0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4],
    });

    // Bottom conclusion
    s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 4.55, w: 9.0, h: 0.85, fill: { color: C.primary, transparency: 85 }, shadow: mkShadow() });
    s.addText([
      { text: "\u7EFC\u5408\u8BC4\u7EA7\uFF1A\u2605\u2605\u2605\u2605\u2606 \u2014 \u5F3A\u70C8\u63A8\u8350", options: { bold: true, fontSize: 16, color: C.white, breakLine: true } },
      { text: "\u5F53\u524D\u9636\u6BB5\u6838\u5FC3\u7ADE\u4E89\u529B\u6765\u6E90\u4E4B\u4E00", options: { fontSize: 13, color: C.textLight } },
    ], { x: 0.7, y: 4.58, w: 8.6, h: 0.8, align: "center", margin: 0 });
  }

  // ═══════════════════════════════════════════
  // SLIDE 17 — Action Items
  // ═══════════════════════════════════════════
  {
    const s = pres.addSlide();
    s.background = { color: C.bgDark };
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.04, fill: { color: C.primary } });
    s.addText("CHAPTER 07", { x: 0.6, y: 0.25, w: 3, h: 0.4, fontSize: 11, fontFace: "Calibri", color: C.primary, bold: true, charSpacing: 4, margin: 0 });
    s.addText("\u4F18\u5148\u884C\u52A8\u5EFA\u8BAE", { x: 0.6, y: 0.6, w: 8, h: 0.55, fontSize: 26, fontFace: "Calibri", color: C.white, bold: true, margin: 0 });

    const actions = [
      { pri: "P0", action: "\u6838\u5FC3\u540C\u4E8B\u5B8C\u6210\u63A5\u5165 + \u6536\u96C6 2-4 \u5468\u4F7F\u7528\u53CD\u9988", time: "\u7ACB\u5373", value: "\u9A8C\u8BC1 + \u8FED\u4EE3", color: C.accent5 },
      { pri: "P1", action: "\u4E3A Butler \u56E2\u961F\u8865\u5145 3-5 \u4EFD SOP \u5230 Obsidian", time: "2 \u5468\u5185", value: "AI \u8F93\u51FA\u8D28\u91CF\u7FFB\u500D", color: C.accent4 },
      { pri: "P2", action: "\u542F\u7528 hr_watcher.py \u5B9E\u65F6\u540C\u6B65", time: "1 \u4E2A\u6708\u5185", value: "\u77E5\u8BC6\u66F4\u65B0\u96F6\u5EF6\u8FDF", color: C.primary },
      { pri: "P3", action: "\u5BF9\u63A5 Claude Agent Teams \u591A\u5B9E\u4F8B\u7F16\u6392", time: "3 \u4E2A\u6708\u5185", value: "\u4E32\u884C\u2192\u5E76\u884C", color: C.accent },
      { pri: "P4", action: "\u8F93\u51FA\u65B9\u6CD5\u8BBA\u767D\u76AE\u4E66 / \u884C\u4E1A\u5206\u4EAB", time: "\u6301\u7EED", value: "\u884C\u4E1A\u5F71\u54CD\u529B", color: C.accent2 },
    ];

    actions.forEach((a, i) => {
      const y = 1.3 + i * 0.82;
      s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y, w: 9.0, h: 0.68, fill: { color: C.bgCard }, shadow: mkShadow() });
      s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y, w: 0.06, h: 0.68, fill: { color: a.color } });
      // Priority badge
      s.addShape(pres.shapes.RECTANGLE, { x: 0.8, y: y + 0.15, w: 0.6, h: 0.38, fill: { color: a.color } });
      s.addText(a.pri, { x: 0.8, y: y + 0.15, w: 0.6, h: 0.38, fontSize: 12, fontFace: "Calibri", color: C.white, bold: true, align: "center", valign: "middle", margin: 0 });
      // Action
      s.addText(a.action, { x: 1.6, y: y + 0.05, w: 5, h: 0.3, fontSize: 13, fontFace: "Calibri", color: C.white, bold: true, margin: 0 });
      s.addText(a.time, { x: 1.6, y: y + 0.35, w: 2, h: 0.25, fontSize: 11, fontFace: "Calibri", color: C.textMuted, margin: 0 });
      s.addText(a.value, { x: 7.5, y: y + 0.15, w: 1.8, h: 0.35, fontSize: 12, fontFace: "Calibri", color: a.color, align: "right", margin: 0 });
    });
  }

  // ═══════════════════════════════════════════
  // SLIDE 18 — Thank You
  // ═══════════════════════════════════════════
  {
    const s = pres.addSlide();
    s.background = { color: C.bgDark };
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.04, fill: { color: C.primary } });

    s.addImage({ data: icons.brain, x: 4.5, y: 1.2, w: 1, h: 1 });
    s.addText("THANK YOU", {
      x: 0.5, y: 2.4, w: 9, h: 0.8, fontSize: 40, fontFace: "Calibri",
      color: C.white, bold: true, align: "center", charSpacing: 8, margin: 0
    });
    s.addShape(pres.shapes.LINE, { x: 3.5, y: 3.3, w: 3, h: 0, line: { color: C.primary, width: 1.5 } });
    s.addText("\u6784\u5EFA AI Native \u7EC4\u7EC7\uFF0C\u8BA9\u77E5\u8BC6\u6C38\u4E0D\u6D41\u5931", {
      x: 0.5, y: 3.5, w: 9, h: 0.5, fontSize: 18, fontFace: "Calibri",
      color: C.textLight, align: "center", margin: 0
    });

    s.addText([
      { text: "Graphify \u667A\u56CA\u56E2 + \u5185\u5BB9\u8FD0\u8425\u56E2\u961F \u7F16\u5236", options: { breakLine: true, fontSize: 12, color: C.textMuted } },
      { text: "2026 \u5E74 4 \u6708", options: { fontSize: 12, color: C.textMuted } },
    ], { x: 0.5, y: 4.3, w: 9, h: 0.7, align: "center" });

    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 5.325, w: 10, h: 0.3, fill: { color: C.primary, transparency: 15 } });
  }

  // ═══════════════════════════════════════════
  // Write file
  // ═══════════════════════════════════════════
  const outputPath = process.argv[2] || "AI_Team_System_Report.pptx";
  await pres.writeFile({ fileName: outputPath });
  console.log("PPTX generated: " + outputPath);
}

main().catch(e => { console.error(e); process.exit(1); });
