# RQ1 — AZ vs EN

| Model                       | Rejim    | N  | AZ EM | EN EM | Fərq   | 95% CI       | p      | p (Holm) | Mənalı |
|-----------------------------|----------|----|-------|-------|--------|--------------|--------|----------|--------|
| Qwen/Qwen3-1.7B             | strict   | 96 | 10.4% | 45.8% | 35.4pp | [26.0, 44.8] | 0.0001 | 0.0016   | bəli   |
| Qwen/Qwen3-1.7B             | morph    | 96 | 10.4% | 45.8% | 35.4pp | [26.0, 44.8] | 0.0001 | 0.0016   | bəli   |
| Qwen/Qwen3-1.7B             | lenient  | 96 | 10.4% | 45.8% | 35.4pp | [26.0, 44.8] | 0.0001 | 0.0016   | bəli   |
| Qwen/Qwen3-1.7B             | translit | 96 | 10.4% | 45.8% | 35.4pp | [26.0, 44.8] | 0.0001 | 0.0016   | bəli   |
| Qwen/Qwen3-VL-4B-Instruct   | strict   | 96 | 26.0% | 51.0% | 25.0pp | [13.5, 34.4] | 0.0001 | 0.0016   | bəli   |
| Qwen/Qwen3-VL-4B-Instruct   | morph    | 96 | 28.1% | 51.0% | 22.9pp | [11.5, 32.3] | 0.0001 | 0.0016   | bəli   |
| Qwen/Qwen3-VL-4B-Instruct   | lenient  | 96 | 28.1% | 51.0% | 22.9pp | [11.5, 32.3] | 0.0001 | 0.0016   | bəli   |
| Qwen/Qwen3-VL-4B-Instruct   | translit | 96 | 28.1% | 51.0% | 22.9pp | [11.5, 32.3] | 0.0001 | 0.0016   | bəli   |
| issai/Qolda-AVL-5B          | strict   | 96 | 9.4%  | 50.0% | 40.6pp | [30.2, 51.0] | 0.0001 | 0.0016   | bəli   |
| issai/Qolda-AVL-5B          | morph    | 96 | 9.4%  | 50.0% | 40.6pp | [30.2, 51.0] | 0.0001 | 0.0016   | bəli   |
| issai/Qolda-AVL-5B          | lenient  | 96 | 9.4%  | 50.0% | 40.6pp | [30.2, 51.0] | 0.0001 | 0.0016   | bəli   |
| issai/Qolda-AVL-5B          | translit | 96 | 19.8% | 50.0% | 30.2pp | [20.8, 40.6] | 0.0001 | 0.0016   | bəli   |
| issai/Qolda-AVL-5B (script) | strict   | 96 | 9.4%  | 44.8% | 35.4pp | [26.0, 45.8] | 0.0001 | 0.0016   | bəli   |
| issai/Qolda-AVL-5B (script) | morph    | 96 | 9.4%  | 44.8% | 35.4pp | [26.0, 45.8] | 0.0001 | 0.0016   | bəli   |
| issai/Qolda-AVL-5B (script) | lenient  | 96 | 9.4%  | 44.8% | 35.4pp | [26.0, 45.8] | 0.0001 | 0.0016   | bəli   |
| issai/Qolda-AVL-5B (script) | translit | 96 | 19.8% | 44.8% | 25.0pp | [15.6, 35.4] | 0.0001 | 0.0016   | bəli   |
