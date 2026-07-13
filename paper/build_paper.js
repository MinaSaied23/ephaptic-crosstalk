const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
  Table, TableRow, TableCell, WidthType, BorderStyle, ShadingType,
  SectionType, Header, PageNumber, Footer, convertInchesToTwip, ImageRun
} = require("docx");
const fs = require("fs");

const FONT = "Times New Roman";
const BODY_SIZE = 20;
const TITLE_SIZE = 28;
const AUTHOR_SIZE = 22;
const ABSTRACT_SIZE = 20;
const HEAD_SIZE = 20;

function P(text, opts = {}) {
  return new Paragraph({
    alignment: opts.align || AlignmentType.JUSTIFIED,
    spacing: { after: 120, line: 240, ...opts.spacing },
    indent: opts.indent,
    children: (Array.isArray(text) ? text : [text]).map(t =>
      typeof t === "string"
        ? new TextRun({ text: t, font: FONT, size: opts.size || BODY_SIZE, bold: opts.bold, italics: opts.italics })
        : t
    ),
  });
}
function FirstLineIndentP(text, opts = {}) {
  return P(text, { indent: { firstLine: convertInchesToTwip(0.2) }, ...opts });
}
function SectionHeading(numeral, title) {
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 200, after: 120 },
    children: [new TextRun({ text: `${numeral}. ${title.toUpperCase()}`, font: FONT, size: HEAD_SIZE, bold: true })],
  });
}
function PlainHeading(title) {
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 200, after: 120 },
    children: [new TextRun({ text: title.toUpperCase(), font: FONT, size: HEAD_SIZE, bold: true })],
  });
}
function SubHeading(letter, title) {
  return new Paragraph({
    spacing: { before: 160, after: 80 },
    children: [new TextRun({ text: `${letter}. ${title}`, font: FONT, size: HEAD_SIZE, bold: true, italics: true })],
  });
}
function eq(text) {
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 100, after: 100 },
    children: [new TextRun({ text, font: "Cambria Math", size: BODY_SIZE, italics: true })],
  });
}
function cell(text, opts = {}) {
  return new TableCell({
    width: { size: opts.width || 2000, type: WidthType.DXA },
    shading: opts.shade ? { type: ShadingType.CLEAR, fill: "D9D9D9" } : undefined,
    margins: { top: 60, bottom: 60, left: 80, right: 80 },
    children: [new Paragraph({
      alignment: opts.align || AlignmentType.CENTER,
      children: [new TextRun({ text, font: FONT, size: 18, bold: opts.bold })],
    })],
  });
}
function captionP(label, text) {
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 80, after: 200 },
    children: [
      new TextRun({ text: `${label}. `, font: FONT, size: 18, bold: true }),
      new TextRun({ text, font: FONT, size: 18, italics: true }),
    ],
  });
}

// ---------------------------------------------------------------
// Title block
// ---------------------------------------------------------------
const titleBlock = [
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 200 },
    children: [new TextRun({
      text: "Ephaptic A\u03b2-to-C-Fiber Crosstalk Requires Multi-Fiber Spatial Summation: A Closed-Loop Core-Conductor Study with Nociceptor-Realistic Channel Kinetics",
      font: FONT, size: TITLE_SIZE, bold: true,
    })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 40 },
    children: [new TextRun({ text: "Author Name(s) To Be Completed", font: FONT, size: AUTHOR_SIZE, italics: true })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 300 },
    children: [new TextRun({ text: "Affiliation / Department To Be Completed", font: FONT, size: 20, italics: true })],
  }),
];

const abstractBlock = [
  new Paragraph({
    spacing: { after: 120 },
    alignment: AlignmentType.JUSTIFIED,
    children: [
      new TextRun({ text: "Abstract: ", font: FONT, size: ABSTRACT_SIZE, bold: true, italics: true }),
      new TextRun({
        text: "Dynamic mechanical allodynia is frequently attributed in part to non-synaptic \u201cephaptic\u201d cross-excitation between myelinated A\u03b2 mechanoreceptive afferents and unmyelinated C-fiber nociceptors at sites of nerve compression or focal demyelination. We present a closed-loop, one-dimensional core-conductor model coupling a Chiu-Ritchie-Rogart-Stagg-Sweeney (CRRSS) myelinated A\u03b2-fiber to a C-fiber through a shared, geometrically restricted extracellular cleft, and use it to test this hypothesis in two phases. In Phase 1, using the field's standard classical Hodgkin-Huxley (HH) C-fiber kinetics, single-fiber-pair ephaptic crosstalk fails under single-pulse stimulation (cleft widths 20 nm\u20135 \u03bcm), tonic sensitization, and temporal summation up to 800 Hz. In Phase 2, we replace the C-fiber's Na\u207a conductance with literature-derived Nav1.8/Nav1.9 nociceptor kinetics (addressing the principal biological objection to Phase 1) and find single-pair crosstalk still fails, although the realistic channels now support a genuinely graded, stable sensitized state (absent in classical HH, which instead transitions sharply into spontaneous firing or depolarization block). We then extend the model to a multi-fiber bundle in which several synchronously-active A\u03b2 afferents share the same extracellular compartment as one C-fiber. Following a rigorous artifact-detection protocol (timing, duration, and geometry-independence checks) that we show is necessary because the explicit-coupling numerical scheme produces a specific, reproducible spurious-firing signature once pushed past its stability ceiling, we find that spatial summation across up to 25 verified-stable synchronized A\u03b2 fibers produces a substantial, non-artifactual depolarization trend (\u2248 8 mV, rest \u2192 \u201347.5 mV) that no single-fiber-pair mechanism approached, without yet crossing threshold within the numerically trustworthy range. These results indicate that single-fiber-pair ephaptic crosstalk is an unlikely explanation for dynamic mechanical allodynia regardless of channel realism, while multi-fiber spatial summation is a mechanistically plausible and partially-supported candidate mechanism whose confirmation requires the fully implicit numerical methods identified here as necessary future work.",
        font: FONT, size: ABSTRACT_SIZE,
      }),
    ],
  }),
  new Paragraph({
    spacing: { after: 200 },
    alignment: AlignmentType.JUSTIFIED,
    children: [
      new TextRun({ text: "Index Terms: ", font: FONT, size: ABSTRACT_SIZE, bold: true, italics: true }),
      new TextRun({
        text: "ephaptic coupling, dynamic mechanical allodynia, peripheral neuropathic pain, core-conductor model, Hodgkin-Huxley model, Nav1.8, Nav1.9, myelinated nerve fiber, C-fiber nociceptor, multi-fiber spatial summation, computational neuroscience.",
        font: FONT, size: ABSTRACT_SIZE, italics: true,
      }),
    ],
  }),
];

// ---------------------------------------------------------------
// Two-column body
// ---------------------------------------------------------------
const body = [];

// I. INTRODUCTION
body.push(SectionHeading("I", "Introduction"));
body.push(FirstLineIndentP([
  "Dynamic mechanical allodynia (pain evoked by light, moving tactile stimuli such as brushing or clothing contact) is a hallmark of peripheral neuropathic pain conditions including painful diabetic neuropathy [4], post-herpetic neuralgia, and nerve entrapment syndromes such as trigeminal neuralgia [3]. A long-standing biophysical hypothesis holds that, at sites of focal demyelination or mechanical nerve compression, the normally independent electrical activity of large myelinated A\u03b2 mechanoreceptive afferents and small unmyelinated C-fiber nociceptors can become directly coupled through their shared, pathologically restricted extracellular space; a phenomenon first described by Arvanitaki [1] and by Katz and Schmitt [2] as \u201cephaptic\u201d interaction. Experimental precedent for non-synaptic cross-excitation between afferent classes has since been reported directly in dorsal root ganglia [5], [6] and in chronically damaged peripheral nerve [7], [8]. Under this hypothesis, ordinary light touch, carried by A\u03b2 fibers, could directly and non-synaptically trigger ectopic firing in a neighboring nociceptor, providing a purely peripheral account of allodynia that does not require central sensitization.",
]));
body.push(FirstLineIndentP([
  "Prior computational treatments of ephaptic interaction in peripheral nerve have generally fallen into two categories: open-loop forward models, in which one fiber's field is imposed on a second fiber without feedback [9], and closed-loop models restricted to fibers of a single class, e.g., bundles of myelinated fibers or central white-matter tracts [11]\u2013[13]. Dedicated simulation platforms and toolkits have extended these approaches to broader classes of ephaptic and extracellular-stimulation problems [14]\u2013[17]. Ephaptic coupling has additionally been documented in central circuits such as cerebellar Purkinje cells [34] and the olfactory bulb [35], indicating the phenomenon is not restricted to peripheral nerve. To our knowledge, no published model has evaluated closed-loop, bidirectional ephaptic coupling between a myelinated A\u03b2 fiber and an unmyelinated C-fiber using biophysically distinct, independently validated channel kinetics for each fiber type, under a systematically swept range of the pathological geometric parameter (extracellular cleft width) that is thought to govern coupling strength, nor has any such model tested whether spatial summation across a multi-fiber bundle can succeed where single-fiber-pair coupling fails.",
]));
body.push(FirstLineIndentP([
  "This paper reports such a model, developed and evaluated in two phases. Phase 1 establishes a closed-loop core-conductor system coupling a CRRSS-kinetics myelinated A\u03b2-fiber and a classical Hodgkin-Huxley (HH) C-fiber (the field's standard baseline formulation) through a shared extracellular potential, and systematically tests whether direct A\u03b2\u2192C ephaptic crosstalk can drive an ectopic C-fiber spike under single-pulse stimulation, tonic peripheral sensitization, and temporal summation from repetitive firing. Anticipating the principal biological objection to a classical-HH nociceptor model, Phase 2 replaces the C-fiber's Na\u207a conductance with literature-derived Na", new TextRun({text:"v",size:20,italics:true}), "1.8/Na", new TextRun({text:"v",size:20,italics:true}), "1.9 nociceptor kinetics, re-validates the fiber and re-runs the Phase 1 experiment set, and then extends the model to a multi-fiber bundle geometry in which several simultaneously-active A\u03b2 afferents converge on a shared extracellular compartment with one C-fiber, directly testing spatial summation as an alternative to single-fiber-pair crosstalk. We report that single-pair crosstalk fails consistently across both channel models, but that multi-fiber spatial summation (verified via a dedicated artifact-detection protocol described in Section III) produces a substantial, non-artifactual trend toward threshold that no single-pair mechanism approached, making it the most promising direction identified for future work.",
]));

