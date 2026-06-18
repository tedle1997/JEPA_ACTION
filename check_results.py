import json

with open(r'E:\Saarland\2026\HLCV\Project\jepa_action\weekend1_pipeline_executed.ipynb', 'r') as f:
    nb = json.load(f)

keywords = ['SUMMARY', 'Final val', 'CosSim', 'Horizon', 'Ablation', 'Delta',
            'complete', 'final_val', 'checkpoint', 'Training complete']

for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code' and cell.get('outputs'):
        for out in cell['outputs']:
            if out.get('output_type') == 'stream' and out.get('name') == 'stdout':
                text = ''.join(out.get('text', []))
                if any(kw in text for kw in keywords):
                    print(f'=== Cell {i} (exec_count={cell.get("execution_count")}) ===')
                    print(text[:2000])
                    print()
