# Offline grader 0.3.2: supported symbol/language aliases, exact raw data retained

Frozen 0.3.0 and numeric-scope correction 0.3.1 can falsely reject physically equivalent Latin A versus Cyrillic А current conditions, English unit symbols, and supported English drawing relations. The old algorithm can also miss an explicit English contradiction such as Ø500 being called a cross-arm tube diameter. This separate offline component corrects those matching rules after inference. It changes no fixture, candidate, native program or model context, and retains both previous scores.

Supported aliases are scoped: physical units and numeric current conditions in column metadata; drawing view markers and a documented vocabulary in figure prose; quantity+M+thread diameter only in dimensional fields d1/d2/d3 after every explicit identity/field/unit/bounds/frequency/state condition passed. Product identifiers remain exact. A full pollution-degree header whose meaning and Roman values are intact may carry a contextual С3-for-СЗ abbreviation typo; that typo remains visible in literal_format_differences. Composite lightning-impulse/dry50Hz headers remain invalid independent of aliases.

The material-absence check is labelled unsupported_material_reference. A phrase such as porcelain-style housing is an appearance analogy, not a factual made-of-porcelain assertion. The strict source-absence proxy flags the unsupported material reference equally in Russian and English; raw wording remains available and must not be overstated as a manufacturing claim.

Raw literal cell/header/label metrics and input SHA remain unchanged. A source 4М16 versus output 4M16 dimensional thread is classified literal_script_only_physical_thread_equivalent, rather than conflating a script difference with a wrong physical value. Wrong quantity, diameter, product identity, condition, unit or incomplete field mapping is not rescued. Source fixtures keep the same physical 17-page /520 engineering +21 drawing denominator.

English support is a conservative, explicit alias vocabulary, not universal language-neutral semantic grading. Numeric boundaries, local negation, charge/execution/view scope and unsupported-claim guards remain. Unknown wording stays missing. Uncovered drawing errors such as H+2 versus H±2 remain in the v3 backlog, not retroactively inserted into these 21 checks.

Use the standalone script with the publicly installed base benchmark 0.3.0:

```bash
catalog-bench dataset --dataset engineering-catalogs-v2 --export dataset-v2
python catalog-language-grader-v0.3.2.py --fixture dataset-v2/fixtures/catalog-1-page-039.json catalogue-page.json --output score-v0.3.2.json
```

Regraded outputs are published separately under examples/offline-regrading/2026-10-12-v032; original 030/031 results and exact model outputs are retained. The profile comparison is between complete integrations with different parsers, prompts, tools and output contracts, not a pure model A/B. In particular, an advertised JSON-object option is not sent in Project X's Anthropic request body; declared settings alone do not establish identical provider requests.