// II. METHODS
body.push(SectionHeading("II", "Methods"));

body.push(SubHeading("A", "Coupled Core-Conductor Formulation"));
body.push(FirstLineIndentP([
  "Two parallel, electrically independent axons of length L = 10 mm are embedded in a shared extracellular channel of longitudinal resistance per unit length r",
  new TextRun({ text: "e", font: FONT, size: 14, subScript: true }),
  ". For axon k \u2208 {1, 2} (A\u03b2, C), the transmembrane potential v",
  new TextRun({ text: "m,k", font: FONT, size: 14, subScript: true }),
  " = u",
  new TextRun({ text: "i,k", font: FONT, size: 14, subScript: true }),
  " \u2212 u",
  new TextRun({ text: "e", font: FONT, size: 14, subScript: true }),
  " evolves according to the coupled cable equations",
]));
body.push(eq("\u2202v_{m,k}/\u2202t = (1/C_{m,k}) [ (d_k / 4\u03c1_i)(\u2202\u00b2v_{m,k}/\u2202z\u00b2 + \u2202\u00b2u_e/\u2202z\u00b2) \u2212 I_{ion,k} ]"));
body.push(FirstLineIndentP([
  "where d",
  new TextRun({ text: "k", font: FONT, size: 14, subScript: true }),
  " is fiber diameter, \u03c1", new TextRun({ text: "i", font: FONT, size: 14, subScript: true }),
  " is axoplasmic resistivity, and the shared extracellular potential u",
  new TextRun({ text: "e", font: FONT, size: 14, subScript: true }),
  " satisfies a regularized Poisson equation driven by the combined transmembrane ionic current of both fibers (Section II-C), following the classical extracellular field formulation of Clark and Plonsey [10] and its cable-theoretic extension to endogenous-field coupling by Goldwyn and Rinzel [21]. In Section II-E this two-fiber system is generalized to n simultaneously-active A\u03b2 fibers sharing the same extracellular compartment as one C-fiber. Fig. 0 summarizes the resulting model architecture.",
]));
body.push({ FIGURE_BREAK: "fig0" });

body.push(SubHeading("B", "Membrane Kinetics"));
body.push(FirstLineIndentP([
  "The A\u03b2-fiber (d = 10 \u03bcm) uses CRRSS kinetics [18], [19] in both phases of this study, with active Na\u207a conductance and leak restricted to discrete nodes of Ranvier spaced 1 mm apart. Internodal compartments are assigned reduced membrane capacitance and leak conductance (250-fold lower than at nodes), reflecting the insulating effect of the myelin sheath; without this correction, saltatory propagation fails; an action potential initiated at one node does not reach the next, because internodal charge leaks away rather than passing passively forward. This requirement, while a standard feature of validated myelinated-fiber models, is easy to omit and was found empirically to be necessary during model validation (Section III-A).",
]));
body.push(FirstLineIndentP([
  "The C-fiber (d = 1 \u03bcm) is modeled in two variants across the two phases of this study. The Phase 1 (baseline) C-fiber uses classical Hodgkin-Huxley kinetics [20], continuously active along its length, parameterized to represent a generic cutaneous afferent; this is the field's standard formulation and the one on which essentially all prior closed-loop ephaptic models rely. The Phase 2 (nociceptor-realistic) C-fiber replaces this classical Na\u207a conductance with Na", new TextRun({text:"v",size:20,italics:true}), "1.8/Na", new TextRun({text:"v",size:20,italics:true}), "1.9 kinetics, detailed in Section II-E.",
]));

body.push(SubHeading("C", "Extracellular Coupling and Regularization"));
body.push(FirstLineIndentP([
  "The longitudinal extracellular resistance r", new TextRun({ text: "e", font: FONT, size: 14, subScript: true }),
  " = \u03c1", new TextRun({ text: "e", font: FONT, size: 14, subScript: true }),
  " / A", new TextRun({ text: "eff", font: FONT, size: 14, subScript: true }),
  " is derived from the annular effective cross-sectional area of the extracellular cleft separating the fibers, parameterized by cleft width w", new TextRun({ text: "cleft", font: FONT, size: 14, subScript: true }),
  ". The governing equation for u", new TextRun({ text: "e", font: FONT, size: 14, subScript: true }),
  " under pure sealed-end (Neumann) boundary conditions is singular, defined only up to an additive constant. We therefore add a small regularization term \u03ba, representing weak leakage of the restricted cleft's potential to the surrounding bulk tissue beyond the simulated segment:",
]));
body.push(eq("\u2202\u00b2u_e/\u2202z\u00b2 \u2212 \u03ba\u00b7u_e = r_e \u00b7 I_total(z)"));
body.push(FirstLineIndentP([
  "\u03ba was calibrated so that a single, physiologically realistic nodal Na\u207a current produces an extracellular field on the order of a few millivolts, consistent with published estimates of ephaptic field magnitude in tightly restricted extracellular spaces [21], [22], [23]. This calibration (\u03ba = 1\u00d710\u2079 m\u207b\u00b2, field decay length \u2248 32 \u03bcm) was used for the two-fiber experiments in both phases (Section III-B through III-H). For the multi-fiber bundle (Section II-F), the total source term scales with the number of simultaneously-active A\u03b2 fibers; \u03ba was accordingly re-verified, and where necessary strengthened, using the duration/timing/geometry-independence artifact-detection protocol described in Section III-I, rather than assumed to transfer unchanged from the two-fiber calibration.",
]));

body.push(SubHeading("D", "Numerical Scheme"));
body.push(FirstLineIndentP([
  "The model is solved on a spatial grid of \u0394z = 10 \u03bcm (N = 1000 compartments). A naive fully-explicit (forward Euler) treatment of the axial diffusion term is numerically unstable at this spatial resolution; we therefore use an implicit\u2013explicit (IMEX) splitting throughout: the linear axial diffusion term is integrated with backward Euler (solved as a tridiagonal system via LAPACK banded solvers), while the nonlinear ionic currents and the ephaptic coupling term are integrated explicitly from the previous time step's membrane state, and the shared extracellular potential is obtained by solving its regularized Poisson equation as a banded tridiagonal system at every time step. Phase 1 (classical HH C-fiber) uses \u0394t = 5\u00d710\u207b\u2076 s, matching the temporal resolution needed for the CRRSS nodal Na\u207a upstroke. Phase 2 (Na", new TextRun({text:"v",size:20,italics:true}), "1.8/1.9 C-fiber) requires a five-fold finer step, \u0394t = 1\u00d710\u207b\u2076 s: the larger Na", new TextRun({text:"v",size:20,italics:true}), "1.8 conductance density needed for continuous propagation (Section II-E) makes the explicit ionic-current update stiff at the coarser step, producing non-physiological voltage blow-up that we verified, by re-running at finer \u0394t, to be a discretization artifact rather than a genuine instability of the underlying dynamics.",
]));
body.push(FirstLineIndentP([
  "This scheme is unconditionally stable with respect to axial diffusion but retains a stability ceiling on coupling strength (governed by \u03ba and, in the multi-fiber case, by the number of simultaneously-active A\u03b2 fibers) because the ephaptic feedback term itself is treated explicitly (Sections III-F, III-I).",
]));

