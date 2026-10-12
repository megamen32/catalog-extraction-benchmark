"""Aggregate only comparable cells of a matrix; never discard failed cases."""
from collections import defaultdict
from .dataset import load_dataset


def summarize(results):
    cases = {c['id']: c for c in load_dataset()['cases']}
    groups = defaultdict(list)
    for run in results['runs']:
        groups[run['project'], run['model'], run.get('stage'), run.get('repeat', 1)].append(run)
    rows = []
    for (project, model, stage, repeat), runs in sorted(groups.items(), key=lambda x: str(x[0])):
        correct = scored = unavailable = 0
        families = defaultdict(lambda: [0, 0])
        seen = set()
        for run in runs:
            cid = run['case_id']
            if cid in seen:
                raise ValueError('Duplicate case in comparison cohort')
            seen.add(cid)
            expected = cases.get(cid, {}).get('coverage', {}).get('engineering_facts', 0)
            factscore = run.get('score', {}).get('engineering_facts')
            family = cases.get(cid, {}).get('product_family', cid)
            if run['status'] == 'completed' and factscore:
                if expected and expected != factscore['expected']:
                    raise ValueError('Result coverage differs from frozen dataset')
                expected = factscore['expected']
                correct += factscore['correct']; scored += expected
                families[family][0] += factscore['correct']
            else:
                unavailable += expected
            families[family][1] += expected
        denominator = scored + unavailable
        times=[r.get('elapsed_seconds') for r in runs]
        known_times=[t for t in times if isinstance(t,(int,float)) and not isinstance(t,bool)]
        versions=[r.get('tested_program') for r in runs if r.get('tested_program')]
        methods=[r.get('test_method') for r in runs if r.get('test_method')]
        rows.append({'tested_program_versions':versions,'test_methods':methods,
                     'elapsed_seconds_total':round(sum(known_times),3) if len(known_times)==len(runs) else None,
                     'known_elapsed_seconds_total':round(sum(known_times),3) if known_times else None,
                     'runs_with_known_time':len(known_times),
                     'project': project, 'model': model, 'stage': stage, 'repeat': repeat,
                     'cases_attempted': len(runs), 'case_ids': sorted(seen),
                     'completed_cases': sum(r['status'] == 'completed' for r in runs),
                     'correct': correct, 'scored_facts': scored, 'unavailable_facts': unavailable,
                     'percent_on_attempted_cases': round(100*correct/denominator, 2) if denominator else None,
                     'family_macro_percent_on_attempted_cases': round(sum(100*a/b for a,b in families.values() if b)/sum(bool(b) for a,b in families.values()), 2) if any(b for a,b in families.values()) else None,
                     'whole_page_accuracy': False})
    comparable = len({tuple(r['case_ids']) for r in rows}) <= 1
    return {'cohorts': rows, 'same_attempted_case_set': comparable,
            'matrix_complete': results.get('complete', False),
            'note': 'Missing or unattempted cases remain visible. Compare identical case sets, stages, grader and dataset versions; no overall model ranking is inferred.'}
