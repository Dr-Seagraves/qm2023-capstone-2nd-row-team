const path = require('path');
const pptxgen = require('pptxgenjs');

const pptx = new pptxgen();
pptx.layout = 'LAYOUT_WIDE';
pptx.author = '2nd Row Team';
pptx.company = 'QM 2023 Capstone';
pptx.subject = 'Final investment memo presentation';
pptx.title = 'Consumer and Investor Sentiment as a Timing Signal for U.S. Equity Returns';
pptx.lang = 'en-US';

const colors = {
  navy: '0F2747',
  blue: '163B63',
  teal: '0C9DA5',
  mint: 'BFE9E4',
  cream: 'F6F1E8',
  sand: 'E7DDCF',
  charcoal: '243447',
  white: 'FFFFFF',
  gray: '6C7A89',
  line: 'D7DDE4',
  softBlue: 'EAF2F8',
  softTeal: 'E6F7F6',
  softGold: 'FFF3D6',
  accentRed: 'C95D4B',
  accentGreen: '2F8F5B',
};

const figuresDir = path.resolve(__dirname, '..', 'results', 'figures');
const outPath = path.resolve(__dirname, '..', 'results', 'reports', 'Final_Investment_Memo_Presentation.pptx');

const img = (name) => path.join(figuresDir, name);

function addFooter(slide, n, dark = false) {
  slide.addText(`2nd Row Team | ${n}/10`, {
    x: 8.35, y: 7.05, w: 1.35, h: 0.18,
    fontFace: 'Calibri', fontSize: 9, color: dark ? 'DDE7F2' : colors.gray,
    align: 'right', margin: 0,
  });
}

function addTitle(slide, title, kicker, dark = false) {
  slide.addText(kicker, {
    x: 0.55, y: 0.4, w: 2.1, h: 0.34,
    fontFace: 'Calibri', fontSize: 11, bold: true,
    color: dark ? colors.navy : colors.teal,
    fill: { color: dark ? colors.mint : colors.softTeal },
    margin: 0.06,
    align: 'center',
    valign: 'mid',
    shape: pptx.ShapeType.roundRect,
    line: { color: dark ? colors.mint : colors.softTeal, transparency: 100 },
  });

  slide.addText(title, {
    x: 0.55, y: 0.82, w: 8.6, h: 0.7,
    fontFace: 'Georgia', fontSize: 24, bold: true,
    color: dark ? colors.white : colors.navy,
    margin: 0,
  });

  slide.addShape(pptx.ShapeType.line, {
    x: 0.55, y: 1.52, w: 9.0, h: 0,
    line: { color: dark ? colors.mint : colors.teal, width: 1.2, transparency: 25 },
  });
}

function addCard(slide, x, y, w, h, fill, title, body, opts = {}) {
  const isDark = !!opts.dark;
  slide.addShape(pptx.ShapeType.roundRect, {
    x, y, w, h,
    rectRadius: 0.08,
    fill: { color: fill },
    line: { color: opts.line || fill, transparency: 100 },
    shadow: opts.shadow || { type: 'outer', color: '000000', blur: 2, angle: 45, offset: 1, opacity: 0.12 },
  });
  slide.addText(title, {
    x: x + 0.18, y: y + 0.14, w: w - 0.36, h: 0.28,
    fontFace: 'Georgia', fontSize: 15, bold: true,
    color: isDark ? colors.white : colors.navy,
    margin: 0,
  });
  slide.addText(body, {
    x: x + 0.18, y: y + 0.46, w: w - 0.36, h: h - 0.58,
    fontFace: 'Calibri', fontSize: 12,
    color: isDark ? 'F4F7FB' : colors.charcoal,
    margin: 0,
    valign: 'top',
    breakLine: false,
  });
}

function addStat(slide, x, y, w, h, value, label, fill, textColor = colors.navy) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x, y, w, h,
    rectRadius: 0.08,
    fill: { color: fill },
    line: { color: fill, transparency: 100 },
  });
  slide.addText(value, {
    x: x + 0.08, y: y + 0.12, w: w - 0.16, h: 0.36,
    fontFace: 'Georgia', fontSize: 24, bold: true,
    color: textColor, align: 'center', margin: 0,
  });
  slide.addText(label, {
    x: x + 0.1, y: y + 0.52, w: w - 0.2, h: h - 0.56,
    fontFace: 'Calibri', fontSize: 11, color: colors.gray, align: 'center', margin: 0,
  });
}