body.push(SubHeading("E", "Nav1.8/Nav1.9 Nociceptor Kinetics"));
body.push(FirstLineIndentP([
  "The Phase 2 C-fiber's Na\u207a current is modeled as the sum of a Na", new TextRun({text:"v",size:20,italics:true}), "1.8 component and a Na", new TextRun({text:"v",size:20,italics:true}), "1.9 component, each governed by first-order relaxation toward a voltage-dependent Boltzmann steady state, dX/dt = (X", new TextRun({text:"\u221e", size:14}), "(v) \u2212 X)/\u03c4", new TextRun({text:"X", size:14, subScript:true}), ":",
]));
body.push(eq("I_Na18 = g\u030418 m8\u00b3 h8 (v \u2212 E_Na),  I_Na19 = g\u030419 m9 (v \u2212 E_Na)"));
body.push(eq("m8_\u221e(v) = 1/[1+exp(\u2212(v\u2212V8m)/k8m)],  V8m=\u221225 mV, k8m=6 mV, \u03c4m8=1.5 ms"));
body.push(eq("h8_\u221e(v) = 1/[1+exp((v\u2212V8h)/k8h)],  V8h=\u221230 mV, k8h=6 mV, \u03c4h8=17 ms"));
body.push(eq("m9_\u221e(v) = 1/[1+exp(\u2212(v\u2212V9m)/k9m)],  V9m=\u221250 mV, k9m=5 mV, \u03c4m9=10 ms"));
body.push(FirstLineIndentP([
  "Na", new TextRun({text:"v",size:20,italics:true}), "1.8's depolarized, dominant-component activation/inactivation midpoints and its slow activation/inactivation time constants are drawn from voltage-clamp recordings of TTX-resistant current in small-diameter DRG neurons [25], [26]; Na", new TextRun({text:"v",size:20,italics:true}), "1.9's markedly hyperpolarized activation midpoint and treatment as a persistent, non-inactivating current (single m-gate, no h-gate) follow its characterization as a subthreshold, near-non-inactivating conductance [27], [28]. Voltage-independent time constants are a deliberate simplification for tractability; K\u207a (classical delayed rectifier) and leak conductances are retained from the Phase 1 model unchanged, with leak reversal E", new TextRun({text:"leak,2", size:14, subScript:true}), " = \u221255 mV. Maximum conductance densities (g\u030418 = 2000 mS/cm\u00b2, g\u030419 = 0.2 mS/cm\u00b2) were determined empirically: point-neuron rheobase testing first identified a stable, excitable regime at modest densities, but full-cable testing showed that Na", new TextRun({text:"v",size:20,italics:true}), "1.8's slow activation time constant (\u03c4m8 = 1.5 ms) gives continuous unmyelinated propagation a substantially lower safety factor than the classical HH Na\u207a conductance's fast kinetics (\u03c4m ~0.1\u20130.5 ms) provide at the same density; g\u030418 was increased, with K\u207a density held at its classical value, until full-length continuous propagation was achieved and confirmed numerically stable at \u0394t = 1 \u03bcs (Section III-G).",
]));

body.push(SubHeading("F", "Multi-Fiber Bundle Formulation"));
body.push(FirstLineIndentP([
  "To test spatial summation as an alternative to single-fiber-pair crosstalk, the two-fiber system of Section II-A is extended to n simultaneously-active, identical A\u03b2 fibers sharing the same extracellular compartment as one Phase-2 C-fiber. Because all n A\u03b2 fibers receive identical stimulation and are identically coupled to the same shared field, they evolve identically by symmetry; we therefore simulate a single representative A\u03b2 cable and scale its contribution to the shared extracellular source term by n:",
]));
body.push(eq("I_total(z) = n\u00b7\u03c0d1 I_ion,1(z) + \u03c0d2 I_ion,2(z)"));
body.push(FirstLineIndentP([
  "Each individual A\u03b2 fiber's own membrane dynamics, and the ephaptic feedback it receives, are unaffected by n, consistent with this symmetric-copy assumption; only the field the ensemble collectively generates (and hence the drive felt by the C-fiber) scales with fiber count. This synchronous-firing configuration represents a receptive field in which a mechanical stimulus (e.g., a light touch or vibratory stroke) simultaneously recruits several A\u03b2 mechanoreceptive afferents converging on a local Remak bundle; asynchronous or jittered multi-fiber recruitment is not tested here and is noted as a direction for future work (Section V).",
]));

body.push(SubHeading("G", "Simulation Protocols"));
body.push(FirstLineIndentP([
  "Each experiment initiates a supra-threshold current pulse (100 nA, 0.2 ms, or a train thereof) at the first A\u03b2 node of Ranvier (z = 0) and monitors the full spatiotemporal C-fiber membrane potential for any ectopic threshold crossing (v", new TextRun({ text: "m,2", font: FONT, size: 14, subScript: true }), " > 0 mV) at locations away from the stimulation site and domain boundaries. Phase 1 (classical HH C-fiber, Sections III-B\u2013III-F) comprises: (1) a single-pulse sweep of cleft width from 20 nm to 5 \u03bcm; (2) tonic C-fiber sensitization, via a persistent depolarizing bias current and separately via a uniform shift of the HH gating kinetics (Section II-H), each combined with single-pulse A\u03b2 stimulation; (3) a temporal summation protocol delivering trains of 5\u201320 A\u03b2 pulses at 50\u2013800 Hz to a genuinely resting (unsensitized) C-fiber; and (4) a stronger-coupling stress test. Phase 2 (Na", new TextRun({text:"v",size:20,italics:true}), "1.8/1.9 C-fiber, Sections III-G\u2013III-I) re-validates the isolated fiber and repeats protocols (1)\u2013(3) at reduced but representative sweep density, then extends to the multi-fiber bundle protocol of Section II-F, sweeping both cleft width and A\u03b2 fiber count n, with every candidate positive result subjected to the timing/duration/geometry-independence artifact-detection checks described in Section III-F and re-applied in Section III-I.",
]));

body.push(SubHeading("H", "Shifted-Kinetics Formulation for Sensitization (Section III-D)"));
body.push(FirstLineIndentP([
  "The Phase 1 sensitization test of Section III-D applies a uniform voltage offset \u0394V", new TextRun({ text: "shift", font: FONT, size: 14, subScript: true }), " (mV) to the voltage argument of every classical HH rate function (both gates of the Na\u207a channel and the K\u207a activation gate) rather than to the Na\u207a activation gate alone. For membrane potential v (mV), each rate is evaluated at v\u2032 = v + \u0394V", new TextRun({ text: "shift", font: FONT, size: 14, subScript: true }), ":",
]));
body.push(eq("\u03b1_m(v) = 0.1(v\u2032+40) / [1\u2212exp(\u2212(v\u2032+40)/10)]"));
body.push(eq("\u03b2_m(v) = 4\u00b7exp[\u2212(v\u2032+65)/18]"));
body.push(eq("\u03b1_h(v) = 0.07\u00b7exp[\u2212(v\u2032+65)/20]"));
body.push(eq("\u03b2_h(v) = 1 / [1+exp(\u2212(v\u2032+35)/10)]"));
body.push(eq("\u03b1_n(v) = 0.01(v\u2032+55) / [1\u2212exp(\u2212(v\u2032+55)/10)]"));
body.push(eq("\u03b2_n(v) = 0.125\u00b7exp[\u2212(v\u2032+65)/80],  v\u2032 = v + \u0394V_{shift}"));
body.push(FirstLineIndentP([
  "with \u0394V", new TextRun({ text: "shift", font: FONT, size: 14, subScript: true }), " > 0 producing a leftward shift of the excitability curve. This uniform-shift formulation was adopted as a parsimonious first approximation of net inflammatory sensitization within the classical HH framework; Section III-D reports its behavior (spontaneous firing, not graded sensitization), motivating the Phase 2 Na", new TextRun({text:"v",size:20,italics:true}), "1.8/1.9 kinetics of Section II-E, whose sensitization behavior is reported in Section III-H.",
]));

// III. RESULTS
body.push(SectionHeading("III", "Results"));
body.push(FirstLineIndentP([
  "Sections III-A through III-F report Phase 1 (classical HH C-fiber) results, summarized in Table I. Sections III-G through III-I report Phase 2 (Na", new TextRun({text:"v",size:20,italics:true}), "1.8/1.9 C-fiber) results, including the multi-fiber bundle experiment, summarized in Table II.",
]));

