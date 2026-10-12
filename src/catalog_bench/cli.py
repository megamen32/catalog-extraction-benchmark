import argparse
import json
from pathlib import Path
import sys

from . import __version__
from .benchmark import score_file
from .dataset import export_dataset, fixture_path, load_dataset, validate_dataset
from .io import write_json


def main():
    parser = argparse.ArgumentParser(description='Independent catalogue extraction benchmark')
    parser.add_argument('--version', action='version', version=__version__)
    subs = parser.add_subparsers(dest='command', required=True)
    data = subs.add_parser('dataset', help='Inspect, verify or export the frozen 15-case dataset')
    data.add_argument('--dataset', default='engineering-catalogs-v1', choices=['engineering-catalogs-v1','engineering-catalogs-v2'])
    data.add_argument('--export', type=Path); data.add_argument('--list', action='store_true')
    score = subs.add_parser('score', help='Grade a page without calling an extraction model')
    selectors = score.add_mutually_exclusive_group(required=True)
    selectors.add_argument('--case'); selectors.add_argument('--fixture', type=Path)
    score.add_argument('--dataset', default='engineering-catalogs-v1', choices=['engineering-catalogs-v1','engineering-catalogs-v2'])
    score.add_argument('candidate', type=Path); score.add_argument('--output', type=Path)
    imp = subs.add_parser('import-jsonl', help='Import a supplied saved-result baseline without inference')
    for flag in ['products', 'characteristics', 'families']:
        imp.add_argument('--'+flag, required=True, type=Path)
    imp.add_argument('--document-id', required=True); imp.add_argument('--page', type=int, required=True); imp.add_argument('--output', required=True, type=Path)
    run = subs.add_parser('run', help='Run explicit project × model × case adapters')
    run.add_argument('manifest', type=Path); run.add_argument('--output', type=Path, required=True); run.add_argument('--resume', action='store_true')
    compare = subs.add_parser('compare', help='Compare saved artifacts without running or repairing them')
    compare.add_argument('manifest', type=Path); compare.add_argument('--output', type=Path, required=True)
    report = subs.add_parser('report', help='Summarize a matrix including failures')
    report.add_argument('results', type=Path); report.add_argument('--output', type=Path)
    demo = subs.add_parser('demo', help='Verify installation using synthetic adapters, with no API keys')
    demo.add_argument('--output', type=Path, required=True)
    scan = subs.add_parser('scan', help='Scan difficulty heuristics; this is not a quality score')
    scan.add_argument('sources', type=Path, nargs='+'); scan.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == 'dataset':
            result = validate_dataset(args.dataset)
            if args.list: result['cases'] = load_dataset(args.dataset)['cases']
            if args.export: result['exported_to'] = str(export_dataset(args.export,args.dataset))
        elif args.command == 'score':
            result = score_file(fixture_path(args.case,args.dataset) if args.case else args.fixture, args.candidate)
            if args.output: write_json(args.output, result)
        elif args.command == 'import-jsonl':
            from .saved_results import import_jsonl
            result = import_jsonl(args.products,args.characteristics,args.families,args.document_id,args.page,args.output)
        elif args.command == 'run':
            from .bench_runner import run_suite
            result = run_suite(args.manifest,args.output,args.resume)
            print(json.dumps({'complete':result['complete'],'runs':len(result['runs']),'results':str(args.output/'results.json')}))
            return 0 if result['complete'] and all(r['status']=='completed' for r in result['runs']) else 2
        elif args.command == 'compare':
            from .compare import compare_saved
            result = compare_saved(args.manifest, args.output.parent / (args.output.stem + '-files'))
            write_json(args.output, result)
            print(json.dumps(result['summary'], ensure_ascii=False, indent=2))
            return 0 if all(r['status']=='completed' for r in result['runs']) else 2
        elif args.command == 'report':
            from .report import summarize
            result = summarize(json.loads(args.results.read_text()))
            if args.output: write_json(args.output,result)
        elif args.command == 'demo':
            from .demo import run_demo
            result = run_demo(args.output)
        else:
            from .difficulty import scan_catalogs
            result = scan_catalogs(args.sources,args.output)
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
        return 0
    except (ValueError, OSError, KeyError) as exc:
        print(f'{type(exc).__name__}: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