function addBulletBlock(slide, x, y, w, h, title, bullets, opts = {}) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x, y, w, h,
    rectRadius: 0.05,
    fill: { color: opts.fill || colors.white },
    line: { color: opts.line || colors.line, width: 1 },
    shadow: opts.shadow || { type: 'outer', color: '000000', blur: 1, angle: 45, offset: 1, opacity: 0.08 },
  });
  slide.addText(title, {
    x: x + 0.16, y: y + 0.12, w: w - 0.32, h: 0.24,
    fontFace: 'Georgia', fontSize: 14, bold: true, color: colors.navy, margin: 0,
  });
  const text = bullets.map((bullet, index) => ({ text: bullet, options: { bullet: { indent: 14 }, breakLine: index < bullets.length - 1 } }));
  slide.addText(text, {
    x: x + 0.18, y: y + 0.42, w: w - 0.36, h: h - 0.52,
    fontFace: 'Calibri', fontSize: 12, color: colors.charcoal, margin: 0,
    paraSpaceAfterPt: 6,
  });
}

function notes(text) {
  return text.trim();
}

// Slide 1
{
  const slide = pptx.addSlide();
  slide.background = { color: colors.navy };
  slide.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: 10, h: 5.625, fill: { color: colors.navy }, line: { color: colors.navy, transparency: 100 } });
  slide.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: 0.22, h: 5.625, fill: { color: colors.teal }, line: { color: colors.teal, transparency: 100 } });
  slide.addShape(pptx.ShapeType.ellipse, { x: 7.9, y: 0.55, w: 1.35, h: 1.35, fill: { color: colors.teal, transparency: 70 }, line: { color: colors.teal, transparency: 100 } });
  slide.addShape(pptx.ShapeType.ellipse, { x: 8.45, y: 1.35, w: 0.95, h: 0.95, fill: { color: colors.mint, transparency: 72 }, line: { color: colors.mint, transparency: 100 } });
  slide.addText('Consumer and Investor Sentiment\nas a Timing Signal for U.S. Equity Returns', {
    x: 0.75, y: 1.1, w: 6.2, h: 1.25,
    fontFace: 'Georgia', fontSize: 26, bold: true, color: colors.white, margin: 0,
  });
  slide.addText('Final investment memo presentation | M1, M2, M3, and M3v2', {
    x: 0.78, y: 2.55, w: 5.3, h: 0.32,
    fontFace: 'Calibri', fontSize: 14, color: 'D7E3F0', margin: 0,
  });
  slide.addText('2nd Row Team: Steffi Brewer, Nicholas Langkamp, Katrina Baiza', {
    x: 0.78, y: 2.95, w: 5.6, h: 0.28,
    fontFace: 'Calibri', fontSize: 12, color: 'D7E3F0', margin: 0,
  });
  addStat(slide, 6.95, 2.0, 1.1, 0.9, '252', 'monthly obs.', colors.softTeal);
  addStat(slide, 8.15, 2.0, 1.1, 0.9, '0', 'missing cells', colors.softBlue);
  addStat(slide, 7.55, 3.02, 1.1, 0.9, '52k', 'firm-years', colors.softGold);
  slide.addText('The memo treats sentiment as a regime filter, not a standalone timing rule.', {
    x: 0.78, y: 4.55, w: 7.1, h: 0.35,
    fontFace: 'Calibri', fontSize: 12, italic: true, color: 'EAF2F8', margin: 0,
  });
  slide.addText('M1 → M2 → M3 → M3v2', {
    x: 8.0, y: 4.95, w: 1.5, h: 0.2,
    fontFace: 'Calibri', fontSize: 10, bold: true, color: 'D7E3F0', align: 'right', margin: 0,
  });
  slide.addNotes(notes(`Open by framing the question simply: do consumer and investor sentiment help timing equity returns? Emphasize that this is a project story that starts with clean data, moves through exploratory evidence, and ends with a more nuanced investment recommendation. Do not lead with econometric jargon; lead with the decision context.`));
  addFooter(slide, 1, true);
}