body.push(SubHeading("A", "Single-Fiber Validation and Positive Control"));
body.push(FirstLineIndentP([
  "With myelin-corrected internodal parameters, the isolated A\u03b2-fiber conducted saltatorily through all ten simulated nodes of Ranvier with stable spike amplitude (~48 mV) and an estimated conduction velocity of 35.6 m/s, within the expected physiological range (30\u201360 m/s) for a 10 \u03bcm myelinated fiber. The isolated Phase 1 (classical HH) C-fiber conducted continuously at 0.57 m/s, within the expected range (0.5\u20131.0 m/s) for a cutaneous C-nociceptor. Both results were obtained with the coupling term disabled, confirming that each fiber's intrinsic kinetics behave as expected before closed-loop coupling was introduced.",
]));
body.push(FirstLineIndentP([
  "These runs additionally serve as a positive control for every negative result reported below: they establish, using the identical spatial discretization and integration scheme used throughout the paper, that the Phase 1 C-fiber model is fully capable of generating and propagating a regenerative action potential when adequately driven (Fig. 1b). The Phase 2 C-fiber's independent positive control is reported in Section III-G. The absence of ectopic firing in the coupled ephaptic experiments is therefore attributable specifically to insufficient ephaptic drive relative to threshold, and not to a C-fiber implementation that is intrinsically unable to spike.",
]));
body.push(FirstLineIndentP([
  "We additionally checked the sensitivity of the reported A\u03b2 conduction velocity to spatial and temporal discretization. Halving \u0394z and \u0394t together (10 \u03bcm/5 \u03bcs \u2192 5 \u03bcm/2.5 \u03bcs \u2192 2.5 \u03bcm/1.25 \u03bcs) increased the estimated CV monotonically (35.6 \u2192 42.6 \u2192 49.6 m/s) rather than converging to a fixed value. This is not evidence of an unstable integration scheme (the IMEX solver itself remains stable, as verified in Section II-D); rather, it reflects a structural property of representing each 1 mm internode's node of Ranvier as a single discrete compartment of width \u0394z. Because the model ties nodal membrane area to \u0394z rather than to the physiological node width (~1 \u03bcm), refining the grid inadvertently shrinks the simulated node's active membrane area, altering local excitability and hence CV. All results reported in this paper use the single, fixed discretization (\u0394z = 10 \u03bcm) described in Section II-D consistently across every experiment and every comparison between conditions, so the relative conclusions of this study (e.g., spike vs. no-spike, and the direction and rough scale of any depolarization trend) are unaffected; the absolute CV value, however, should be read as characteristic of this discretization rather than as a grid-independent physical prediction. Decoupling node width from \u0394z (e.g., by representing each node as a fixed physical patch spanning multiple fine compartments regardless of overall grid resolution) would be required to obtain a grid-independent CV, and is noted as a refinement for future work (Section V).",
]));
body.push({ FIGURE_BREAK: "fig1" });

body.push(SubHeading("B", "Experiment 1: Single-Pulse Crosstalk (Phase 1)"));
body.push(FirstLineIndentP([
  "No ectopic C-fiber spike was observed at any tested cleft width across the full range of 20 nm to 5 \u03bcm. The peak ephaptic perturbation of C-fiber membrane potential, measured away from the stimulation artifact, was approximately 2.8\u20134 mV; well below the ~10\u201315 mV depolarization required to reach threshold from rest. Consistent with the classical core-conductor picture of ephaptic interaction, the sign of the effect was spatially structured: at the location precisely aligned with a passing A\u03b2 node, the induced perturbation was transiently hyperpolarizing, while depolarizing lobes of comparable magnitude occurred at flanking locations slightly offset in space and time from the source.",
]));

body.push(SubHeading("C", "Sensitization via Persistent Depolarizing Bias (Phase 1)"));
body.push(FirstLineIndentP([
  "A tonic depolarizing bias current was applied uniformly along the C-fiber to model peripheral sensitization by inflammatory mediators. At biases producing a steady-state resting depolarization to approximately \u221255 to \u221250 mV, combined with A\u03b2 ephaptic input at cleft widths down to 50 nm, no threshold crossing occurred; the marginal ephaptic contribution above the elevated baseline remained small (~2\u20133 mV) regardless of cleft width. At larger biases sufficient to depolarize the resting potential further (toward \u221230 mV or beyond), the C-fiber began firing spontaneously with no A\u03b2 input whatsoever, indicating that these bias levels do not correspond to a genuinely stable sensitized resting state within classical HH kinetics but instead cross an intrinsic instability of the model.",
]));

body.push(SubHeading("D", "Sensitization via Uniform HH Kinetics Shift (Phase 1)"));
body.push(FirstLineIndentP([
  "As an alternative representation of inflammatory sensitization, we applied the uniform gating-kinetics shift defined in Section II-H to lower the effective firing threshold, without external current injection. Even a modest shift (\u0394V", new TextRun({ text: "shift", font: FONT, size: 14, subScript: true }), " \u2265 3 mV) produced spontaneous, self-sustained repetitive firing with zero external input. This indicates that the classical HH parameter set exhibits a sharp transition between quiescence and spontaneous oscillation (consistent with the known Hopf-bifurcation structure of type II excitable membrane models) rather than a graded region in which the membrane is stably quiescent yet meaningfully closer to threshold. This structural property of classical HH channel kinetics, rather than an implementation error, directly motivated the Phase 2 nociceptor-realistic channel model (Section II-E), whose sensitization behavior is reported in Section III-H.",
]));

body.push(SubHeading("E", "Temporal Summation (Phase 1)"));
body.push(FirstLineIndentP([
  "To isolate genuine ephaptic summation from the confounds identified in Sections III-C and III-D, trains of 5 to 20 A\u03b2 pulses were delivered at frequencies from 50 to 800 Hz to a C-fiber held at its unmodified, independently-validated resting state (no tonic bias or kinetic shift). Long-duration control simulations (up to 300 ms) confirmed this baseline never fires spontaneously. Across the full combination of pulse train frequency, pulse count, and cleft width (50 nm to 1 \u03bcm), no ectopic spike occurred; maximal cumulative depolarization reached only 1\u20132 mV above rest, indicating that successive ephaptic pushes do not summate effectively at physiologically-calibrated coupling strength.",
]));

body.push(SubHeading("F", "Stronger Coupling and Its Numerical Limits (Phase 1)"));
body.push(FirstLineIndentP([
  "Motivated by literature reports of larger ephaptic field magnitudes in extremely tightly apposed membranes (e.g., cardiac intercalated-disc ephaptic coupling [23], [24]), we tested a substantially stronger coupling condition (\u03ba = 3\u00d710\u2077 m\u207b\u00b2, decay length \u2248183 \u03bcm), the strongest value for which a single-shot Poisson solve remained numerically stable. Under this condition, apparent ectopic spikes occurred, but with two features inconsistent with genuine ephaptic triggering: spike timing bore no relationship to the arrival of the A\u03b2 action potential at the corresponding location (delays of up to several milliseconds rather than a sub-millisecond response), and, when the simulation window was extended, every tested cleft width (including a 1 \u03bcm cleft previously shown to be robustly stable under weaker coupling) eventually exhibited the same spurious firing. We conclude that this coupling regime exceeds the stability ceiling of the explicit-feedback numerical scheme described in Section II-D, and that its apparent \u201cresults\u201d reflect a numerical artifact rather than biophysics. This delayed-onset, geometry-independent spurious-firing signature (verified here for the first time) recurs whenever the scheme is pushed past its stability ceiling, and the same diagnostic protocol (timing relative to expected arrival; behavior under extended simulation duration; independence from the geometric parameter nominally being tested) is applied again in Section III-I, where it proves essential.",
]));
body.push(FirstLineIndentP([
  "Table I consolidates the outcome of every Phase 1 condition; no condition drawn from a physiologically-stable baseline produced genuine ephaptic threshold crossing.",
]));

body.push(new Paragraph({ spacing: { after: 100 }, children: [] }));
body.push(new Table({
  width: { size: 4700, type: WidthType.DXA },
  columnWidths: [1800, 1500, 1400],
  rows: [
    new TableRow({ children: [cell("Condition", { width: 1800, bold: true, shade: true }), cell("Max \u0394v (mV)", { width: 1500, bold: true, shade: true }), cell("Spike?", { width: 1400, bold: true, shade: true })] }),
    new TableRow({ children: [cell("Single pulse, 20 nm\u20135 \u03bcm", { width: 1800 }), cell("~2.8\u20134", { width: 1500 }), cell("No", { width: 1400 })] }),
    new TableRow({ children: [cell("Mild bias + pulse", { width: 1800 }), cell("~2\u20133", { width: 1500 }), cell("No", { width: 1400 })] }),
    new TableRow({ children: [cell("Aggressive bias", { width: 1800 }), cell("n/a", { width: 1500 }), cell("Spontaneous*", { width: 1400 })] }),
    new TableRow({ children: [cell("Kinetics shift \u22653 mV", { width: 1800 }), cell("n/a", { width: 1500 }), cell("Spontaneous*", { width: 1400 })] }),
    new TableRow({ children: [cell("Summation, 50\u2013800 Hz", { width: 1800 }), cell("~1\u20132", { width: 1500 }), cell("No", { width: 1400 })] }),
    new TableRow({ children: [cell("Strong coupling (\u03ba=3e7)", { width: 1800 }), cell("N/A", { width: 1500 }), cell("Artifact\u2020", { width: 1400 })] }),
  ],
}));
body.push(captionP("Table I", "Phase 1 (classical HH C-fiber): summary of experimental conditions and outcomes. *Fires independent of A\u03b2 input, reflecting model instability rather than a genuine sensitized state. \u2020Non-physiological, geometry-independent, delayed; attributed to explicit-scheme numerical instability (Sec. III-F)."));

