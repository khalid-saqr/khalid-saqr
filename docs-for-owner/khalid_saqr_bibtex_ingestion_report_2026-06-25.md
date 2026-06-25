# BibTeX Ingestion Report

Generated: 2026-06-25

## Status

The uploaded Scopus BibTeX file was read and indexed into the raw substrate for the planned `khalid-saqr.github.io` repository.

## Counts

- Parsed records: 86
- Articles: 69
- Conference records: 17
- DOI records: 70
- Unique DOIs: 70
- Records without DOI: 16
- Year range: 2007–2026

## Latest indexed records

- 2026 — Resonant spectral cascade in Womersley flow triggered by arterial geometry — Physics of Fluids — https://doi.org/10.1063/5.0319995
- 2026 — A transverse picoNewton force revealed in anisotropic Womersley flow — Scientific Reports — https://doi.org/10.1038/s41598-026-47474-x
- 2025 — Judicial Authority and Rhetorical Strategies in Egyptian Abortion Rulings: A Computational Forensic Analysis — International Journal for the Semiotics of Law — https://doi.org/10.1007/s11196-025-10300-0
- 2025 — Effects of wall compliance on pulsatile flow in a full-scale, patient-specific cerebral aneurysm model: Particle image velocimetry experiments — Medical Engineering and Physics — https://doi.org/10.1016/j.medengphy.2025.104381

## Implementation notes

- Use generated stable publication IDs instead of raw BibTeX keys because the export includes duplicate `Saqr2026` keys.
- Treat DOI records from the BibTeX export as the publication DOI authority layer.
- Treat CV Markdown as a biography/roles/claims source, not as the DOI authority layer.
- Keep source files under `/source/`; derive redacted public files under `/content/` and `/data/`.