// Slide 2
{
  const slide = pptx.addSlide();
  slide.background = { color: colors.cream };
  addTitle(slide, 'What we found in one sentence', 'Executive Summary');
  addCard(slide, 0.55, 1.9, 2.95, 2.3, colors.white, 'Broad market', 'Sentiment is useful, but it is not a strong standalone timing rule for the overall market. The aggregate M3 coefficients were small and weak.', { line: colors.line });
  addCard(slide, 3.5, 1.9, 2.95, 2.3, colors.softTeal, 'Where the signal shows up', 'The stronger effect appears in crisis transitions and in smaller, more sentiment-sensitive firms. That is where funding conditions and risk appetite matter most.', { line: colors.softTeal });
  addCard(slide, 6.45, 1.9, 2.95, 2.3, colors.softGold, 'Decision rule', 'Use sentiment as a regime overlay. Tilt risk exposure within equities, but do not rely on it to predict the next month of the market by itself.', { line: colors.softGold });
  slide.addShape(pptx.ShapeType.chevron, { x: 4.4, y: 4.65, w: 1.2, h: 0.42, fill: { color: colors.teal }, line: { color: colors.teal, transparency: 100 } });
  slide.addText('from signal to allocation', { x: 3.4, y: 4.7, w: 3.3, h: 0.2, fontFace: 'Calibri', fontSize: 11, bold: true, color: colors.gray, align: 'center', margin: 0 });
  slide.addNotes(notes(`Use this slide as the non-technical headline. State that the project did not uncover a simple buy-sell rule for the whole market, but it did uncover a more economically interesting regime story. Mention that AAII positioning is closer to market moves than broad consumer confidence, and that the later firm-panel model strengthens the interpretation.`));
  addFooter(slide, 2);
}

// Slide 3
{
  const slide = pptx.addSlide();
  slide.background = { color: colors.white };
  addTitle(slide, 'M1: Clean data was the foundation of the analysis', 'Data and sample construction');
  addBulletBlock(slide, 0.58, 1.86, 3.1, 3.1, 'Three source streams', [
    'Michigan consumer sentiment from FRED',
    'AAII weekly investor sentiment, manually collected',
    'Kenneth R. French factor data for market controls',
  ], { fill: colors.softBlue });
  slide.addImage({ path: img('final_panel_overview.png'), x: 3.95, y: 1.86, w: 5.45, h: 3.1, sizing: { type: 'contain', w: 5.45, h: 3.1 } });
  addStat(slide, 0.62, 5.1, 1.25, 0.82, '0', 'missing cells', colors.softTeal);
  addStat(slide, 1.95, 5.1, 1.55, 0.82, '2004-2024', 'analysis window', colors.softGold);
  addStat(slide, 3.65, 5.1, 1.5, 0.82, 'Month-end', 'alignment rule', colors.softBlue);
  slide.addText('Why month-end matters: it aligns investor mood with pricing horizons and avoids smoothing away the last signal in the month.', {
    x: 5.35, y: 5.15, w: 4.0, h: 0.4,
    fontFace: 'Calibri', fontSize: 11.5, color: colors.charcoal, margin: 0,
  });
  slide.addNotes(notes(`Walk through the data pipeline. Explain that the M1 result matters because the later slides rely on a merged panel with no missing cells. Emphasize the month-end AAII aggregation choice as an economic decision, not just a coding choice. If someone asks why no outlier trimming, say the crisis episodes are exactly what investors need the model to understand.`));
  addFooter(slide, 3);
}