body.push(SubHeading("G", "Nav1.8/Nav1.9 C-Fiber Validation (Phase 2)"));
body.push(FirstLineIndentP([
  "Point-neuron rheobase testing located a stable resting state and a clear, regenerative excitation threshold for the Na", new TextRun({text:"v",size:20,italics:true}), "1.8/1.9 kinetics of Section II-E (rheobase between 0.5 and 1.0 nA for a 1 ms pulse; peak spike amplitude ~21\u201325 mV at near-rheobase current, consistent with the broader, smaller-amplitude action potentials typically reported for nociceptors relative to fast myelinated fibers). Full-cable testing, however, showed that classical-HH-scale Na\u207a density (120\u2013150 mS/cm\u00b2) does not support continuous propagation with Na", new TextRun({text:"v",size:20,italics:true}), "1.8's slow activation kinetics (\u03c4m8 = 1.5 ms): an action potential initiated at the stimulation site failed to recruit neighboring compartments and decayed within 2\u20133 mm. Increasing Na", new TextRun({text:"v",size:20,italics:true}), "1.8 density restored propagation, and full-length continuous conduction through all five tested positions (z = 1\u20139 mm) was achieved at g\u030418 = 2000 mS/cm\u00b2 (Fig. 2a), confirmed numerically stable at \u0394t = 1 \u03bcs. The resulting conduction velocity, \u22480.36 m/s, is on the slow end of (but not inconsistent with) the physiological range reported for cutaneous C-nociceptors, and we report it as such rather than continuing to tune the model to match the Phase 1 classical-HH benchmark exactly. Long-duration (300 ms) simulation with no A\u03b2 input confirmed the resting state is genuinely stable (identical results at 100 ms and 300 ms, no spontaneous firing), providing a positive control for Phase 2 directly analogous to that established for Phase 1 in Section III-A.",
]));
body.push({ FIGURE_BREAK: "fig2" });

body.push(SubHeading("H", "Phase 2 Crosstalk Results (Nav1.8/Nav1.9 C-Fiber)"));
body.push(FirstLineIndentP([
  "Single-pulse stimulation was re-run across the same cleft-width range as Phase 1 (20 nm\u20135 \u03bcm). No ectopic spike occurred at any cleft width; the peak ephaptic perturbation (~0.2\u20130.3 mV) was, if anything, smaller than the Phase 1 classical-HH effect, consistent with the C-fiber's more depolarized resting potential and the Na", new TextRun({text:"v",size:20,italics:true}), "1.9 persistent current partially buffering small perturbations near rest.",
]));
body.push(FirstLineIndentP([
  "Tonic sensitization via a persistent depolarizing bias current, re-tested with the Na", new TextRun({text:"v",size:20,italics:true}), "1.8/1.9 C-fiber, revealed a materially different (and more biologically plausible) failure structure than Phase 1. A genuinely graded, stable sensitized window exists: biases up to ~0.25 A/m\u00b2 produced a stable elevated resting potential (up to \u2248\u221256.8 mV) with no spontaneous activity, in contrast to classical HH's immediate transition to spontaneous firing. Above this window (bias \u2273 0.3 A/m\u00b2), however, the fiber does not fire repetitively; it instead settles into a sustained depolarized, silent state (depolarization block, driven by near-complete Na", new TextRun({text:"v",size:20,italics:true}), "1.8 inactivation); a different, but still non-physiological, failure mode. Combining ephaptic input with sensitization at the edge of the genuinely stable window (bias 0.2\u20130.28 A/m\u00b2, cleft widths down to 20 nm) still produced no threshold crossing; the marginal ephaptic contribution remained under 1 mV, far short of the several-millivolt gap remaining to threshold even at the most favorable bias tested.",
]));
body.push(FirstLineIndentP([
  "Temporal summation, re-tested at reduced but representative sweep density (200\u2013400 Hz, 5\u201310 pulses, cleft widths 20\u2013200 nm, unsensitized C-fiber), likewise produced no ectopic spike, consistent with both Phase 1 and the single-pulse Phase 2 result above.",
]));
body.push(FirstLineIndentP([
  "In summary, replacing classical HH kinetics with literature-derived Na", new TextRun({text:"v",size:20,italics:true}), "1.8/1.9 nociceptor kinetics changes the qualitative behavior of sensitization (producing a genuine, if narrow, graded stable window rather than classical HH's sharp bifurcation) but does not change the bottom-line conclusion: single-fiber-pair ephaptic crosstalk remains insufficient under any tested combination of stimulation, sensitization, or summation.",
]));

body.push(SubHeading("I", "Multi-Fiber Bundle Spatial Summation (Phase 2)"));
body.push(FirstLineIndentP([
  "Motivated by the consistent failure of single-fiber-pair mechanisms in both phases, we tested the multi-fiber bundle formulation of Section II-F: n synchronously-firing A\u03b2 fibers sharing one extracellular compartment with an unsensitized Na", new TextRun({text:"v",size:20,italics:true}), "1.8/1.9 C-fiber. An initial sweep at the Section II-C two-fiber calibration (\u03ba = 1\u00d710\u2079 m\u207b\u00b2) produced an apparent ectopic spike at n = 5 (cleft 200 nm). Applying the artifact-detection protocol established in Section III-F immediately identified this as spurious: the threshold crossing occurred 0.40 ms after stimulation at a location the A\u03b2 wave reached at 0.08 ms (a 0.32 ms unexplained delay) and extending the simulation window showed that nominally \u201cstable\u201d nearby conditions (n = 3 and n = 5 at a narrower cleft) also eventually fired spuriously given more time, while genuine two-fiber-equivalent conditions (n = 1) did not. This behavior is the same delayed-onset, duration-dependent, non-monotonic-in-geometry signature documented in Section III-F, now triggered by total A\u03b2 source current scaling with n rather than by \u03ba directly.",
]));
body.push(FirstLineIndentP([
  "We therefore re-calibrated \u03ba specifically for the multi-fiber source magnitude, verifying at each step (via extended-duration simulation (up to 18 ms, several-fold longer than the 2\u20133 ms window in which genuine ephaptic responses complete) and timing checks against expected A\u03b2 arrival) that reported outcomes are genuine rather than artifactual. At \u03ba = 5\u00d710\u2079 m\u207b\u00b2, n = 1\u20138 remained stable under extended duration; at \u03ba = 2\u00d710\u00b9\u2070 m\u207b\u00b2, stability under extended duration (confirmed to 18 ms) extended to n = 25. Beyond this (n = 40 tested at \u03ba = 2\u00d710\u00b9\u2070 m\u207b\u00b2) the same delayed-onset artifact reappeared (first crossing at 3.31 ms against an expected arrival of 0.17 ms), and was excluded from the reported result.",
]));
body.push(FirstLineIndentP([
  "Within the numerically verified-stable range (n = 1 to 25), spatial summation produced a substantial, monotonic, non-artifactual depolarization trend: peak C-fiber membrane potential shifted from \u221255.0 mV (n = 1, indistinguishable from the two-fiber result of Section III-H) to \u221247.5 mV (n = 25); an \u22488 mV effect, roughly an order of magnitude larger than any single-fiber-pair mechanism tested in either phase, and confirmed stable under an 18 ms simulation window (Fig. 2b). This trend did not cross threshold within the verified-stable range, and we explicitly do not claim that it would with additional fibers; extending the trend beyond n = 25 requires a numerical scheme not limited by the explicit-coupling stability ceiling identified in Sections III-F and III-I (see Section V).",
]));

body.push(new Paragraph({ spacing: { after: 100 }, children: [] }));
body.push(new Table({
  width: { size: 4700, type: WidthType.DXA },
  columnWidths: [1900, 1500, 1300],
  rows: [
    new TableRow({ children: [cell("Condition (Phase 2)", { width: 1900, bold: true, shade: true }), cell("Max \u0394v (mV)", { width: 1500, bold: true, shade: true }), cell("Spike?", { width: 1300, bold: true, shade: true })] }),
    new TableRow({ children: [cell("Single pulse, 20 nm\u20135 \u03bcm", { width: 1900 }), cell("~0.2\u20130.3", { width: 1500 }), cell("No", { width: 1300 })] }),
    new TableRow({ children: [cell("Graded bias (\u22640.25 A/m\u00b2)", { width: 1900 }), cell("stable, subthresh.", { width: 1500 }), cell("No", { width: 1300 })] }),
    new TableRow({ children: [cell("Bias + pulse (edge of window)", { width: 1900 }), cell("<1", { width: 1500 }), cell("No", { width: 1300 })] }),
    new TableRow({ children: [cell("Aggressive bias (\u22730.3 A/m\u00b2)", { width: 1900 }), cell("n/a", { width: 1500 }), cell("Depol. block*", { width: 1300 })] }),
    new TableRow({ children: [cell("Summation, 200\u2013400 Hz", { width: 1900 }), cell("~1", { width: 1500 }), cell("No", { width: 1300 })] }),
    new TableRow({ children: [cell("Multi-fiber, n=1\u201325 (verified)", { width: 1900 }), cell("\u2248 8 (trend)", { width: 1500 }), cell("No (trending)", { width: 1300 })] }),
    new TableRow({ children: [cell("Multi-fiber, n=40 (\u03ba=2e10)", { width: 1900 }), cell("N/A", { width: 1500 }), cell("Artifact\u2020", { width: 1300 })] }),
  ],
}));
body.push(captionP("Table II", "Phase 2 (Nav1.8/Nav1.9 C-fiber): summary of experimental conditions and outcomes. *Sustained depolarized, silent state (near-complete Nav1.8 inactivation), not repetitive firing. \u2020Delayed-onset, duration-dependent; excluded as non-physiological per the Section III-F/III-I artifact-detection protocol."));

