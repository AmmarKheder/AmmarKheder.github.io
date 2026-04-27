#!/usr/bin/env python3
"""Generate a sober two-page PDF CV for Ammar Kheder using fpdf2.

Output: /scratch/project_462000640/ammar/portfolio/AmmarKheder-CV.pdf
"""

from pathlib import Path

from fpdf import FPDF

OUT = Path(__file__).resolve().parent.parent / "AmmarKheder-CV.pdf"


# --- helpers --------------------------------------------------------------- #


class CV(FPDF):
    """A sober single-column CV layout."""

    INK = (20, 20, 20)
    MUTED = (110, 110, 110)
    ACCENT = (0, 0, 136)  # navy, same as the website
    RULE = (210, 210, 210)

    def header(self) -> None:  # type: ignore[override]
        # Footer/header are drawn manually per page; nothing on auto header.
        pass

    def footer(self) -> None:  # type: ignore[override]
        self.set_y(-12)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*self.MUTED)
        self.cell(
            0, 5,
            f"Ammar Kheder  |  ammarkheder.github.io  |  page {self.page_no()}/{{nb}}",
            align="C",
        )

    # --- typographic primitives --- #
    def name_block(self) -> None:
        self.set_font("Helvetica", "B", 22)
        self.set_text_color(*self.INK)
        self.cell(0, 9, "Ammar Kheder", new_x="LMARGIN", new_y="NEXT")

        self.set_font("Helvetica", "", 11)
        self.set_text_color(*self.MUTED)
        self.cell(
            0, 5,
            "Doctoral Researcher in Computational Engineering, LUT University, AMC-Lahti",
            new_x="LMARGIN", new_y="NEXT",
        )

        self.set_font("Helvetica", "", 9)
        self.set_text_color(*self.INK)
        # Two compact lines so the right margin is never overflown.
        line1 = [
            "ammar.kheder@lut.fi",
            "ammarkheder.github.io",
            "ORCID 0009-0001-2306-1223",
        ]
        line2 = [
            "github.com/AmmarKheder",
            "linkedin.com/in/ammar-kheder",
            "Scholar: ZYvKJF4AAAAJ",
        ]
        self.cell(0, 4.5, "  ".join(f"- {c}" for c in line1),
                  new_x="LMARGIN", new_y="NEXT")
        self.cell(0, 4.5, "  ".join(f"- {c}" for c in line2),
                  new_x="LMARGIN", new_y="NEXT")
        self.ln(2)
        self.draw_rule()
        self.ln(2)

    def section(self, title: str) -> None:
        self.ln(2)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(*self.ACCENT)
        self.cell(0, 6, title.upper(), new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(*self.INK)
        self.draw_rule()
        self.ln(0.5)

    def draw_rule(self) -> None:
        self.set_draw_color(*self.RULE)
        self.set_line_width(0.2)
        y = self.get_y()
        self.line(self.l_margin, y, self.w - self.r_margin, y)

    def entry(
        self,
        date: str,
        title: str,
        place: str = "",
        body: str = "",
    ) -> None:
        # date column (left, fixed width)
        date_w = 28
        x0 = self.l_margin
        y0 = self.get_y()

        self.set_xy(x0, y0)
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*self.MUTED)
        self.cell(date_w, 4.5, date)

        self.set_xy(x0 + date_w, y0)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*self.INK)
        self.multi_cell(0, 4.8, title, new_x="LMARGIN", new_y="NEXT")

        if place:
            self.set_x(x0 + date_w)
            self.set_font("Helvetica", "I", 9)
            self.set_text_color(*self.MUTED)
            self.multi_cell(0, 4.5, place, new_x="LMARGIN", new_y="NEXT")

        if body:
            self.set_x(x0 + date_w)
            self.set_font("Helvetica", "", 9)
            self.set_text_color(*self.INK)
            self.multi_cell(0, 4.3, body, new_x="LMARGIN", new_y="NEXT")

        self.ln(1.2)

    def bullet(self, text: str) -> None:
        self.set_x(self.l_margin)
        self.set_font("Helvetica", "", 9)
        self.set_text_color(*self.INK)
        self.cell(4, 4.3, "-")
        self.multi_cell(0, 4.3, text, new_x="LMARGIN", new_y="NEXT")

    def pub(
        self,
        title: str,
        authors: str,
        venue: str,
        cites: int | None = None,
    ) -> None:
        self.set_x(self.l_margin)
        self.set_font("Helvetica", "B", 9.5)
        self.set_text_color(*self.INK)
        if cites is None:
            suffix = ""
        else:
            word = "citation" if cites == 1 else "citations"
            suffix = f"  [{cites} {word}]"
        self.multi_cell(0, 4.6, title + suffix, new_x="LMARGIN", new_y="NEXT")

        self.set_font("Helvetica", "", 9)
        self.set_text_color(*self.INK)
        self.multi_cell(0, 4.3, authors, new_x="LMARGIN", new_y="NEXT")

        self.set_font("Helvetica", "I", 9)
        self.set_text_color(*self.MUTED)
        self.multi_cell(0, 4.3, venue, new_x="LMARGIN", new_y="NEXT")
        self.ln(1.2)