// Slide 4
{
  const slide = pptx.addSlide();
  slide.background = { color: colors.cream };
  addTitle(slide, 'M2: The EDA pointed to a short-run sentiment channel', 'Exploratory analysis');
  slide.addImage({ path: img('M2_01_correlation_heatmap.png'), x: 0.55, y: 1.85, w: 4.3, h: 3.2, sizing: { type: 'contain', w: 4.3, h: 3.2 } });
  addCard(slide, 5.0, 1.85, 4.45, 1.0, colors.white, 'Headline correlation', 'Market returns correlate weakly with Michigan sentiment (0.029) but more strongly with AAII bull-bear spread (0.461).', { line: colors.line });
  addCard(slide, 5.0, 3.0, 4.45, 0.95, colors.softTeal, 'Lag structure', 'The largest lagged relationship appeared around 12 months, which justified testing lagged sentiment in M3.', { line: colors.softTeal });
  addCard(slide, 5.0, 4.08, 4.45, 0.95, colors.softGold, 'Economic reading', 'Retail positioning seems to move faster than broad consumer confidence, especially near turning points.', { line: colors.softGold });
  slide.addText('Use sentiment as an indicator of market mood, but not as a one-variable forecast model.', { x: 5.0, y: 5.2, w: 4.3, h: 0.24, fontFace: 'Calibri', fontSize: 11.5, italic: true, color: colors.gray, margin: 0 });
  slide.addNotes(notes(`This slide should sound like the bridge between the clean data and the regression results. Point out that the EDA did not support a simple, linear, same-month timing rule. The useful takeaway is that AAII positioning is more immediate and that lagged sentiment relationships exist, but only weakly. That is why the later models used lags and regime checks.`));
  addFooter(slide, 4);
}

// Slide 5
{
  const slide = pptx.addSlide();
  slide.background = { color: colors.white };
  addTitle(slide, 'M3: The aggregate timing model did not produce stable alpha', 'Regression failure that still mattered');
  slide.addImage({ path: img('m3_market_model_fit.png'), x: 0.55, y: 1.82, w: 4.95, h: 3.35, sizing: { type: 'contain', w: 4.95, h: 3.35 } });
  addCard(slide, 5.75, 1.82, 3.7, 0.92, colors.softBlue, 'Direct signal', 'The broad-market sentiment coefficients were close to zero and statistically weak.', { line: colors.softBlue });
  addCard(slide, 5.75, 2.86, 3.7, 0.92, colors.softGold, 'Interpretation', 'The market appears to absorb sentiment quickly, or sentiment matters only through exposure and liquidity channels.', { line: colors.softGold });
  addCard(slide, 5.75, 3.9, 3.7, 1.1, colors.softTeal, 'Why this is useful', 'A null direct effect is not a dead end. It tells us the right question is not whether sentiment moves every monthly return, but when and where it changes risk pricing.', { line: colors.softTeal });
  slide.addText('M3 failure = boundary condition for the final recommendation', { x: 5.75, y: 5.18, w: 3.9, h: 0.2, fontFace: 'Calibri', fontSize: 11, bold: true, color: colors.gray, margin: 0 });
  slide.addNotes(notes(`Present this carefully: do not hide the fact that the aggregate M3 model was weak. Explain that the weak result is economically meaningful because it tells us sentiment is not a simple broad-market alpha signal. That shifts the investment use case from outright timing to regime and exposure management.`));
  addFooter(slide, 5);
}

// Slide 6
{
  const slide = pptx.addSlide();
  slide.background = { color: colors.cream };
  addTitle(slide, 'When markets break, sentiment becomes economically visible', 'Event study');
  slide.addImage({ path: img('time_series_event_study_window_bars.png'), x: 0.58, y: 1.82, w: 5.2, h: 3.55, sizing: { type: 'contain', w: 5.2, h: 3.55 } });
  addBulletBlock(slide, 6.0, 1.82, 3.05, 1.08, '2008 crisis', [
    'Cumulative abnormal returns were sharply negative across the event windows.',
    'This is a repricing of default risk, funding stress, and recession odds.',
  ], { fill: colors.white });
  addBulletBlock(slide, 6.0, 3.0, 3.05, 1.08, 'COVID shock', [
    'The immediate shock was severe, but the recovery path was faster than 2008.',
    'Markets interpreted the shock as temporary but severe, with policy support quickly priced in.',
  ], { fill: colors.white });
  addCard(slide, 6.0, 4.25, 3.05, 0.95, colors.softTeal, 'Economic message', 'Sentiment is most useful at inflection points, not in calm periods.', { line: colors.softTeal });
  slide.addNotes(notes(`Use the event study to connect the macro story to investor behavior. The point is not just that crashes were negative; it is that the abnormal-return pattern shows how sentiment and risk appetite matter most when the market has to reprice uncertainty quickly. Contrast the slower, deeper 2008 drawdown with the faster COVID shock and recovery.`));
  addFooter(slide, 6);
}