// IV. DISCUSSION
body.push(SectionHeading("IV", "Discussion"));
body.push(FirstLineIndentP([
  "Across both phases of this study (classical HH and literature-derived Na", new TextRun({text:"v",size:20,italics:true}), "1.8/1.9 C-fiber kinetics) and across single-pulse stimulation, tonic sensitization, and high-frequency temporal summation, direct A\u03b2-to-C ephaptic coupling between a single fiber pair never drives an ectopic nociceptor spike at physiologically-calibrated coupling strength. This convergence across two biophysically distinct channel models is, we argue, stronger evidence against single-fiber-pair crosstalk as a stand-alone allodynia mechanism than either phase would provide alone: it rules out the specific objection that a classical-HH nociceptor model is simply the wrong biology, since replacing it with realistic Na", new TextRun({text:"v",size:20,italics:true}), "1.8/1.9 kinetics (which do materially change how the model fails (a genuine, if narrow, graded sensitized window rather than an immediate bifurcation into spontaneous firing)) does not change the outcome.",
]));
body.push(FirstLineIndentP([
  "What does change the outcome, at least partially, is abandoning the single-fiber-pair assumption altogether. The multi-fiber bundle result of Section III-I is the first mechanism tested in this study, across either phase, to produce a substantial, non-artifactual trend toward threshold (an order of magnitude larger than any single-pair effect) and it is directly compatible with the anatomy motivating the ephaptic hypothesis in the first place: a Remak bundle or compressed nerve segment does not contain one A\u03b2 fiber and one C-fiber in isolation, but many afferents of both types sharing a genuinely restricted extracellular space. A mechanical stimulus recruiting several A\u03b2 mechanoreceptors simultaneously (as ordinary light touch or a brushing stimulus naturally would) is precisely the scenario the multi-fiber protocol models. This is also consistent with the earliest experimental reports of cross-excitation in dorsal root ganglia, which document functional coupling between populations of afferents rather than isolated fiber pairs [5], [6].",
]));
body.push(FirstLineIndentP([
  "This finding must, however, be reported with the same caution applied throughout this study to any candidate positive result. We could not extend the verified-stable range past n = 25 fibers without encountering the same explicit-coupling numerical artifact documented in Section III-F, and we make no claim about whether the trend observed here would continue, saturate, or cross threshold at larger, more anatomically realistic bundle sizes. The honest conclusion is that multi-fiber spatial summation is a mechanistically plausible and partially-supported candidate mechanism for ephaptic contributions to dynamic mechanical allodynia (the most promising of everything tested in this study) whose confirmation or refutation requires numerical methods not limited by the stability ceiling identified here.",
]));

body.push(SubHeading("A", "Limitations"));
body.push(FirstLineIndentP([
  "This study uses a one-dimensional core-conductor approximation of a fully three-dimensional, tortuous extracellular geometry and a purely ohmic extracellular medium. As established in Section III-A, the reported A\u03b2 conduction velocity is discretization-dependent because nodal membrane area is tied to \u0394z rather than fixed at the physiological node width; all comparisons in this study use a single, consistent discretization, but the absolute CV should not be over-interpreted as a grid-independent physical prediction. The multi-fiber bundle (Section II-F) assumes identical, perfectly synchronous A\u03b2 fibers by symmetry; asynchronous recruitment, fiber-to-fiber heterogeneity, and summation among multiple C-fibers (rather than convergence onto one) are not tested. The extracellular regularization parameter \u03ba, while calibrated to produce physiologically plausible field magnitudes for a single active node and re-verified for the multi-fiber source magnitude, is not derived from first-principles bundle histology. Most importantly, the explicit treatment of the ephaptic feedback term imposes a hard numerical ceiling (n \u2264 25 fibers in this study) beyond which candidate results cannot currently be distinguished from artifact; this ceiling, not any biophysical saturation, is what bounds our multi-fiber conclusion.",
]));
body.push(FirstLineIndentP([
  "The 1D approximation in particular assumes a uniform, annular extracellular cleft along the full fiber length. Real compressed or demyelinated nerve segments instead present highly tortuous, non-uniform 3D extracellular spaces, in which locally tight pockets of apposition can produce field concentrations that a longitudinally-averaged 1D cable equation is structurally unable to represent. Fully coupled 3D finite-element Extracellular\u2013Membrane\u2013Intracellular (EMI) formulations, recently applied to ephaptic coupling and extracellular stimulation in central neurons [32], [33], provide a template for such a model; applying this approach to the true extracellular geometry of a compressed or demyelinated peripheral nerve bundle could both reveal localized field hotspots that the 1D approximation averages out and, being naturally suited to multi-fiber geometries, remove the explicit-coupling ceiling that bounds the present multi-fiber result.",
]));

// V. FUTURE WORK
body.push(SectionHeading("V", "Future Work"));
body.push(FirstLineIndentP([
  "Five extensions follow directly from the results and limitations above. (1) A fully implicit joint solver for the coupled cable, multi-fiber source, and extracellular Poisson systems is now concretely motivated, not merely plausible: it is the specific requirement for testing whether the multi-fiber trend of Section III-I continues past n = 25 and crosses threshold at anatomically realistic bundle sizes, and would remove the explicit-coupling stability ceiling documented in Sections III-F and III-I entirely. (2) Asynchronous or jittered multi-fiber recruitment (relaxing the perfectly-synchronous assumption of Section II-F) would test whether spatial summation requires coincident A\u03b2 firing or tolerates the timing dispersion expected from a real, spatially-extended receptive field. (3) Further refinement of nociceptor channel kinetics, e.g., incorporating Na", new TextRun({text:"v",size:20,italics:true}), "1.7 [29] alongside Na", new TextRun({text:"v",size:20,italics:true}), "1.8/1.9, or adopting a full published parameterization such as Tigerholm ", new TextRun({text:"et al.", italics:true}), " or Sundt ", new TextRun({text:"et al.", italics:true}), " [30], [31] in place of the simplified constant-time-constant formulation used here, could widen the narrow graded-sensitization window identified in Section III-H. (4) A 3D finite-element EMI representation [32], [33] of the true, non-uniform extracellular geometry at a compression or demyelination site, applied to a multi-fiber bundle rather than a single fiber pair, would address the two most consequential simplifications in this study (1D geometry and the explicit-coupling ceiling) simultaneously. (5) Decoupling nodal membrane area from grid resolution (Section III-A), e.g., by fixing each node of Ranvier's physical width independent of \u0394z, would remove the discretization-dependence identified in the conduction-velocity convergence check and allow a grid-independent CV to be reported.",
]));

// VI. CONCLUSION
body.push(SectionHeading("VI", "Conclusion"));
body.push(FirstLineIndentP([
  "A closed-loop, biophysically validated core-conductor model coupling a myelinated A\u03b2-fiber and a C-fiber through a shared, pathologically restricted extracellular space finds no evidence that single-fiber-pair ephaptic crosstalk (under single-pulse stimulation, plausible tonic sensitization, or high-frequency temporal summation) is sufficient to trigger an ectopic nociceptor spike, and this conclusion holds under both classical Hodgkin-Huxley and literature-derived Na", new TextRun({text:"v",size:20,italics:true}), "1.8/Na", new TextRun({text:"v",size:20,italics:true}), "1.9 nociceptor channel kinetics. Extending the model to a multi-fiber bundle, in which several synchronously-active A\u03b2 afferents share an extracellular compartment with one C-fiber, produces the first substantial, non-artifactual trend toward threshold identified in this study; verified via a dedicated timing/duration/geometry-independence protocol that also exposes a specific, reproducible numerical-artifact signature relevant to any closed-loop ephaptic model using an explicit coupling scheme. This trend does not cross threshold within the numerically trustworthy range (n \u2264 25 fibers), and we do not claim that it would at larger bundle sizes; rather, this result reframes the central open question of ephaptic allodynia research from whether single-fiber-pair crosstalk is sufficient (it is not) to whether multi-fiber spatial summation is (plausible, unconfirmed), and it identifies the fully implicit multi-fiber solver needed to answer that question.",
]));

