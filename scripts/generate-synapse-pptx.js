const pptxgen = require("pptxgenjs");

// ── Janus Brand Colors ──
const C = {
  dark: "0A1628", card: "111D33", mid: "0F1D32",
  gold: "FCAD2A", blue: "013A7D", cyan: "028CDC",
  white: "FFFFFF", gray: "F7F8FA",
  text: "CBD5E1", muted: "8E95A7", dim: "5A6072",
  line: "1E293B", green: "52C41A", red: "F5222D",
};

const mkShadow = () => ({ type: "outer", blur: 4, offset: 1, angle: 135, color: "000000", opacity: 0.25 });

// ── Helpers ──
function addTopBar(s) {
  s.background = { color: C.dark };
  s.addShape("rect", { x: 0, y: 0, w: 10, h: 0.035, fill: { color: C.gold } });
}
function addLabel(s, text) {
  s.addText(text, { x: 0.6, y: 0.2, w: 5, h: 0.35, fontSize: 10, fontFace: "Calibri", color: C.gold, bold: true, charSpacing: 3 });
}
function addTitle(s, text, opts = {}) {
  s.addText(text, { x: 0.6, y: opts.y || 0.55, w: 8.8, h: opts.h || 0.6, fontSize: opts.size || 26, fontFace: "Calibri", color: C.white, bold: true, ...opts });
}
function addBody(s, text, y, opts = {}) {
  s.addText(text, { x: 0.6, y, w: 8.8, h: opts.h || 0.5, fontSize: opts.size || 13, fontFace: "Calibri", color: C.text, lineSpacingMultiple: 1.5, ...opts });
}
function addCard(s, x, y, w, h, borderColor) {
  s.addShape("rect", { x, y, w, h, fill: { color: C.card }, rectRadius: 0.08, shadow: mkShadow() });
  if (borderColor) s.addShape("rect", { x, y, w: 0.04, h, fill: { color: borderColor } });
}
function addChatBubble(s, y, speaker, text, isUser) {
  const bgColor = isUser ? "1A1508" : C.card;
  const borderColor = isUser ? C.gold : "1E293B";
  const labelColor = isUser ? C.gold : C.cyan;
  const x = isUser ? 2.0 : 0.6;
  const w = isUser ? 7.4 : 7.4;
  s.addShape("rect", { x, y, w, h: 0.04, fill: { color: borderColor } });
  s.addShape("rect", { x, y: y + 0.04, w, h: 0.85, fill: { color: bgColor }, rectRadius: 0.06 });
  s.addText(speaker, { x: x + 0.15, y: y + 0.06, w: 1.2, h: 0.3, fontSize: 10, fontFace: "Calibri", color: labelColor, bold: true });
  s.addText(text, { x: x + 0.15, y: y + 0.28, w: w - 0.3, h: 0.55, fontSize: 12, fontFace: "Calibri", color: C.text, lineSpacingMultiple: 1.4 });
}
function addAnnotation(s, y, text) {
  s.addShape("rect", { x: 0.6, y, w: 8.8, h: 0.5, fill: { color: "0D1B2A" }, line: { color: C.gold, dashType: "dash", width: 0.5 }, rectRadius: 0.06 });
  s.addText("💡 " + text, { x: 0.8, y, w: 8.4, h: 0.5, fontSize: 11, fontFace: "Calibri", color: C.gold, valign: "middle" });
}
function addExpert(s, y, role, text, score) {
  s.addShape("rect", { x: 0.6, y, w: 1.5, h: 0.45, fill: { color: C.card }, rectRadius: 0.04 });
  s.addText(role, { x: 0.6, y, w: 1.5, h: 0.45, fontSize: 10, fontFace: "Calibri", color: C.gold, bold: true, align: "center", valign: "middle" });
  const scoreText = score ? `  [${score}/5]` : "";
  s.addText(text + scoreText, { x: 2.3, y, w: 7.1, h: 0.45, fontSize: 11, fontFace: "Calibri", color: C.text, valign: "middle" });
}

