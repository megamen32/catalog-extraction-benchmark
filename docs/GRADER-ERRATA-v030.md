# Frozen grader0.3.0 drawing-scope erratum

Before the new model cohort began, an adversarial synthetic check exposed an overly broad charge-group scope: `1[,.]2` matched the suffix of an unprinted11,2. Thus a figure titled “11,2Кл IIIСЗ” could supply the1,2Кл III scoped drawing assertion when its diameter phrase matched. This is a narrow false-positive in group association, not a change to the original source annotation.

The separate corrected offline grader0.3.1 adds numeric boundaries to source charge scopes1,2/1,6. It preserves every original fixture byte and all other grading rules. Its release number/digest differs from0.3.0. The frozen native17×3 pipeline, original grader files and112 input pins are not modified.

Original0.3.0 scores remain published as historical measurements. After each cohort, exact retained output JSON is additionally scored with corrected0.3.1 and clearly labeled. No corrected annotation or score enters any tested model context. Results are not retuned to favor observed model output; the regression and fix precede the first model call.

The standalone corrected script requires the public benchmark0.3.0 package. It accepts an explicit fixture/candidate and writes a separate output file; it never overwrites model JSON or old score files.
