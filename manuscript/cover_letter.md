[Date of submission]

The Editors
*Journal of Computational Neuroscience*

Dear Editors,

Please find enclosed the revised version of "Ephaptic Aβ-to-C-Fiber Crosstalk and Multi-Fiber Spatial Summation: A Closed-Loop Core-Conductor Study with Nociceptor-Realistic Channel Kinetics", submitted as an Original Article to the *Journal of Computational Neuroscience*, together with a point-by-point response to both reviewers.

I am grateful to the reviewers for reports that went into the implementation as well as the text. Reviewer 2's second major comment identified an error in the Aβ membrane's inactivation gate, and following it up led me to a second, independent error in the coupling scheme: the extracellular potential was lagged by one time step, so the solver's error grew with the number of fibers. Both are corrected, everything has been recomputed on one consistent model, and the central multi-fiber claim of the submitted version is withdrawn: summation does not saturate and does not approach threshold, it is limited by failure of the Aβ action potential under the very confinement that strengthens the coupling. The title has been changed accordingly. The response letter states this before the point-by-point replies rather than leaving it to be inferred.

Ephaptic excitation of C-fiber nociceptors by myelinated Aβ afferents at sites of nerve injury is often invoked as a peripheral mechanism of tactile allodynia, but whether it can reach threshold has not been settled quantitatively. We address this question with a closed-loop core-conductor model of a CRRSS Aβ axon and a C-fiber, with either classical or Nav1.8/Nav1.9 kinetics, sharing a restricted compartment along a focal lesion. Three features distinguish the revised study:

- **Verified numerics.** Intracellular and extracellular potentials are solved monolithically, and every reported endpoint is shown to converge. We show that a lagged coupling scheme, of the kind commonly used for such models, produces an apparent saturation of multi-fiber summation whose error grows with the number of fibers.
- **Excitability measured directly.** We characterize the C-fiber's excitability for the brief, local drive that ephaptic coupling produces, through strength–duration curves and a safety factor on the recorded extracellular potential, rather than through a nominal voltage threshold.
- **A broad sensitivity analysis.** We map the outcome over the number of synchronous fibers (equivalently the extracellular area per fiber), five decades of extracellular leak, lesion length, stimulus strength, temporal dispersion, repetitive trains, sensitizing bias and C-fiber kinetics.

The main result is that the drive (≈70 µs, spatially narrow and carrying little net charge) stays far below threshold for standard C-fiber membranes; at 25 synchronous fibers it would have to be amplified 4.6-fold to fire the Nav1.8/Nav1.9 fiber. Multi-fiber summation is limited by failure of Aβ conduction under the very confinement that strengthens the coupling. Excitation appears only for fast C-fiber membranes combined with extreme confinement. These results define the conditions an experimental demonstration of ephaptic Aβ→C excitation would have to meet.

All code, data and the scripts that generate every figure, table and quoted number are openly available (https://github.com/MinaSaied23/ephaptic-crosstalk), with a manifest linking every figure, table and number to the script and raw output behind it. The manuscript is not under consideration elsewhere, and the author declares no competing interests.

Sincerely,

Mina Saied Attia Rizk
New Cairo STEM School, Cairo, Egypt
Mina.3024031@stemnewcairo.moe.edu.eg