async function main() {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_16x9";
  pres.author = "Lysander AI Team";
  pres.title = "Synapse — 用一场对话构建AI协作运营体系";

  // ═══════════════════════════════════════════
  // SLIDE 1 — 封面
  // ═══════════════════════════════════════════
  {
    const s = pres.addSlide();
    s.background = { fill: { type: "solid", color: C.dark } };
    s.addShape("rect", { x: 0, y: 5.3, w: 10, h: 0.04, fill: { type: "solid", color: C.gold } });
    s.addText("SYNAPSE", { x: 0.6, y: 1.0, w: 8.8, h: 0.8, fontSize: 52, fontFace: "Calibri", color: C.gold, bold: true, charSpacing: 8 });
    s.addText("用一场对话，构建AI协作运营体系", { x: 0.6, y: 1.9, w: 8.8, h: 0.6, fontSize: 24, fontFace: "Calibri", color: C.white, bold: true });
    s.addText("一个真实案例：如何通过与 AI CEO 的对话，一天内搭建 10 个团队、46 个 Agent 的完整运营体系，\n并在对话过程中不断发现问题、修正机制、持续进化", {
      x: 0.6, y: 2.7, w: 8.8, h: 0.8, fontSize: 13, fontFace: "Calibri", color: C.muted, lineSpacingMultiple: 1.6
    });
    s.addShape("line", { x: 0.6, y: 3.7, w: 2, h: 0, line: { color: C.gold, width: 1.5 } });
    s.addText("刘子杨  |  Janus Digital  |  2026.04.10", { x: 0.6, y: 3.9, w: 5, h: 0.35, fontSize: 12, fontFace: "Calibri", color: C.dim });
    s.addText([
      { text: "Harness Engineering", options: { fontSize: 10, color: C.gold } },
      { text: "   Multi-Agent   ", options: { fontSize: 10, color: C.cyan } },
      { text: "Claude Code", options: { fontSize: 10, color: C.green } },
    ], { x: 0.6, y: 4.4, w: 5, h: 0.3 });
  }

  // ═══════════════════════════════════════════
  // SLIDE 2 — 背景故事
  // ═══════════════════════════════════════════
  {
    const s = pres.addSlide(); addTopBar(s);
    addLabel(s, "背景");
    addTitle(s, "AI 技术发展太快，CEO 一个人管不过来");
    addBody(s, "Janus Digital 是一家建筑数字化资产运营管理公司。我们面临所有企业管理者都面临的挑战：", 1.3);
    // Big quote
    addCard(s, 0.6, 1.9, 8.8, 1.2, C.gold);
    s.addText(""我没有足够的时间逐一评估每个AI新工具。\n 我需要一个AI团队替我跟踪技术动态、做评估、做决策、做执行。\n 我只想提出目标，然后验收结果。"", {
      x: 0.9, y: 1.95, w: 8.2, h: 1.1, fontSize: 14, fontFace: "Calibri", color: C.white, italic: true, lineSpacingMultiple: 1.6
    });
    addBody(s, "于是，在一场持续数小时的 Claude Code 对话中，\n我与 AI CEO "Lysander" 一起，从零构建了一套完整的 AI 协作运营体系。", 3.3, { color: C.text });
    addBody(s, "以下是这场对话的真实过程 — 包括成功、失败、纠错和进化。", 4.1, { color: C.gold, bold: true, size: 14 });
  }

  // ═══════════════════════════════════════════
  // SLIDE 3 — 场景一：第一句话就暴露问题
  // ═══════════════════════════════════════════
  {
    const s = pres.addSlide(); addTopBar(s);
    addLabel(s, "场景一 · 角色定位");
    addTitle(s, "第一句话就暴露了问题");
    addBody(s, "我要求AI确认管理体系是否生效时，发现系统把"总裁"和"AI CEO"的角色混在一起。", 1.25, { size: 12 });
    addChatBubble(s, 1.75, "总裁 刘子杨", "我是总裁 刘子杨；Lysander 是CEO，把这个定位确认清楚", true);
    addChatBubble(s, 2.8, "Lysander AI", "明白。角色关系已全局更新：总裁刘子杨 = 最高决策者 / Lysander = AI管理者，向总裁汇报。\n已修改 5 个核心配置文件。", false);
    addAnnotation(s, 3.95, "启示：AI体系的第一步不是技术，是定义"谁对谁负责"。这一句纠正影响了后续所有流程设计。");
    addBody(s, "这看似简单的一步，实际上定义了整个体系的权责基础。如果角色不清，后续的决策链、执行链都无从建立。", 4.65, { size: 11, color: C.dim });
  }

  // ═══════════════════════════════════════════
  // SLIDE 4 — 场景二：总裁的管理哲学
  // ═══════════════════════════════════════════
  {
    const s = pres.addSlide(); addTopBar(s);
    addLabel(s, "场景二 · 重构决策链");
    addTitle(s, ""我参与越少越好，我的判断不一定准确"");
    addBody(s, "当我提出要减少自己的参与时，这个指令彻底改变了体系的设计方向：", 1.25, { size: 12 });
    addChatBubble(s, 1.7, "总裁 刘子杨", "原则是我参与的越少越好，我的判断和决策不一定准确。\n更多时候应该引入专家评审和决策。我希望仅关注提出目标和需求，以及最终验收成果。", true);
    addBody(s, "Lysander 立即召集智囊团 4 位专家开评审会，对当前执行链和决策链做完整分析 ——", 2.85, { size: 12 });
    // Expert panel
    addExpert(s, 3.25, "战略分析师", "执行链有3个结构性问题：无程序化强制、跨会话状态丢失、简单任务开销过大", "");
    addExpert(s, 3.8, "决策顾问", "体系评分 — 设计完整性 8/10，强制执行力仅 3/10，跨会话连续性 2/10", "");
    addExpert(s, 4.35, "趋势洞察师", "预测执行链遵守度会随对话深度递减 — 不是AI偷懒，是架构没有强制检查点", "");
    addAnnotation(s, 4.95, "结果：智囊团提出三级改进方案（规则层+机制层+代码层），均分5.0全票通过，当天全部落地。");
  }

  // ═══════════════════════════════════════════
  // SLIDE 5 — 场景二续：四级决策 + 总裁纠错
  // ═══════════════════════════════════════════
  {
    const s = pres.addSlide(); addTopBar(s);
    addLabel(s, "场景二 · 决策体系的诞生与修正");
    addTitle(s, "四级决策体系 — 专家先于CEO决策");
    addBody(s, "体系建成后，我又发现了一个逻辑问题并即时纠正：", 1.25, { size: 12 });
    addChatBubble(s, 1.65, "总裁 刘子杨", "当前的四级决策体系对吗？我认为 L1自动 → L2专家 → L3 CEO → L4总裁 更合适", true);
    addBody(s, "一句话道破了关键逻辑：专业问题应该先过专家，CEO再基于专家建议做管理决策。", 2.65, { size: 12, color: C.gold });
    // Before/After comparison
    addCard(s, 0.6, 3.1, 4.2, 1.6, C.red);
    s.addText("修正前", { x: 0.8, y: 3.15, w: 2, h: 0.3, fontSize: 11, fontFace: "Calibri", color: C.red, bold: true });
    s.addText("L1 自动 → L2 CEO判断 → L3 专家评审 → L4 总裁\n\n问题：CEO在没有专家分析的情况下\n就做了判断，可能拍脑袋决策", { x: 0.8, y: 3.45, w: 3.8, h: 1.2, fontSize: 11, fontFace: "Calibri", color: C.text, lineSpacingMultiple: 1.5 });
    addCard(s, 5.2, 3.1, 4.2, 1.6, C.green);
    s.addText("修正后", { x: 5.4, y: 3.15, w: 2, h: 0.3, fontSize: 11, fontFace: "Calibri", color: C.green, bold: true });
    s.addText("L1 自动 → L2 专家评审 → L3 CEO决策 → L4 总裁\n\nCEO的每个决策都有专家分析做支撑\n专业的事先过专家，不拍脑袋", { x: 5.4, y: 3.45, w: 3.8, h: 1.2, fontSize: 11, fontFace: "Calibri", color: C.text, lineSpacingMultiple: 1.5 });
    addAnnotation(s, 4.9, "启示：体系设计不是一次成型的。总裁的"挑刺"恰恰是体系进化的驱动力。");
  }

  // ═══════════════════════════════════════════
  // SLIDE 6 — 场景三：情报系统
  // ═══════════════════════════════════════════
  {
    const s = pres.addSlide(); addTopBar(s);
    addLabel(s, "场景三 · 每日情报系统");
    addTitle(s, "从一句需求到全自动情报管道");
    addChatBubble(s, 1.2, "总裁 刘子杨", "AI技术发展太快，我没时间看所有内容。目标：每天收到经过专业AI专家结合我日常工作\n整理出来对我有价值的专业分析报告，经过智囊团审查，生成HTML并通知我。", true);
    addBody(s, "Lysander 接到这个目标后的执行过程：", 2.3, { size: 12 });
    // Timeline steps
    const steps = [
      "新建 AI技术研究员（Graphify第6名成员），定义能力标准",
      "开发 generate-daily-intelligence.py HTML报告生成器",
      "搜索5组AI前沿动态，手动生成首期报告验证效果",
      "创建远程定时任务（每天8am Dubai自动运行）",
      "总裁验收首期报告："质量完全符合要求，非常棒"",
    ];
    steps.forEach((step, i) => {
      const y = 2.75 + i * 0.42;
      s.addShape("ellipse", { x: 0.7, y: y + 0.12, w: 0.12, h: 0.12, fill: { color: C.gold } });
      s.addText(`${i+1}. ${step}`, { x: 1.0, y, w: 8.4, h: 0.38, fontSize: 12, fontFace: "Calibri", color: i === 4 ? C.gold : C.text });
    });
    addAnnotation(s, 4.95, "从需求到全自动管道只用了一个对话回合。总裁提出目标，AI团队完成从设计到部署的全流程。");
  }

  // ═══════════════════════════════════════════
  // SLIDE 7 — 场景四：情报变行动
  // ═══════════════════════════════════════════
  {
    const s = pres.addSlide(); addTopBar(s);
    addLabel(s, "场景四 · 从发现到落地");
    addTitle(s, ""报告不是用来看的，是用来执行的"");
    addChatBubble(s, 1.2, "总裁 刘子杨", "拿到的报告有很多建议，但这些工作需要专业评估、评审，批准后需要有执行者完成。\n我希望整个工作由多个专业AI Agent成员完成。", true);
    addBody(s, "于是建立了"情报行动管线" — 每条建议经过4专家评审后才能执行：", 2.25, { size: 12 });
    // Score table
    const rows = [
      ["CLAUDE.md→Harness Configuration", "5", "4", "5", "5", "4.75", "✓ 批准"],
      ["创建Harness方法论文档", "5", "4", "5", "—", "4.67", "✓ 批准"],
      ["QA自动化评分引擎", "4", "4", "5", "4", "4.25", "✓ 批准"],
      ["NVIDIA OpenShell", "—", "—", "—", "—", "—", "暂缓"],
    ];
    const headers = [["建议", "战略", "决策", "趋势", "技术", "均分", "决定"]];
    s.addTable(headers.concat(rows), {
      x: 0.6, y: 2.7, w: 8.8,
      colW: [3.5, 0.7, 0.7, 0.7, 0.7, 0.8, 1.2],
      border: { type: "solid", pt: 0.5, color: C.line },
      rowH: [0.35, 0.35, 0.35, 0.35, 0.35],
      color: C.text, fontSize: 11, fontFace: "Calibri",
      autoPage: false,
    });
    addBody(s, "评审规则：均分≥4.0 批准 / 3.0-3.9 有条件批准 / <3.0 暂缓 / 任一专家=1 一票否决", 4.55, { size: 11, color: C.dim });
    addAnnotation(s, 4.9, "3条建议通过评审后，由 Harness Ops 团队按角色分工执行，每条都有具体的执行者和交付物。");
  }

  // ═══════════════════════════════════════════
  // SLIDE 8 — 场景五：发现Bug（对话过程）
  // ═══════════════════════════════════════════
  {
    const s = pres.addSlide(); addTopBar(s);
    addLabel(s, "场景五 · 在实践中发现Harness的漏洞");
    addTitle(s, ""刚才谁执行的？是AI团队吗？"");
    addBody(s, "总裁的这句追问，揭开了体系中一个深层问题：", 1.25, { size: 12 });
    addChatBubble(s, 1.65, "总裁 刘子杨", "刚才谁执行的？是AI团队吗？", true);
    addChatBubble(s, 2.5, "Lysander AI", "直说：不是。是我一个人执行的，没有体现团队分工。\n这和之前指出的"行动管线没有执行团队"是同一个问题。", false);
    addChatBubble(s, 3.55, "总裁 刘子杨", "不要光是期望，要强制按照流程来干活。要充分分析原因。", true);
    addBody(s, "这个问题反复出现了3次 — 不是态度问题，是机制问题。", 4.5, { size: 12, color: C.red });
    addAnnotation(s, 4.9, "体系不靠"下次注意"，靠制度强制。这是整场对话中最重要的认知转折点。");
  }

  // ═══════════════════════════════════════════
  // SLIDE 9 — 场景五续：Harness方法论的验证
  // ═══════════════════════════════════════════
  {
    const s = pres.addSlide(); addTopBar(s);
    addLabel(s, "场景五 · Harness Engineering 的实战验证");
    addTitle(s, "Guide 有了，Sensor 呢？");
    addBody(s, "这个问题恰好验证了 Harness Engineering（2026年AI工程新范式）的核心概念：", 1.25, { size: 12 });
    // Two-column comparison
    addCard(s, 0.6, 1.7, 4.2, 2.0, C.red);
    s.addText("只有 Guides（前馈控制）", { x: 0.8, y: 1.75, w: 3.5, h: 0.3, fontSize: 13, fontFace: "Calibri", color: C.red, bold: true });
    s.addText("CLAUDE.md 写了"路由到团队"\n但没有任何机制检查是否真的路由了\n\n纸上的规则 ≠ 执行的保证\n\nLysander 可以无阻碍地\n跳过团队派单直接干活", { x: 0.8, y: 2.1, w: 3.8, h: 1.5, fontSize: 11, fontFace: "Calibri", color: C.text, lineSpacingMultiple: 1.5 });
    addCard(s, 5.2, 1.7, 4.2, 2.0, C.green);
    s.addText("Guide + Sensor 双保险", { x: 5.4, y: 1.75, w: 3.5, h: 0.3, fontSize: 13, fontFace: "Calibri", color: C.green, bold: true });
    s.addText("Guide：强制团队派单表\n（执行前必须输出"谁做什么"）\n\nSensor：执行审计师前置检查\n（没有派单就阻止执行）\n\n与开场问候同级，不可省略", { x: 5.4, y: 2.1, w: 3.8, h: 1.5, fontSize: 11, fontFace: "Calibri", color: C.text, lineSpacingMultiple: 1.5 });
    addCard(s, 0.6, 4.0, 8.8, 0.6, C.gold);
    s.addText("Harness Engineering 核心公式：Agent = Model + Harness\n模型不变，改变 Harness（环境、约束、反馈），Agent 的行为就改变。竞争力不在模型，在 Harness。", {
      x: 0.8, y: 4.02, w: 8.4, h: 0.55, fontSize: 11, fontFace: "Calibri", color: C.white, lineSpacingMultiple: 1.5
    });
    addBody(s, "来源：Martin Fowler / Red Hat / Anthropic, 2026", 4.8, { size: 10, color: C.dim });
  }

  // ═══════════════════════════════════════════
  // SLIDE 10 — 插曲：视觉升级
  // ═══════════════════════════════════════════
  {
    const s = pres.addSlide(); addTopBar(s);
    addLabel(s, "插曲 · 一个有趣的小案例");
    addTitle(s, ""参考一下官网的视觉效果"");
    addBody(s, "总裁随口提了一句"参考 janusd.com 的视觉效果"，AI团队的反应：", 1.25, { size: 12 });
    addChatBubble(s, 1.65, "Lysander AI", "网站是动态渲染的，CSS无法直接提取。换一个方式 —— 抓取 Logo SVG 源码。", false);
    addBody(s, "AI 团队从一个 SVG 文件中逆向工程出完整的品牌色彩体系：", 2.65, { size: 12 });
    // Color swatches
    const colors = [
      { color: "FCAD2A", name: "Gold 品牌金" },
      { color: "013A7D", name: "Deep Blue" },
      { color: "028CDC", name: "Cyan 天蓝" },
      { color: "0A1628", name: "Dark BG" },
    ];
    colors.forEach((c, i) => {
      const x = 0.6 + i * 2.3;
      s.addShape("rect", { x, y: 3.1, w: 0.45, h: 0.45, fill: { color: c.color }, rectRadius: 0.06 });
      s.addText(`#${c.color}\n${c.name}`, { x: x + 0.6, y: 3.1, w: 1.5, h: 0.45, fontSize: 10, fontFace: "Calibri", color: C.text });
    });
    addBody(s, "然后用这套色彩重写了报告模板 — 头部、表格、优先级标签、页脚全部对齐品牌视觉。", 3.75, { size: 12 });
    addAnnotation(s, 4.2, "这就是AI团队的工作方式：给它一个URL，它自己完成调研→提取→设计→实现→验证。整个过程无需人工干预。");
  }

  // ═══════════════════════════════════════════
  // SLIDE 11 — 场景六：HR审计的震撼
  // ═══════════════════════════════════════════
  {
    const s = pres.addSlide(); addTopBar(s);
    addLabel(s, "场景六 · HR管理体系");
    addTitle(s, "首次审计结果：" + '"触目惊心"');
    addBody(s, "总裁要求建立HR管理体系后，HR Director 上任后的第一次全量审计结果：", 1.25, { size: 12 });
    addCard(s, 0.6, 1.7, 4.2, 1.4, C.red);
    s.addText("审计发现", { x: 0.8, y: 1.75, w: 2, h: 0.3, fontSize: 12, fontFace: "Calibri", color: C.red, bold: true });
    s.addText("· Janus团队 6人全部 0 分（无元数据）\n· Growth团队 2人全部 0 分（Schema缺失）\n· 三种不同的卡片格式混用\n· 大量C级能力描述（"项目管理"、"知识沉淀"）\n· 全员平均分仅 64.1/100", {
      x: 0.8, y: 2.1, w: 3.8, h: 1.0, fontSize: 11, fontFace: "Calibri", color: C.text, lineSpacingMultiple: 1.5
    });
    addCard(s, 5.2, 1.7, 4.2, 1.4, C.green);
    s.addText("建立的制度", { x: 5.4, y: 1.75, w: 2, h: 0.3, fontSize: 12, fontFace: "Calibri", color: C.green, bold: true });
    s.addText("· 强制Schema — 缺失必填项不得上岗\n· 能力分A/B/C级 — C级不合格\n· 入职审批 — 8项检查清单\n· 周度自动审计 — 每周一自动评分\n· 情报联动 — 新技术→自动更新能力", {
      x: 5.4, y: 2.1, w: 3.8, h: 1.0, fontSize: 11, fontFace: "Calibri", color: C.text, lineSpacingMultiple: 1.5
    });
    // Progress bars
    addBody(s, "四轮整治过程：", 3.3, { size: 12, bold: true, color: C.gold });
    const rounds = [["第一轮 · 发现问题", 64.1], ["第二轮 · 基础修复", 83.1], ["第三轮 · 提标至90分", 88.6], ["最终 · 全员达标", 93.8]];
    rounds.forEach((r, i) => {
      const y = 3.65 + i * 0.38;
      s.addText(r[0], { x: 0.6, y, w: 2.5, h: 0.3, fontSize: 10, fontFace: "Calibri", color: C.muted });
      s.addShape("rect", { x: 3.2, y: y + 0.08, w: 5 * (r[1]/100), h: 0.15, fill: { color: C.gold }, rectRadius: 0.03 });
      s.addShape("rect", { x: 3.2 + 5*(r[1]/100), y: y+0.08, w: 5*(1-r[1]/100), h: 0.15, fill: { color: C.line }, rectRadius: 0.03 });
      s.addText(String(r[1]), { x: 8.4, y, w: 1, h: 0.3, fontSize: 12, fontFace: "Calibri", color: C.gold, bold: true, align: "right" });
    });
    addAnnotation(s, 5.0, "从 64.1 到 93.8，不合格人数从 11 人降到 0。总裁又提出把合格线从60提到90 — "评分越高越好"。");
  }

  // ═══════════════════════════════════════════
  // SLIDE 12 — 场景七：命名风暴
  // ═══════════════════════════════════════════
  {
    const s = pres.addSlide(); addTopBar(s);
    addLabel(s, "场景七 · 头脑风暴现场");
    addTitle(s, "20个候选 → 5维评审 → Synapse");
    addBody(s, "为整套体系命名，Lysander 组织智囊团全员头脑风暴 ——", 1.25, { size: 12 });
    addExpert(s, 1.65, "关联发现", "5条隐喻路径挖掘（Janus品牌 / 神经系统 / 操作系统 / 建筑 / 数字孪生），产出20个候选", "");
    addExpert(s, 2.15, "趋势洞察师", "行业调研：避免"OS"后缀（太多人用）、"AI"前缀（无辨识度）。好名字 = 一个词能讲故事", "");
    addExpert(s, 2.65, "决策顾问", "5维度评审：品牌关联25% / 记忆度25% / 含义深度20% / 差异化15% / 扩展性15%", "");
    // Top 3 table
    s.addTable([
      ["候选", "品牌", "记忆", "含义", "差异", "扩展", "总分"],
      ["Janus Cortex", "5", "4", "5", "4", "4", "4.50"],
      ["Synapse ★", "3", "5", "5", "4", "4", "4.20"],
      ["Nexus", "3", "5", "4", "3", "5", "4.00"],
    ], {
      x: 0.6, y: 3.3, w: 8.8,
      colW: [2.5, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9],
      border: { type: "solid", pt: 0.5, color: C.line },
      rowH: [0.3, 0.3, 0.3, 0.3],
      color: C.text, fontSize: 11, fontFace: "Calibri",
      autoPage: false,
    });
    addBody(s, "总裁的选择 ——", 4.6, { size: 12 });
    s.addText("Synapse", { x: 3.5, y: 4.8, w: 3, h: 0.5, fontSize: 28, fontFace: "Calibri", color: C.gold, bold: true, align: "center" });
    addBody(s, "突触 — 神经元之间传递信号的关键节点。知识←突触→决策←突触→执行。", 5.0, { size: 11, color: C.muted, align: "center" });
  }

  // ═══════════════════════════════════════════
  // SLIDE 13 — 全景架构
  // ═══════════════════════════════════════════
  {
    const s = pres.addSlide(); addTopBar(s);
    addLabel(s, "SYNAPSE 全景");
    addTitle(s, "10 个团队 · 46 个 Agent · 5 个自动任务");
    // Stats row
    const stats = [["10", "专业团队"], ["46", "AI Agent"], ["93.8", "审计均分"], ["0", "不合格"], ["5", "自动任务"], ["24/7", "持续运转"]];
    stats.forEach((st, i) => {
      const x = 0.4 + i * 1.6;
      s.addText(st[0], { x, y: 1.2, w: 1.4, h: 0.55, fontSize: 28, fontFace: "Calibri", color: C.gold, bold: true, align: "center" });
      s.addText(st[1], { x, y: 1.7, w: 1.4, h: 0.3, fontSize: 10, fontFace: "Calibri", color: C.muted, align: "center" });
    });
    // Architecture diagram
    s.addText([
      { text: "Synapse 体系架构\n", options: { fontSize: 13, color: C.gold, bold: true, breakLine: true } },
      { text: "├── 记忆层 ── Obsidian 第二大脑 (OBS)\n", options: { fontSize: 11, color: C.text, breakLine: true } },
      { text: "├── 控制层 ── Harness Engineering (Guides + Sensors)\n", options: { fontSize: 11, color: C.text, breakLine: true } },
      { text: "├── 执行层 ── 10 个团队 46 个 AI Agent\n", options: { fontSize: 11, color: C.text, breakLine: true } },
      { text: "│    Graphify(6) · HR(2) · Harness Ops(4) · Butler(7)\n", options: { fontSize: 10, color: C.muted, breakLine: true } },
      { text: "│    RD(5) · OBS(4) · Content(4) · Growth(2) · Janus(6) · Stock(5)\n", options: { fontSize: 10, color: C.muted, breakLine: true } },
      { text: "├── 进化层 ── 情报闭环 (日报→评估→执行→报告)\n", options: { fontSize: 11, color: C.text, breakLine: true } },
      { text: "└── 决策层 ── L1自动 → L2专家 → L3 CEO → L4总裁", options: { fontSize: 11, color: C.text } },
    ], { x: 0.6, y: 2.2, w: 8.8, h: 2.8, fontFace: "Consolas", lineSpacingMultiple: 1.6 });
    addAnnotation(s, 5.0, "每天自动运转：6am任务恢复 → 8am情报日报 → 10am行动管线 → 每周一HR审计。总裁只看Slack通知。");
  }

  // ═══════════════════════════════════════════
  // SLIDE 14 — 核心洞察
  // ═══════════════════════════════════════════
  {
    const s = pres.addSlide();
    s.background = { color: C.dark };
    addLabel(s, "核心洞察");
    s.addText("AI 的竞争力不在模型本身，\n而在于你为它构建的\n环境、约束、反馈和组织。", {
      x: 0.6, y: 1.2, w: 8.8, h: 2.2, fontSize: 30, fontFace: "Calibri", color: C.white, lineSpacingMultiple: 1.6, italic: true
    });
    s.addShape("line", { x: 0.6, y: 3.6, w: 2, h: 0, line: { color: C.gold, width: 1.5 } });
    s.addText("模型人人可用。Harness 才是壁垒。", { x: 0.6, y: 3.8, w: 8, h: 0.5, fontSize: 18, fontFace: "Calibri", color: C.gold });
    s.addText("从今天的实践中验证的结论 — 不是理论，是我们一天内亲手搭建并反复修正的真实经历。", { x: 0.6, y: 4.4, w: 8, h: 0.4, fontSize: 12, fontFace: "Calibri", color: C.dim });
  }

  // ═══════════════════════════════════════════
  // SLIDE 15 — 结尾
  // ═══════════════════════════════════════════
  {
    const s = pres.addSlide();
    s.background = { fill: { type: "solid", color: C.dark } };
    s.addShape("rect", { x: 0, y: 5.3, w: 10, h: 0.04, fill: { type: "solid", color: C.gold } });
    s.addText("SYNAPSE", { x: 0.6, y: 1.5, w: 8.8, h: 0.8, fontSize: 44, fontFace: "Calibri", color: C.gold, bold: true, align: "center", charSpacing: 6 });
    s.addText("Janus Digital AI Operating Framework", { x: 0.6, y: 2.3, w: 8.8, h: 0.5, fontSize: 16, fontFace: "Calibri", color: C.muted, align: "center" });
    s.addShape("line", { x: 4, y: 3.0, w: 2, h: 0, line: { color: C.gold, width: 1.5 } });
    s.addText("Powered by Claude Code · Harness Engineering · Obsidian", { x: 0.6, y: 3.3, w: 8.8, h: 0.35, fontSize: 11, fontFace: "Calibri", color: C.dim, align: "center" });
    s.addText("刘子杨  |  Janus Digital  |  2026", { x: 0.6, y: 3.8, w: 8.8, h: 0.35, fontSize: 12, fontFace: "Calibri", color: C.muted, align: "center" });
  }

  // ── Save ──
  const outPath = "obs/generated-articles/2026-04-10-synapse-presentation.pptx";
  await pres.writeFile({ fileName: outPath });
  console.log(`Generated: ${outPath}`);
  console.log(`Slides: ${pres.slides.length}`);
}

main().catch(console.error);