// Slide 7
{
  const slide = pptx.addSlide();
  slide.background = { color: colors.white };
  addTitle(slide, 'M3v2: The panel model says smaller firms are more sentiment-sensitive', 'Firm-level fixed effects');
  slide.addImage({ path: img('m3v2_group_trends.png'), x: 0.55, y: 1.85, w: 4.35, h: 3.15, sizing: { type: 'contain', w: 4.35, h: 3.15 } });
  slide.addImage({ path: img('m3v2_interaction_elasticity.png'), x: 5.05, y: 1.85, w: 4.35, h: 3.15, sizing: { type: 'contain', w: 4.35, h: 3.15 } });
  addStat(slide, 0.72, 5.25, 1.55, 0.72, '0.211*', 'sentiment x small-firm exposure', colors.softTeal);
  addStat(slide, 2.42, 5.25, 1.45, 0.72, 'p = 0.0418', 'statistical evidence', colors.softBlue);
  addCard(slide, 4.04, 5.12, 5.1, 0.92, colors.softGold, 'Economic reading', 'The same sentiment shock matters more for firms with weaker financing capacity and more exposure to investor mood.', { line: colors.softGold });
  slide.addNotes(notes(`Explain that this is the most policy-relevant or portfolio-relevant result. The panel model is not about the market average; it is about differential exposure. That makes the coefficient economically intuitive: smaller firms are more vulnerable to financing frictions, risk aversion, and shifts in investor willingness to hold risk.`));
  addFooter(slide, 7);
}

// Slide 8
{
  const slide = pptx.addSlide();
  slide.background = { color: colors.cream };
  addTitle(slide, 'Diagnostics: the stronger story is robustness, not overclaiming', 'Checks and caveats');
  slide.addImage({ path: img('m3v2_residuals_vs_fitted.png'), x: 0.55, y: 1.9, w: 4.05, h: 2.95, sizing: { type: 'contain', w: 4.05, h: 2.95 } });
  slide.addImage({ path: img('m3v2_coefficient_comparison.png'), x: 4.88, y: 1.9, w: 4.55, h: 2.95, sizing: { type: 'contain', w: 4.55, h: 2.95 } });
  addCard(slide, 0.65, 5.06, 2.1, 0.86, colors.softTeal, 'Breusch-Pagan', 'p = 0.8943', { line: colors.softTeal });
  addCard(slide, 2.9, 5.06, 2.0, 0.86, colors.softBlue, 'Max VIF', '1.31', { line: colors.softBlue });
  addCard(slide, 5.05, 5.06, 2.15, 0.86, colors.softGold, 'Placebo check', 'Weak pre-trend signal', { line: colors.softGold });
  addCard(slide, 7.38, 5.06, 1.98, 0.86, colors.white, 'Bottom line', 'No severe collinearity or heteroskedasticity red flags, but the aggregate alpha story stays weak.', { line: colors.line });
  slide.addNotes(notes(`This slide is where you show discipline. The diagnostics are important because they let you say the evidence is not being driven by obvious model pathologies. But also be honest that diagnostics are not the same as strong explanatory power. The result is robust enough to trust, yet not strong enough to overstate.`));
  addFooter(slide, 8);
}

