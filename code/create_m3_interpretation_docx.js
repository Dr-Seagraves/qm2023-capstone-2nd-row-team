const fs = require("fs");
const path = require("path");
const {
  AlignmentType,
  BorderStyle,
  Document,
  Footer,
  HeadingLevel,
  LevelFormat,
  PageBreak,
  PageNumber,
  Packer,
  Paragraph,
  ShadingType,
  Table,
  TableCell,
  TableOfContents,
  TableRow,
  TabStopPosition,
  TabStopType,
  TextRun,
  WidthType,
} = require("docx");

const PAGE_WIDTH = 12240;
const PAGE_HEIGHT = 15840;
const PAGE_MARGIN = 1440;
const CONTENT_WIDTH = PAGE_WIDTH - PAGE_MARGIN * 2;
const BORDER = { style: BorderStyle.SINGLE, size: 1, color: "CFCFCF" };
const CELL_MARGINS = { top: 80, bottom: 80, left: 120, right: 120 };

const outputPath = path.resolve(
  __dirname,
  "..",
  "results",
  "reports",
  "M3_interpretation.docx"
);

function inlineRuns(text, options = {}) {
  const parts = text.split(/(`[^`]+`|\*\*[^*]+\*\*)/g).filter(Boolean);
  return parts.map((part) => {
    if (part.startsWith("`") && part.endsWith("`")) {
      return new TextRun({
        text: part.slice(1, -1),
        font: "Courier New",
        size: options.size,
        color: options.color,
      });
    }

    if (part.startsWith("**") && part.endsWith("**")) {
      return new TextRun({
        text: part.slice(2, -2),
        bold: true,
        size: options.size,
        color: options.color,
      });
    }

    return new TextRun({
      text: part,
      bold: options.bold,
      italics: options.italics,
      size: options.size,
      color: options.color,
    });
  });
}

function paragraphFromText(text, options = {}) {
  return new Paragraph({
    children: inlineRuns(text, options),
    spacing: options.spacing || { after: 120, line: 276 },
    alignment: options.alignment,
    style: options.style,
    heading: options.heading,
    border: options.border,
    shading: options.shading,
    indent: options.indent,
    numbering: options.numbering,
    pageBreakBefore: options.pageBreakBefore,
  });
}

function bullet(text, level = 0) {
  return paragraphFromText(text, {
    numbering: { reference: "bullets", level },
    spacing: { after: 90, line: 276 },
  });
}

function numbered(text, level = 0) {
  return paragraphFromText(text, {
    numbering: { reference: "numbers", level },
    spacing: { after: 90, line: 276 },
  });
}

function tableCell(text, width, options = {}) {
  return new TableCell({
    width: { size: width, type: WidthType.DXA },
    borders: {
      top: BORDER,
      bottom: BORDER,
      left: BORDER,
      right: BORDER,
    },
    margins: CELL_MARGINS,
    shading: options.shading,
    children: [
      paragraphFromText(text, {
        bold: options.bold,
        spacing: { after: 0, line: 240 },
      }),
    ],
    verticalAlign: "center",
  });
}

function simpleTable(headers, rows, widths) {
  return new Table({
    width: { size: CONTENT_WIDTH, type: WidthType.DXA },
    columnWidths: widths,
    rows: [
      new TableRow({
        children: headers.map((header, index) =>
          tableCell(header, widths[index], {
            bold: true,
            shading: { fill: "DCE6F1", type: ShadingType.CLEAR },
          })
        ),
      }),
      ...rows.map(
        (row, rowIndex) =>
          new TableRow({
            children: row.map((value, index) =>
              tableCell(value, widths[index], {
                shading:
                  rowIndex % 2 === 0
                    ? { fill: "F8FAFC", type: ShadingType.CLEAR }
                    : undefined,
              })
            ),
          })
      ),
    ],
  });
}

const generatedOn = new Intl.DateTimeFormat("en-US", {
  year: "numeric",
  month: "long",
  day: "numeric",
}).format(new Date());

const doc = new Document({
  creator: "GitHub Copilot",
  title: "M3 Interpretation: Fixed Effects and Difference-in-Differences",
  description: "Professionally formatted DOCX version of the M3 interpretation report.",
  styles: {
    default: {
      document: {
        run: {
          font: "Arial",
          size: 22,
          color: "1F2933",
        },
      },
    },
    paragraphStyles: [
      {
        id: "Heading1",
        name: "Heading 1",
        basedOn: "Normal",
        next: "Normal",
        quickFormat: true,
        run: { size: 30, bold: true, font: "Arial", color: "123B5D" },
        paragraph: { spacing: { before: 280, after: 120 }, outlineLevel: 0 },
      },
      {
        id: "Heading2",
        name: "Heading 2",
        basedOn: "Normal",
        next: "Normal",
        quickFormat: true,
        run: { size: 26, bold: true, font: "Arial", color: "204A69" },
        paragraph: { spacing: { before: 220, after: 90 }, outlineLevel: 1 },
      },
      {
        id: "Heading3",
        name: "Heading 3",
        basedOn: "Normal",
        next: "Normal",
        quickFormat: true,
        run: { size: 24, bold: true, font: "Arial", color: "3B5D7A" },
        paragraph: { spacing: { before: 180, after: 80 }, outlineLevel: 2 },
      },
    ],
  },
  numbering: {
    config: [
      {
        reference: "bullets",
        levels: [
          {
            level: 0,
            format: LevelFormat.BULLET,
            text: "•",
            alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 720, hanging: 360 } } },
          },
          {
            level: 1,
            format: LevelFormat.BULLET,
            text: "○",
            alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 1080, hanging: 360 } } },
          },
        ],
      },
      {
        reference: "numbers",
        levels: [
          {
            level: 0,
            format: LevelFormat.DECIMAL,
            text: "%1.",
            alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 720, hanging: 360 } } },
          },
        ],
      },
    ],
  },
  sections: [
    {
      properties: {
        page: {
          size: { width: PAGE_WIDTH, height: PAGE_HEIGHT },
          margin: {
            top: PAGE_MARGIN,
            right: PAGE_MARGIN,
            bottom: PAGE_MARGIN,
            left: PAGE_MARGIN,
          },
        },
      },
      footers: {
        default: new Footer({
          children: [
            new Paragraph({
              tabStops: [
                { type: TabStopType.RIGHT, position: TabStopPosition.MAX },
              ],
              border: {
                top: { style: BorderStyle.SINGLE, size: 4, color: "93A4B5", space: 1 },
              },
              spacing: { before: 120, after: 0 },
              children: [
                new TextRun({ text: "M3 Interpretation Report", size: 18, color: "425466" }),
                new TextRun({ text: "\t" }),
                new TextRun({ text: "Page ", size: 18, color: "425466" }),
                new TextRun({ children: [PageNumber.CURRENT] }),
              ],
            }),
          ],
        }),
      },
      children: [
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { before: 900, after: 160 },
          children: [
            new TextRun({
              text: "M3 Interpretation",
              bold: true,
              size: 36,
              color: "123B5D",
            }),
          ],
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { after: 220 },
          children: [
            new TextRun({
              text: "Fixed Effects and Difference-in-Differences",
              italics: true,
              size: 24,
              color: "425466",
            }),
          ],
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          border: {
            bottom: { style: BorderStyle.SINGLE, size: 8, color: "123B5D", space: 1 },
          },
          spacing: { after: 280 },
          children: [new TextRun({ text: "Capstone Report Deliverable", size: 22, color: "52606D" })],
        }),
        paragraphFromText(
          "This document presents the M3 fixed-effects and difference-in-differences interpretation for the capstone analysis, including model structure, estimated effects, diagnostics, robustness checks, and generated outputs.",
          {
            alignment: AlignmentType.CENTER,
            spacing: { after: 240, line: 300 },
          }
        ),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { after: 120 },
          children: [
            new TextRun({ text: `Source: M3_interpretation.md`, size: 18, color: "52606D" }),
          ],
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { after: 260 },
          children: [
            new TextRun({ text: `Generated on ${generatedOn}`, size: 18, color: "52606D" }),
          ],
        }),
        new Paragraph({ children: [new PageBreak()] }),
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("Table of Contents")],
        }),
        new TableOfContents("Contents", {
          hyperlink: true,
          headingStyleRange: "1-3",
        }),
        new Paragraph({ children: [new PageBreak()] }),
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("What We Estimated")],
        }),
        numbered("Calendar-month fixed effects model for market returns"),
        bullet("Outcome: `mkt_ret`", 1),
        bullet("Key predictors: lagged Michigan sentiment and lagged AAII bull-bear spread", 1),
        bullet("Controls: `smb`, `hml`, `rmw`, `cma`", 1),
        bullet("Fixed effects: month-of-year dummies", 1),
        numbered("Model A: Two-way fixed effects (entity and time) on the long panel"),
        bullet("Outcome: standardized `value_z` in long-form panel", 1),
        bullet("Fixed effects: variable/entity dummies and date fixed effects", 1),
        bullet("Standard errors: clustered by entity (`variable`)", 1),
        bullet("Shock indicators: post-2008 and post-COVID", 1),
        numbered("Difference-in-differences model for shocks"),
        bullet("Treated group: sentiment series (`sentiment_michigan_ics`, AAII sentiment variables)", 1),
        bullet("Control group: market return and factor series", 1),
        bullet("Interactions: `treated_sentiment x post_gfc` and `treated_sentiment x post_covid`", 1),
        bullet("Date fixed effects included", 1),
        bullet("Standard errors: clustered by entity (`variable`)", 1),
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("Sample Sizes")],
        }),
        simpleTable(
          ["Model Slice", "Observations"],
          [
            ["Market fixed-effects model", "251"],
            ["Panel / DiD models", "3024"],
          ],
          [6360, 3000]
        ),
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("Main Economic Interpretation")],
        }),
        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("1) Predictive Return Model")],
        }),
        bullet("`sentiment_michigan_ics_l1`: coef = 0.0022, p = 0.9223, 95% CI [-0.0414, 0.0457]"),
        bullet("`bull_bear_spread_l1`: coef = -0.0063, p = 0.7255, 95% CI [-0.0414, 0.0288]"),
        bullet("`smb`: coef = 0.4568***, p = 0.0002, 95% CI [0.2144, 0.6991]"),
        bullet("`hml`: coef = 0.3643***, p = 0.0038, 95% CI [0.1179, 0.6107]"),
        bullet("`rmw`: coef = -0.2760, p = 0.1289, 95% CI [-0.6324, 0.0803]"),
        bullet("`cma`: coef = -0.6590***, p = 0.0010, 95% CI [-1.0520, -0.2660]"),
        paragraphFromText("Interpretation:", { bold: true, spacing: { after: 60, before: 80 } }),
        bullet("A positive lagged sentiment coefficient would mean stronger confidence last month is associated with higher return this month."),
        bullet("A negative lagged bull-bear spread coefficient would support a contrarian story: too much bullishness predicts softer next-month returns."),
        bullet("Factor coefficients capture whether common risk channels still explain returns after sentiment is added."),
        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("2) Entity Fixed Effects Shock Shifts")],
        }),
        bullet("`post_gfc`: coef = -0.5316, p = 0.2243, 95% CI [-1.3891, 0.3258]"),
        bullet("`post_covid`: coef = 0.0151, p = 0.9175, 95% CI [-0.2712, 0.3015]"),
        paragraphFromText("Interpretation:", { bold: true, spacing: { after: 60, before: 80 } }),
        bullet("The entity fixed-effects model asks whether the average standardized level of each series shifts after each macro shock, after controlling for each variable’s own baseline level."),
        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("3) DiD: Differential Effect on Sentiment vs Controls")],
        }),
        bullet("`treated_sentiment x post_gfc`: coef = 0.2010, p = 0.5609, 95% CI [-0.4763, 0.8783]"),
        bullet("`treated_sentiment x post_covid`: coef = -0.5286**, p = 0.0448, 95% CI [-1.0449, -0.0123]"),
        paragraphFromText("Interpretation:", { bold: true, spacing: { after: 60, before: 80 } }),
        bullet("Positive DiD interaction: sentiment series rose more, or fell less, than return and factor controls after that shock."),
        bullet("Negative DiD interaction: sentiment series weakened more than controls after that shock."),
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("Diagnostics")],
        }),
        simpleTable(
          ["Diagnostic", "Value", "Interpretation"],
          [
            [
              "Breusch-Pagan p-value",
              "0.0001",
              "The low p-value indicates heteroskedasticity risk, so robust or clustered standard errors are appropriate.",
            ],
            [
              "Max VIF among predictors",
              "1.58",
              "Values well below 10 reduce concern about severe multicollinearity.",
            ],
            [
              "Residual diagnostics",
              "Saved",
              "Residual-vs-fitted, Q-Q, and histogram plots were produced for distributional review.",
            ],
          ],
          [2500, 1400, 5460]
        ),
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("Robustness Checks")],
        }),
        simpleTable(
          ["Check", "Baseline", "Comparison", "Interpretive Note"],
          [
            [
              "alternative_lags",
              "0.0035",
              "0.0122 / 0.01092024870131658",
              "Signs and magnitudes across lags show whether the sentiment effect depends heavily on lag choice.",
            ],
            [
              "exclude_covid_crash_window",
              "-0.5286",
              "-0.5484 / NA",
              "Close values imply the COVID interaction is not driven only by the crash window.",
            ],
            [
              "placebo_pre_gfc",
              "0.0000",
              "-0.4685 / 0.17289273102453484",
              "Small or insignificant placebo effects support the DiD identification assumptions.",
            ],
          ],
          [2200, 1300, 2100, 3760]
        ),
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("Visual Evidence")],
        }),
        bullet("`results/figures/m3_treated_vs_control_trends.png`: treated vs control paths with 2008 and 2020 markers."),
        bullet("`results/figures/m3_did_coefficients.png`: DiD point estimates and confidence intervals."),
        bullet("`results/figures/m3_market_model_fit.png`: observed vs fitted market returns."),
        bullet("`results/figures/m3_residuals_vs_fitted.png`: residual spread across fitted values."),
        bullet("`results/figures/m3_residuals_qq.png`: residual normality diagnostic."),
        bullet("`results/figures/m3_residuals_hist.png`: residual distribution check."),
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("Applicability and Limitations")],
        }),
        bullet("The dataset has one aggregate market return series over time, so classic multi-firm panel fixed effects on returns is not directly available."),
        bullet("The entity fixed-effects and DiD analyses are applied on the stacked long panel where each variable acts as an entity."),
        bullet("This design is useful for testing shock sensitivity across groups of series, but it should not be interpreted as a firm-level causal panel model."),
        bullet("Robust (HC1) standard errors are used to reduce heteroskedasticity concerns."),
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("Files Generated for M3")],
        }),
        bullet("`results/tables/m3_market_fe_results.csv`"),
        bullet("`results/tables/m3_entity_fe_results.csv`"),
        bullet("`results/tables/m3_did_results.csv`"),
        bullet("`results/tables/m3_bp_test_results.csv`"),
        bullet("`results/tables/m3_vif_results.csv`"),
        bullet("`results/tables/m3_robustness_checks.csv`"),
        bullet("`results/tables/m3_model_comparison_table.csv`"),
        bullet("`results/figures/m3_treated_vs_control_trends.png`"),
        bullet("`results/figures/m3_did_coefficients.png`"),
        bullet("`results/figures/m3_market_model_fit.png`"),
        bullet("`results/figures/m3_residuals_vs_fitted.png`"),
        bullet("`results/figures/m3_residuals_qq.png`"),
        bullet("`results/figures/m3_residuals_hist.png`"),
      ],
    },
  ],
});

fs.mkdirSync(path.dirname(outputPath), { recursive: true });

Packer.toBuffer(doc).then((buffer) => {
  fs.writeFileSync(outputPath, buffer);
  process.stdout.write(`Wrote ${outputPath}\n`);
});