# --- content --------------------------------------------------------------- #


def build() -> Path:
    pdf = CV(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=14)
    pdf.set_margins(left=18, top=14, right=18)
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.name_block()

    # ---- Profile ---- #
    pdf.section("Profile")
    pdf.set_font("Helvetica", "", 9.5)
    pdf.set_text_color(*pdf.INK)
    pdf.multi_cell(
        0, 4.6,
        "Doctoral researcher in computational engineering at LUT University, working "
        "on neural architectures that explicitly encode atmospheric physics for air "
        "quality and Earth system prediction. Hands-on experience with large-scale "
        "distributed training on the LUMI supercomputer (up to 1,024 AMD MI250X GPUs). "
        "Lead author of TopoFlow (npj Climate and Atmospheric Science, 2026). Founder "
        "and CEO of Wabel Group, an AI and web development company.",
    )

    # ---- Education ---- #
    pdf.section("Education")
    pdf.entry(
        "2024 - now",
        "Ph.D., Computational Engineering",
        "LUT University, Lahti, Finland",
        "Atmospheric Modelling Centre (AMC-Lahti). Supervisors: Prof. Michael Boy, "
        "Assoc. Prof. Zhi-Song Liu.",
    )
    pdf.entry(
        "2021 - 2024",
        "M.Sc., Engineering (Big Data and Artificial Intelligence)",
        "EiCnam Paris, France",
        "Apprenticeship at INRIA Bordeaux (Mnemosyne team).",
    )
    pdf.entry(
        "2019 - 2021",
        "B.Sc., Data Science (BUT STID)",
        "BUT Niort, Universite de Poitiers, France",
        "Statistics, big data, business intelligence, data science.",
    )

    # ---- Experience ---- #
    pdf.section("Experience")
    pdf.entry(
        "2024 - now",
        "Junior Researcher and Teaching Assistant",
        "LUT University, Computational Engineering",
        "Research on physics-informed deep learning for atmospheric science. "
        "Teaching assistant for Foundations of AI and Machine Learning (twice) "
        "and Foundations of Computer Science. "
        "Contributor to the AMC-Lahti summer school (25 participants, 2025).",
    )
    pdf.entry(
        "2023 - 2026",
        "CEO and Founder, Wabel Group",
        "AI services and web development",
        "Built cDESP, a B2B SaaS compliance platform for industrial refrigeration "
        "pressure equipment, in production for DCRR.",
    )
    pdf.entry(
        "2021 - 2022",
        "Research Engineer (Apprenticeship)",
        "INRIA Bordeaux, Mnemosyne team",
        "Worked on LingoRob, a crowdsourcing platform for multi-language linguistic "
        "corpora used to train Reservoir Computing models for human-robot interaction. "
        "Supervisor: Xavier Hinaut.",
    )
    pdf.entry(
        "2021 - 2023",
        "Volunteer Firefighter",
        "Sapeurs-Pompiers des Deux-Sevres (SDIS 79), France",
        "2 years 8 months of on-call service. Certifications: FISPV, PSC 1, PSE 1, "
        "PSE 2, SAP, INC 1, DIV.",
    )

    # ---- Publications ---- #
    pdf.section("Publications")
    pdf.pub(
        "TopoFlow: topography-aware pollutant Flow learning for high-resolution "
        "air quality prediction.",
        "A. Kheder, H. Toropainen, W. Peng, S. Antao, J. Chen, M. Boy, Z.-S. Liu.",
        "npj Climate and Atmospheric Science (Nature Portfolio), 2026. "
        "DOI: 10.1038/s41612-026-01417-5",
    )
    pdf.pub(
        "CRAN-PM: Cross-Resolution Attention Network for High-Resolution PM2.5 "
        "Prediction.",
        "A. Kheder et al.",
        "Preprint, 2026 (under review). arXiv:2603.11725",
    )
    pdf.pub(
        "Inverse Neural Operator for ODE Parameter Optimization.",
        "Z.-S. Liu, W. Peng, H. Toropainen, A. Kheder, A. Rupp, H. Froning, X. Lin, "
        "M. Boy.",
        "Preprint, 2026. arXiv:2603.11854",
    )
    pdf.pub(
        "Deep Spatio-Temporal Neural Network for Air Quality Reanalysis.",
        "A. Kheder, B. Foreback, L. Wang, Z.-S. Liu, M. Boy.",
        "Scandinavian Conference on Image Analysis (SCIA 2025), Springer LNCS. "
        "DOI: 10.1007/978-3-031-95911-0_6",
    )

    # ---- Talks and presentations ---- #
    pdf.section("Talks and presentations")
    pdf.bullet("Accepted talk at IAC 2026 (International Aerosol Conference), Xi'an, "
               "China.")
    pdf.bullet("EAC 2025 (European Aerosol Conference), Lecce, Italy. AQ-Net poster.")
    pdf.bullet("SCIA 2025, Reykjavik, Iceland. Speed talk and poster, Springer LNCS "
               "publication.")
    pdf.bullet("LUT Doctoral School Science Conference 2025 (20 May), Lappeenranta.")
    pdf.bullet("Invited visit to BUT SD Niort (5 January 2026): academic and "
               "professional journey.")

    # ---- Selected projects ---- #
    pdf.section("Selected projects")
    pdf.bullet("cDESP, a B2B SaaS compliance platform for industrial refrigeration "
               "pressure equipment. Built by Wabel Group for DCRR. esp.dcrr.fr")
    pdf.bullet("Pokemon Robot Auction (22 Dec 2023, Paris). The world's first Pokemon "
               "card auction co-hosted by a NAO humanoid robot. 1,693 viewers. "
               "Endorsed by the French Presidency.")
    pdf.bullet("LingoRob (INRIA Bordeaux, 2021-2022). Crowdsourcing platform for "
               "multi-language linguistic corpora to train brain-inspired language "
               "models for human-robot interaction.")

    # ---- Teaching ---- #
    pdf.section("Teaching")
    pdf.bullet("BM40A1601 Foundations of AI and Machine Learning, Fall 2024 and Fall "
               "2025 (LUT, blended, Lpr/Lahti).")
    pdf.bullet("BM40A0202 Foundations of Computer Science, Spring 2026 (LUT, blended, "
               "Lpr).")
    pdf.bullet("AMC-Lahti summer school, Application of AI / ML techniques in "
               "Atmospheric Science (11-15 August 2025, 25 participants).")

    # ---- Visits ---- #
    pdf.section("Academic visits")
    pdf.bullet("February 2026: Prof. Jia Chen's group, TU Munich. Atmospheric sensing "
               "and AI.")
    pdf.bullet("July 2025: Istanbul Technical University. Air quality modelling with "
               "Dr Metin Baykara.")
    pdf.bullet("April 2025: INRIA Bordeaux (N. Rougier and F. Alexandre) and Ecole "
               "Polytechnique Paris (V. Kalogeiton and M.-P. Cani).")
    pdf.bullet("October 2025: LUMI training, Tallinn. Supercomputing, GPU profiling, "
               "performance optimisation.")

    # ---- Skills ---- #
    pdf.section("Technical skills")
    pdf.bullet("Programming: Python (PyTorch, NumPy, scientific stack), C, SQL, "
               "JavaScript, HTML / CSS, VBA.")
    pdf.bullet("HPC: distributed training on LUMI (up to 1,024 AMD MI250X GPUs), DDP, "
               "ROCm / CUDA, Slurm, Zarr.")
    pdf.bullet("Deep learning: vision transformers, recurrent and graph neural "
               "networks, physics-informed and Reservoir Computing models.")
    pdf.bullet("Web and product: Django, Flask, full-stack web, B2B SaaS delivery.")

    # ---- Languages ---- #
    pdf.section("Languages")
    pdf.bullet("French: native.")
    pdf.bullet("Arabic: native.")
    pdf.bullet("English: fluent (working language at LUT and in research).")

    pdf.output(str(OUT))
    return OUT


if __name__ == "__main__":
    p = build()
    print(f"Wrote {p} ({p.stat().st_size / 1024:.1f} KB)")