// Slide 9
{
  const slide = pptx.addSlide();
  slide.background = { color: colors.navy };
  slide.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: 10, h: 5.625, fill: { color: colors.navy }, line: { color: colors.navy, transparency: 100 } });
  slide.addText('Recommendation: treat sentiment as a risk-budget overlay', {
    x: 0.65, y: 0.65, w: 7.9, h: 0.7,
    fontFace: 'Georgia', fontSize: 24, bold: true, color: colors.white, margin: 0,
  });
  slide.addText('Use it to adjust exposure, not to predict the next monthly return.', {
    x: 0.68, y: 1.35, w: 6.9, h: 0.3,
    fontFace: 'Calibri', fontSize: 13, color: 'D7E3F0', margin: 0,
  });
  addCard(slide, 0.7, 2.05, 2.85, 1.95, colors.white, 'If sentiment improves after a shock', 'Tilt modestly toward smaller, more sentiment-sensitive firms. That is where the panel model says the exposure is strongest.', { line: colors.white, shadow: { type: 'outer', color: '000000', blur: 2, angle: 45, offset: 1, opacity: 0.2 } });
  addCard(slide, 3.57, 2.05, 2.85, 1.95, colors.softTeal, 'If sentiment weakens in stress', 'Reduce exposure to the most financing-sensitive names and keep the core book diversified.', { line: colors.softTeal, shadow: { type: 'outer', color: '000000', blur: 2, angle: 45, offset: 1, opacity: 0.2 } });
  addCard(slide, 6.44, 2.05, 2.85, 1.95, colors.softGold, 'If the committee wants a hedge', 'Use quality or lower leverage tilts. Sentiment itself should not be carrying all the forecasting weight.', { line: colors.softGold, shadow: { type: 'outer', color: '000000', blur: 2, angle: 45, offset: 1, opacity: 0.2 } });
  slide.addShape(pptx.ShapeType.chevron, { x: 4.3, y: 4.55, w: 1.4, h: 0.45, fill: { color: colors.teal }, line: { color: colors.teal, transparency: 100 } });
  slide.addText('Regime shift → allocation tilt', { x: 3.3, y: 4.6, w: 3.4, h: 0.2, fontFace: 'Calibri', fontSize: 11, bold: true, color: 'D7E3F0', align: 'center', margin: 0 });
  slide.addNotes(notes(`Make the recommendation concrete. The audience should leave with a decision rule, not just a statistical conclusion. Stress that the recommendation is conditional: sentiment matters most when regimes are changing, especially for small firms and financing-sensitive names. The point is disciplined risk tilting, not market timing bravado.`));
  addFooter(slide, 9, true);
}

// Slide 10
{
  const slide = pptx.addSlide();
  slide.background = { color: colors.navy };
  slide.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: 10, h: 5.625, fill: { color: colors.navy }, line: { color: colors.navy, transparency: 100 } });
  slide.addShape(pptx.ShapeType.ellipse, { x: 7.95, y: 0.45, w: 1.55, h: 1.55, fill: { color: colors.teal, transparency: 68 }, line: { color: colors.teal, transparency: 100 } });
  slide.addShape(pptx.ShapeType.ellipse, { x: 6.95, y: 1.25, w: 1.0, h: 1.0, fill: { color: colors.mint, transparency: 78 }, line: { color: colors.mint, transparency: 100 } });
  slide.addText('Bottom line', {
    x: 0.7, y: 0.75, w: 2.0, h: 0.4,
    fontFace: 'Calibri', fontSize: 12, bold: true, color: 'D7E3F0', margin: 0,
  });
  slide.addText('Sentiment is a regime signal, not a magic timing machine.', {
    x: 0.7, y: 1.25, w: 7.4, h: 1.0,
    fontFace: 'Georgia', fontSize: 25, bold: true, color: colors.white, margin: 0,
  });
  slide.addText('That is the most honest and most useful conclusion for an investment committee.', {
    x: 0.72, y: 2.35, w: 6.6, h: 0.3,
    fontFace: 'Calibri', fontSize: 13, color: 'D7E3F0', margin: 0,
  });
  addCard(slide, 0.72, 3.1, 2.8, 1.25, colors.white, 'What to defend', 'Clean data, weak broad-market alpha, stronger small-firm exposure, and a cautious investment recommendation.', { line: colors.white });
  addCard(slide, 3.73, 3.1, 2.8, 1.25, colors.softTeal, 'What to customize', 'Insert your final names, any course-specific wording, and any additional academic citations before export.', { line: colors.softTeal });
  addCard(slide, 6.74, 3.1, 2.55, 1.25, colors.softGold, 'What to say if asked', 'The model is strongest as a risk-management overlay, not as a pure return predictor.', { line: colors.softGold });
  slide.addText('Questions?', { x: 0.72, y: 5.0, w: 2.0, h: 0.25, fontFace: 'Georgia', fontSize: 18, bold: true, color: colors.mint, margin: 0 });
  slide.addNotes(notes(`Close by repeating the practical takeaway: sentiment helps the committee manage risk, but it does not give a stable market-timing edge on its own. End with confidence, not hype. If there is time, invite questions about the M3 failure, because that is where the most honest methodological discussion will come from.`));
  addFooter(slide, 10, true);
}

async function main() {
  await pptx.writeFile({ fileName: outPath });
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});