# Future hard cases — independent visual audit leads

These leads are outside the frozen17-case dataset v2 and all current three-round inputs. They require fresh independent source inspection/annotation before any future v3 fixture is released. They are not supplied to the current benchmark models and change no existing denominator or score.

Source: public60-page OPN catalogue, SHA256 `300f06a65b18b1656c589e85c94eb29486aaf6d16a5c10b0544dbdc51666adc2`.

| Physical page | Source-grounded failure to cover | Evidence status |
|---|---|---|
|42|Central circular elements in viewБ were assigned a grounding-M10 function; the printed grounding callout points to a side element of the lower principal-view assembly.|Full original and drawing/table zooms reviewed by catalogue owner;48 literal table cells matched. Candidate SHA6cb2b1cb281d6b3050db4f5428b211f6c8ff278beab372ccb651616d1ecc32c6; reviewer SHA0cb8b11666e2fc8b89fe844cf580e47c0405378dcdc354fe7365b81aaa021d39.|
|48|Unprinted porcelain/metal materials and a specifically suspended construction were asserted for the drawing. The source lists several available constructions without identifying the pictured one.|Full original and drawing/table zooms reviewed by catalogue owner;64 literal table cells matched. Candidate SHA2e3f4b51ec7d6e4c291a9f3be8cdfe403895618873352bcfffc0104bad9ebb3d; reviewer SHA2808ec9a98388223a2ef3df17558f336d4e6219f40f51337d16bc131eae67304.|
|47|Unsupported porcelain material claim.|Catalogue owner reported an additional original-image audit finding; exact source/candidate/review binding and independent annotation remain pending.|

The paired42/48 audit confirmed112 literal cells while finding semantic drawing errors. Model acceptance and selected engineering-fact accuracy therefore do not establish full visual correctness. Original candidate bytes were preserved and the live conversion reopened affected pages for independent review; no manual PageContent repair was used.

Canonical next action: independently inspect each original drawing/callout and source paragraph; freeze scoped positive relations and unsupported-claim checks in a new v3 dataset; run new three-round cohorts rather than silently adding facts to v2. Keep all old outputs and scores.