// NOMENCLATURE
body.push(PlainHeading("Nomenclature"));
body.push(new Table({
  width: { size: 4700, type: WidthType.DXA },
  columnWidths: [1000, 3700],
  rows: [
    new TableRow({ children: [cell("Symbol", { width: 1000, bold: true, shade: true }), cell("Definition", { width: 3700, bold: true, shade: true, align: AlignmentType.LEFT })] }),
    new TableRow({ children: [cell("v_{m,k}", { width: 1000 }), cell("Transmembrane potential of axon k (A\u03b2 = 1, C = 2)", { width: 3700, align: AlignmentType.LEFT })] }),
    new TableRow({ children: [cell("u_e", { width: 1000 }), cell("Shared extracellular potential", { width: 3700, align: AlignmentType.LEFT })] }),
    new TableRow({ children: [cell("r_e, \u03ba", { width: 1000 }), cell("Extracellular longitudinal resistance per unit length; Poisson regularization constant", { width: 3700, align: AlignmentType.LEFT })] }),
    new TableRow({ children: [cell("w_cleft", { width: 1000 }), cell("Extracellular cleft width", { width: 3700, align: AlignmentType.LEFT })] }),
    new TableRow({ children: [cell("\u03c1_i, \u03c1_e", { width: 1000 }), cell("Axoplasmic / extracellular resistivity", { width: 3700, align: AlignmentType.LEFT })] }),
    new TableRow({ children: [cell("d_1, d_2", { width: 1000 }), cell("A\u03b2 / C-fiber diameter", { width: 3700, align: AlignmentType.LEFT })] }),
    new TableRow({ children: [cell("g\u030418, g\u030419", { width: 1000 }), cell("Maximum Nav1.8 / Nav1.9 conductance density", { width: 3700, align: AlignmentType.LEFT })] }),
    new TableRow({ children: [cell("\u0394V_shift", { width: 1000 }), cell("Uniform HH gating-kinetics voltage shift (Phase 1 sensitization)", { width: 3700, align: AlignmentType.LEFT })] }),
    new TableRow({ children: [cell("n", { width: 1000 }), cell("Number of synchronously-active A\u03b2 fibers (multi-fiber bundle)", { width: 3700, align: AlignmentType.LEFT })] }),
    new TableRow({ children: [cell("\u0394z, \u0394t", { width: 1000 }), cell("Spatial / temporal discretization step", { width: 3700, align: AlignmentType.LEFT })] }),
  ],
}));
body.push(new Paragraph({ spacing: { after: 200 }, children: [] }));

// END MATTER
body.push(PlainHeading("Data and Code Availability"));
body.push(FirstLineIndentP([
  "The simulation code implementing the core-conductor model, the CRRSS, classical HH, and Nav1.8/Nav1.9 kinetics, the multi-fiber bundle formulation, and the artifact-detection protocols described in this paper is available from the corresponding author upon reasonable request, and will be deposited in a public repository upon publication.",
]));
body.push(PlainHeading("Acknowledgment"));
body.push(FirstLineIndentP([
  "The authors thank [to be completed] for helpful discussion.",
]));

body.push(PlainHeading("References"));

function refP(num, text) {
  return new Paragraph({
    alignment: AlignmentType.JUSTIFIED,
    spacing: { after: 60 },
    indent: { left: convertInchesToTwip(0.22), hanging: convertInchesToTwip(0.22) },
    children: [new TextRun({ text: `[${num}]\u2002${text}`, font: FONT, size: 18 })],
  });
}

const references = [
  "A. Arvanitaki, \u201cEffects evoked in an axon by the activity of a contiguous one,\u201d J. Neurophysiol., vol. 5, no. 2, pp. 89\u2013108, Mar. 1942.",
  "B. Katz and O. H. Schmitt, \u201cElectric interaction between two adjacent nerve fibres,\u201d J. Physiol., vol. 97, no. 4, pp. 471\u2013488, Feb. 1940.",
  "Z. H. Rappaport and M. Devor, \u201cTrigeminal neuralgia: The role of self-sustaining discharge (ignition) in the medicine and surgery of paroxysmal pain,\u201d Pain, vol. 56, no. 2, pp. 127\u2013138, Feb. 1994.",
  "A. Asmedi, S. Wibowo, and L. Meliala, \u201cEphaptic crosstalk in painful diabetic neuropathy: An electrodiagnostic study,\u201d J. Med. Sci. (Berkala Ilmu Kedokteran), vol. 50, no. 2, pp. 173\u2013179, Apr. 2018.",
  "M. Devor and P. D. Wall, \u201cCross-excitation in dorsal root ganglia of nerve-injured and intact rats,\u201d J. Neurophysiol., vol. 64, no. 6, pp. 1733\u20131744, Dec. 1990.",
  "R. Amir and M. Devor, \u201cFunctional cross-excitation between afferent A- and C-neurons in dorsal root ganglia,\u201d Neuroscience, vol. 95, no. 1, pp. 189\u2013195, Jan. 2000.",
  "Z. Seltzer and M. Devor, \u201cEphaptic transmission in chronically damaged peripheral nerves,\u201d Neurology, vol. 29, no. 7, pp. 1061\u20131064, Jul. 1979.",
  "M. Rasminsky, \u201cEphaptic transmission between single nerve fibres in the spinal nerve roots of dystrophic mice,\u201d J. Physiol., vol. 305, no. 1, pp. 151\u2013169, Aug. 1980.",
  "H. Lind\u00e9n, T. Hagen, J. H. \u0141\u0119ski, E. S. Norheim, J. H. Pettersen, and G. T. Einevoll, \u201cLFPy: A tool for biophysical simulation of extracellular potentials generated by detailed model neurons,\u201d Front. Neuroinform., vol. 7, p. 41, Jan. 2014.",
  "J. W. Clark and R. Plonsey, \u201cThe extracellular potential field of the single active nerve fiber in a volume conductor,\u201d Biophys. J., vol. 8, no. 7, pp. 842\u2013864, Jul. 1968.",
  "H. Schmidt, G. Hahn, G. Deco, and T. R. Kn\u00f6sche, \u201cEphaptic coupling in white matter fibre bundles modulates axonal transmission delays,\u201d PLOS Comput. Biol., vol. 17, no. 2, p. e1007858, Feb. 2021.",
  "E. Rossoni, B. Tirozzi, and M. S. McDonald, \u201cA model of action potential propagation in bundles of myelinated nerve fibers,\u201d Biol. Cybern., vol. 89, no. 6, pp. 430\u2013440, Dec. 2003.",
  "H. Schmidt and T. R. Kn\u00f6sche, \u201cModelling the effect of ephaptic coupling on spike propagation in peripheral nerve fibres,\u201d Biol. Cybern., vol. 116, no. 4, pp. 461\u2013473, Aug. 2022.",
  "A. R. Shifman and J. E. Lewis, \u201cELFENN: A generalized platform for modeling ephaptic coupling in spiking neuron models,\u201d Front. Neuroinform., vol. 13, p. 35, May 2019.",
  "M. Capllonch-Juan and F. Sepulveda, \u201cModelling the effects of ephaptic coupling on selectivity and response patterns during artificial stimulation of peripheral nerves,\u201d PLOS Comput. Biol., vol. 16, no. 6, p. e1007826, Jun. 2020.",
  "D. P. Marshall, E. S. Farah, E. D. Musselman, N. A. Pelot, and W. M. Grill, \u201cPyFibers: An open-source NEURON-Python package to simulate responses of model nerve fibers to electrical stimulation,\u201d PLOS Comput. Biol., vol. 21, no. 12, p. e1013764, Dec. 2025.",
  "N. A. Pelot, D. C. Catherall, B. J. Thio, N. D. Titus, E. D. Liang, C. S. Henriquez, and W. M. Grill, \u201cExcitation properties of computational models of unmyelinated peripheral axons,\u201d J. Neurophysiol., vol. 125, no. 5, pp. 1770\u20131790, May 2021.",
  "S. Y. Chiu, J. M. Ritchie, R. B. Rogart, and D. Stagg, \u201cA quantitative description of membrane currents in rabbit myelinated nerve,\u201d J. Physiol., vol. 292, no. 1, pp. 149\u2013166, Jul. 1979.",
  "J. D. Sweeney, J. T. Mortimer, and D. M. Durand, \u201cModeling of mammalian myelinated nerve for functional neuromuscular stimulation,\u201d in Proc. 9th Ann. Conf. IEEE Eng. Med. Biol. Soc., Boston, MA, USA, 1987, pp. 1577\u20131578.",
  "A. L. Hodgkin and A. F. Huxley, \u201cA quantitative description of membrane current and its application to conduction and excitation in nerve,\u201d J. Physiol., vol. 117, no. 4, pp. 500\u2013544, Aug. 1952.",
  "J. H. Goldwyn and J. Rinzel, \u201cNeuronal coupling by endogenous electric fields: Cable theory and applications to coincidence detector neurons in the auditory brain stem,\u201d J. Neurophysiol., vol. 115, no. 4, pp. 2033\u20132051, Apr. 2016.",
  "M. Schl\u00f6tter, G. U. Maret, and C. J. Kleineidam, \u201cAnnihilation of action potentials induces electrical coupling between neurons,\u201d eLife, vol. 12, p. RP88335, Dec. 2023.",
  "R. Veeraraghavan, J. Lin, G. S. Hoeker, J. P. Keener, R. G. Gourdie, and S. Poelzing, \u201cSodium channels in the Cx43 gap junction perinexus may constitute a cardiac ephapse: An experimental and modeling study,\u201d Pfl\u00fcgers Arch. - Eur. J. Physiol., vol. 467, no. 10, pp. 2081\u20132093, Oct. 2015.",
  "J. Lin and J. Keener, \u201cEphaptic coupling is a mechanism of conduction reserve during reduced gap junction coupling,\u201d Proc. Natl. Acad. Sci. U.S.A., vol. 107, no. 49, pp. 21078\u201321083, Dec. 2010.",
  "A. N. Akopian, L. Sivilotti, and J. N. Wood, \u201cA tetrodotoxin-resistant voltage-gated sodium channel expressed by sensory neurons,\u201d Nature, vol. 379, no. 6562, pp. 257\u2013262, Jan. 1996.",
  "A. H. Klein, A. Vyshnevska, T. V. Hartke, R. De Col, J. L. Mankowski, B. Turnquist, F. Bosmans, P. W. Reeh, M. Schmelz, R. W. Carr, and M. Ringkamp, \u201cSodium channel NaV1.8 underlies TTX-resistant axonal action potential conduction in somatosensory C-fibers of distal cutaneous nerves,\u201d J. Neurosci., vol. 37, no. 21, pp. 5204\u20135214, May 2017.",
  "T. R. Cummins, S. D. Dib-Hajj, J. A. Black, A. N. Akopian, J. N. Wood, and S. G. Waxman, \u201cA novel persistent tetrodotoxin-resistant sodium current in SNS-null and wild-type small primary sensory neurons,\u201d J. Neurosci., vol. 19, no. 24, pp. RC43(1\u20136), Dec. 1999.",
  "M. D. Baker, S. Y. Chandra, Y. Ding, and S. G. Waxman, \u201cGTP-induced tetrodotoxin-resistant Na\u207a current regulates excitability in mouse and rat small diameter sensory neurones,\u201d J. Physiol., vol. 548, no. 2, pp. 373\u2013382, Apr. 2003.",
  "S. D. Dib-Hajj, Y. Yang, J. A. Black, and S. G. Waxman, \u201cThe NaV1.7 sodium channel in health and disease,\u201d Nat. Rev. Neurosci., vol. 14, no. 1, pp. 49\u201362, Jan. 2013.",
  "J. Tigerholm, M. E. Petersson, O. Obreja, A. Lampert, R. Carr, M. Schmelz, and E. Frans\u00e9n, \u201cModeling activity-dependent changes of axonal spike conduction in primary afferent C-nociceptors,\u201d J. Neurophysiol., vol. 111, no. 8, pp. 1721\u20131735, Apr. 2014.",
  "D. Sundt, N. Gamper, and D. B. Jaffe, \u201cSpike propagation through the dorsal root ganglia in an unmyelinated sensory neuron: A modeling study,\u201d J. Neurophysiol., vol. 114, no. 6, pp. 3140\u20133153, Dec. 2015.",
  "K. H. J\u00e6ger and A. Tveito, \u201cExtracellular stimulation and ephaptic coupling of neurons in a fully coupled finite element-based Extracellular\u2013Membrane\u2013Intracellular (EMI) model,\u201d Front. Comput. Neurosci., vol. 20, p. 1755548, Jan. 2026.",
  "K. H. J\u00e6ger, A. Tveito, and colleagues, \u201cA cell-based Extracellular-Membrane-Intracellular (EMI) model of excitable tissue,\u201d Front. Physiol., vol. 12, p. 811029, Dec. 2021.",
  "K. S. Han, C. Guo, C. H. Chen, L. Witter, T. Osorno, and W. G. Regehr, \u201cEphaptic coupling promotes synchronous firing of cerebellar Purkinje cells,\u201d Neuron, vol. 100, no. 3, pp. 564\u2013578, Nov. 2018.",
  "H. Bokil, N. Laaris, K. Blinder, M. Ennis, and A. Keller, \u201cEphaptic interactions in the mammalian olfactory system,\u201d J. Neurosci., vol. 21, no. 20, pp. RC173(1\u20135), Oct. 2001.",
];

