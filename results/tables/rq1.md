# RQ1 — AZ vs EN

| Model                       | Rejim    | N   | AZ EM | EN EM | Fərq   | 95% CI       | p      | p (Holm) | Mənalı |
|-----------------------------|----------|-----|-------|-------|--------|--------------|--------|----------|--------|
| Qwen/Qwen3-1.7B             | strict   | 356 | 5.9%  | 23.6% | 17.7pp | [13.8, 21.6] | 0.0001 | 0.0020   | bəli   |
| Qwen/Qwen3-1.7B             | morph    | 356 | 6.5%  | 23.6% | 17.1pp | [13.2, 21.1] | 0.0001 | 0.0020   | bəli   |
| Qwen/Qwen3-1.7B             | lenient  | 356 | 7.0%  | 23.9% | 16.9pp | [12.9, 20.8] | 0.0001 | 0.0020   | bəli   |
| Qwen/Qwen3-1.7B             | translit | 356 | 7.0%  | 23.9% | 16.9pp | [12.9, 20.8] | 0.0001 | 0.0020   | bəli   |
| Qwen/Qwen3-VL-4B-Instruct   | strict   | 356 | 16.6% | 30.6% | 14.0pp | [9.5, 18.8]  | 0.0001 | 0.0020   | bəli   |
| Qwen/Qwen3-VL-4B-Instruct   | morph    | 356 | 17.7% | 30.6% | 12.9pp | [8.4, 17.4]  | 0.0001 | 0.0020   | bəli   |
| Qwen/Qwen3-VL-4B-Instruct   | lenient  | 356 | 18.0% | 30.6% | 12.6pp | [8.1, 17.1]  | 0.0001 | 0.0020   | bəli   |
| Qwen/Qwen3-VL-4B-Instruct   | translit | 356 | 18.0% | 30.6% | 12.6pp | [8.1, 17.1]  | 0.0001 | 0.0020   | bəli   |
| Qwen/Qwen3-VL-4B-Thinking   | strict   | 356 | 12.6% | 29.5% | 16.9pp | [12.9, 21.1] | 0.0001 | 0.0020   | bəli   |
| Qwen/Qwen3-VL-4B-Thinking   | morph    | 356 | 13.2% | 29.5% | 16.3pp | [12.4, 20.5] | 0.0001 | 0.0020   | bəli   |
| Qwen/Qwen3-VL-4B-Thinking   | lenient  | 356 | 13.5% | 29.5% | 16.0pp | [12.1, 20.2] | 0.0001 | 0.0020   | bəli   |
| Qwen/Qwen3-VL-4B-Thinking   | translit | 356 | 13.5% | 29.5% | 16.0pp | [12.1, 20.2] | 0.0001 | 0.0020   | bəli   |
| issai/Qolda-AVL-5B          | strict   | 356 | 3.1%  | 29.5% | 26.4pp | [21.9, 31.2] | 0.0001 | 0.0020   | bəli   |
| issai/Qolda-AVL-5B          | morph    | 356 | 3.1%  | 29.5% | 26.4pp | [21.9, 31.2] | 0.0001 | 0.0020   | bəli   |
| issai/Qolda-AVL-5B          | lenient  | 356 | 3.1%  | 29.5% | 26.4pp | [21.9, 31.2] | 0.0001 | 0.0020   | bəli   |
| issai/Qolda-AVL-5B          | translit | 356 | 12.1% | 29.5% | 17.4pp | [13.2, 22.2] | 0.0001 | 0.0020   | bəli   |
| issai/Qolda-AVL-5B (script) | strict   | 356 | 3.4%  | 28.7% | 25.3pp | [20.8, 30.1] | 0.0001 | 0.0020   | bəli   |
| issai/Qolda-AVL-5B (script) | morph    | 356 | 3.9%  | 28.7% | 24.7pp | [20.2, 29.2] | 0.0001 | 0.0020   | bəli   |
| issai/Qolda-AVL-5B (script) | lenient  | 356 | 3.9%  | 28.7% | 24.7pp | [20.2, 29.2] | 0.0001 | 0.0020   | bəli   |
| issai/Qolda-AVL-5B (script) | translit | 356 | 12.1% | 28.7% | 16.6pp | [12.6, 21.1] | 0.0001 | 0.0020   | bəli   |
