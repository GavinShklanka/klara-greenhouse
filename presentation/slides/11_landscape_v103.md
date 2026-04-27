---
title: "Where the Landscape Stands"
slug: "landscape_v103"
order: 11
status: "meeting_ready"
audience: "nscc"
show_speaker_notes: true
show_now_next_later: false
show_scope_boundary: false
landscape_reference: "v1.0.3 (canonical) + v1.0.4-candidate (deck framing)"
---

# Where the Landscape Stands <span class="update-badge">v1.0.3 + v1.0.4 candidate</span>

## Klara Greenhouse — Landscape Document v1.0.3 (2026-04-24)

Since our last conversation, the landscape document has been formalized through external stress-testing. This deck reflects v1.0.3 governance language *and* v1.0.4-candidate routing-framing language — used together, deliberately. See the hybrid-framing note below.

---

<div class="section-divider"><span>What v1.0.3 makes explicit</span></div>

**Five operational functions** — one routing core expressed five ways:

1. Small commercial operator improvement (MILP / DP / ML core)
2. Prosumer and household green-space enablement
3. B2B forward-demand declaration (the inverse of a marketplace)
4. Partnership-channeled supplier and advisory routing
5. Excess-routing and community-food-channel strengthening

<div class="decision-callout">
  <div class="decision-label">Decision-support posture (governance backbone)</div>
  <p>Klara suggests; humans decide. The technical core produces alternative paths with explicit feasibility tradeoffs and evidence tiers <span class="ev-badge ev-A">A</span> <span class="ev-badge ev-B">B</span> <span class="ev-badge ev-C">C</span> <span class="ev-badge ev-D">D</span>, not a single recommendation. Operator agency is preserved.</p>
</div>

<div class="routing-callout">
  <div class="routing-label">Routing infrastructure (stakeholder-facing framing — v1.0.4 candidate)</div>
  <p>Klara routes intake through Nova Scotia's existing food and agriculture network. Routing happens at the infrastructure layer; suggesting happens within each route. Both are true; both are load-bearing.</p>
</div>

<div class="territory-callout">
  <div class="territory-label">Mi'kma'ki territory and Indigenous engagement posture</div>
  <p>Klara operates on unceded Mi'kmaw territory. No Mi'kmaw partnership currently exists. Engagement is held as prospective, awaiting institutional introduction. Klara does not claim to advance Mi'kmaw food sovereignty.</p>
</div>

---

<div class="section-divider"><span>What v1.0.3 explicitly disclaims</span></div>

| Klara is NOT | Why it matters to say it |
|---|---|
| A listing site | Listings are passive; Klara is structured intake + evidence-tiered routing + HITL governance |
| An automated recommendation engine | Klara surfaces feasible sets with tradeoffs; the operator chooses |
| A marketplace | No transactions clear through the platform |
| A delivery service | Klara routes compliant paths; does not execute deliveries |
| A food-bank operation | NSH / Summer Street Farm partnerships already serve that need |
| A replacement for Perennia, NSCC, or extension services | Klara routes upstream of extension; suggests when escalation is appropriate |

---

<div class="section-divider"><span>Stress-test status</span></div>

- **Jay (informal reviewer)** — CLOSED, applied in v1.0.1 <span class="ev-badge ev-A">A</span>
- **Roman (informal reviewer)** — OPEN, awaiting feedback on v1.0.3 <span class="ev-badge ev-B">B</span>
- **Mi'kma'ki section** — OPEN for Mi'kmaw-led review through institutional introduction channels <span class="ev-badge ev-C">C</span>
- **Pat Wiggins / NSCC** — current conversation; v1.0.3 is the framing under review <span class="ev-badge ev-A">A</span>

---

<div class="section-divider"><span>One specific Mi'kma'ki ask of NSCC</span></div>

The v1.0.3 landscape names NSCC's documented CMM (Confederacy of Mainland Mi'kmaq) collaboration on the Emergency Management Program as a candidate institutional pathway for Mi'kmaw review of the v1.0.3 Mi'kma'ki section. Offered as a question, not a request for action: would NSCC's existing CMM relationship be an appropriate channel through which to seek Mi'kmaw review of how Klara is framing engagement on Mi'kma'ki?

---

<div class="section-divider"><span>Read v1.0.3 in full</span></div>

The full landscape document is bundled with this deck. Click below to download.

<!-- LANDSCAPE_PDF_DOWNLOAD_BUTTON -->

- Markdown source: `klara_landscape_v1_0_3.md`
- Length: ~12 pages; reading time ~15 minutes
- Audit trail: v1.0 through v1.0.3 preserved; v1.0.3 supersedes prior versions
- v1.0.4 candidate (routing-framing language) currently lives in this deck and pending operator decision on landscape registration

---

> *The v1.0.3 landscape is the document this deck, the BP-in-progress, and the PIVP application all anchor to. If a slide and v1.0.3 disagree on substance, v1.0.3 wins. Routing-framing language layered on top is stylistic anchoring for stakeholder narrative; substance is unchanged.*

<!-- speaker_notes -->
## Speaker Notes

- This slide bridges Roadmap and the Ask. Pat sees the v1.0.3 framing here before responding to the four-part ask on slide 12.
- Lead with the five functions if Pat hasn't seen the PDF; lead with the Mi'kma'ki section if he has.
- The CMM ask is specific and low-burden. Frame as a question; do not push.
- The hybrid routing/suggesting framing is deliberate — explain it openly if asked. Routing = infrastructure. Suggesting = decision discipline. Different layers.
- If he asks for the PDF: he can download from the button on this slide. Send via email after the meeting as well so it lives in his inbox.
- Do not paraphrase the Mi'kma'ki section in conversation — defer to the document.

<!-- do_not_say -->
- Do not soften "unceded Mi'kmaw territory" or "Klara does not claim to advance Mi'kmaw food sovereignty" — protocol-critical.
- Do not present this slide as a list of accomplishments — it's a framing-maturity status update.
- Do not promise Mi'kmaw review on a specific timeline — engagement happens on Mi'kmaw terms or not at all.

<!-- implementation_notes -->
- Streamlit_app.py detects slug=="landscape_v103" after rendering body and calls render_landscape_pdf_download() at the marker line.
- PDF lives at presentation/assets/landscape/Klara_Landscape_v1_0_3.pdf and ships with the deck.