references.forEach((text, i) => body.push(refP(i + 1, text)));

// ---------------------------------------------------------------
// Assemble: title/abstract (1-col) -> body part 1 (2-col) -> fig1 (1-col)
// -> body part 2 (2-col) -> fig2 (1-col) -> body part 3 (2-col, incl refs)
// ---------------------------------------------------------------
function splitAtMarker(arr, marker) {
  const idx = arr.findIndex(p => p && p.FIGURE_BREAK === marker);
  if (idx < 0) return [arr, []];
  return [arr.slice(0, idx), arr.slice(idx + 1)];
}

const [beforeFig0, afterFig0] = splitAtMarker(body, "fig0");
const [beforeFig1, afterFig1] = splitAtMarker(afterFig0, "fig1");
const [beforeFig2, afterFig2] = splitAtMarker(afterFig1, "fig2");

const fig0Buffer = fs.readFileSync("./source_figures/fig0_schematic.png");
const fig1Buffer = fs.readFileSync("./source_figures/fig1_positive_control.png");
const fig2Buffer = fs.readFileSync("./source_figures/fig2_navc_bundle.png");

function figureSection(buffer, wIn, hIn, label, captionText) {
  return [
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { before: 120, after: 40 },
      children: [new ImageRun({ data: buffer, type: "png", transformation: { width: Math.round(wIn*96), height: Math.round(hIn*96) } })],
    }),
    captionP(label, captionText),
  ];
}

const fig0Section = figureSection(fig0Buffer, 6.0, 2.562, "Fig. 0",
  "Model architecture (simplified schematic). A myelinated A\u03b2 fiber and an unmyelinated C-fiber are embedded in a shared, geometrically restricted extracellular cleft. Both fibers' transmembrane ionic currents drive a regularized Poisson equation for the shared extracellular potential u_e(z,t), which is solved at every integration time step and fed back into each fiber's cable equation as an ephaptic driving term (double-headed arrows), closing the loop. Full biophysical detail (nodes of Ranvier, internodal myelin, the governing equations, and the multi-fiber extension) is given in Section II.");

const fig1Section = figureSection(fig1Buffer, 7.16, 2.565, "Fig. 1",
  "Positive control confirming both Phase 1 fiber models are independently excitable and conduct correctly, with ephaptic coupling disabled. (a) Isolated A\u03b2-fiber: saltatory action potential recorded at five nodes of Ranvier (z = 1\u20139 mm) following a 100 nA, 0.2 ms current pulse at z = 0, propagating at \u224835.6 m/s. (b) Isolated classical-HH C-fiber: continuously conducted action potential recorded at five positions (z = 1\u20139 mm) following a 1 nA, 1 ms current pulse at z = 0, propagating at \u22480.57 m/s. Both fibers reach full regenerative spike amplitude at every recorded location, confirming that the negative results of Sections III-B\u2013III-F reflect insufficient ephaptic drive rather than an intrinsically inexcitable C-fiber model.");

const fig2Section = figureSection(fig2Buffer, 7.16, 2.497, "Fig. 2",
  "(a) Positive control for the Phase 2 C-fiber: isolated Nav1.8/1.9 C-fiber conducting continuously at \u22480.36 m/s (z = 1\u20139 mm, 3 nA/1 ms stimulus at z = 0), confirming the nociceptor-realistic channel model is independently excitable and propagating before closed-loop coupling is introduced. (b) Multi-fiber spatial summation trend (Section III-I): peak C-fiber depolarization vs. number of synchronized A\u03b2 fibers n, at \u03ba = 2\u00d710\u00b9\u2070 m\u207b\u00b2, restricted to the range (n \u2264 25) independently verified stable under extended-duration simulation. The monotonic \u22488 mV trend does not cross threshold within this verified range.");

const pageProps = { size: { width: 12240, height: 15840 }, margin: { top: 1080, bottom: 1080, left: 1080, right: 1080 } };
const twoCol = { type: SectionType.CONTINUOUS, page: pageProps, column: { count: 2, space: 360 } };
const oneCol = { type: SectionType.CONTINUOUS, page: pageProps };

const doc = new Document({
  styles: { default: { document: { run: { font: FONT, size: BODY_SIZE } } } },
  sections: [
    { properties: { page: pageProps }, children: [...titleBlock, ...abstractBlock] },
    { properties: twoCol, children: beforeFig0 },
    { properties: oneCol, children: fig0Section },
    { properties: twoCol, children: beforeFig1 },
    { properties: oneCol, children: fig1Section },
    { properties: twoCol, children: beforeFig2 },
    { properties: oneCol, children: fig2Section },
    { properties: twoCol, children: afterFig2 },
  ],
});

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync("./ephaptic_crosstalk_paper_IEEE.docx", buf);
  console.log("done");
});
