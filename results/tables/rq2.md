# RQ2 — modellərarası müqayisə (AZ)

| Model A                     | Model B                     | Rejim    | N  | A EM  | B EM  | Fərq    | p      | p (Holm) | Mənalı |
|-----------------------------|-----------------------------|----------|----|-------|-------|---------|--------|----------|--------|
| Qwen/Qwen3-1.7B             | Qwen/Qwen3-VL-4B-Instruct   | strict   | 96 | 10.4% | 26.0% | -15.6pp | 0.0003 | 0.0045   | bəli   |
| Qwen/Qwen3-1.7B             | Qwen/Qwen3-VL-4B-Instruct   | morph    | 96 | 10.4% | 28.1% | -17.7pp | 0.0001 | 0.0024   | bəli   |
| Qwen/Qwen3-1.7B             | Qwen/Qwen3-VL-4B-Instruct   | lenient  | 96 | 10.4% | 28.1% | -17.7pp | 0.0001 | 0.0024   | bəli   |
| Qwen/Qwen3-1.7B             | Qwen/Qwen3-VL-4B-Instruct   | translit | 96 | 10.4% | 28.1% | -17.7pp | 0.0001 | 0.0024   | bəli   |
| Qwen/Qwen3-1.7B             | issai/Qolda-AVL-5B (script) | strict   | 96 | 10.4% | 9.4%  | 1.0pp   | 1.0000 | 1.0000   | xeyr   |
| Qwen/Qwen3-1.7B             | issai/Qolda-AVL-5B (script) | morph    | 96 | 10.4% | 9.4%  | 1.0pp   | 1.0000 | 1.0000   | xeyr   |
| Qwen/Qwen3-1.7B             | issai/Qolda-AVL-5B (script) | lenient  | 96 | 10.4% | 9.4%  | 1.0pp   | 1.0000 | 1.0000   | xeyr   |
| Qwen/Qwen3-1.7B             | issai/Qolda-AVL-5B (script) | translit | 96 | 10.4% | 19.8% | -9.4pp  | 0.0359 | 0.5025   | xeyr   |
| Qwen/Qwen3-1.7B             | issai/Qolda-AVL-5B          | strict   | 96 | 10.4% | 9.4%  | 1.0pp   | 1.0000 | 1.0000   | xeyr   |
| Qwen/Qwen3-1.7B             | issai/Qolda-AVL-5B          | morph    | 96 | 10.4% | 9.4%  | 1.0pp   | 1.0000 | 1.0000   | xeyr   |
| Qwen/Qwen3-1.7B             | issai/Qolda-AVL-5B          | lenient  | 96 | 10.4% | 9.4%  | 1.0pp   | 1.0000 | 1.0000   | xeyr   |
| Qwen/Qwen3-1.7B             | issai/Qolda-AVL-5B          | translit | 96 | 10.4% | 19.8% | -9.4pp  | 0.0463 | 0.6018   | xeyr   |
| Qwen/Qwen3-VL-4B-Instruct   | issai/Qolda-AVL-5B (script) | strict   | 96 | 26.0% | 9.4%  | 16.7pp  | 0.0002 | 0.0042   | bəli   |
| Qwen/Qwen3-VL-4B-Instruct   | issai/Qolda-AVL-5B (script) | morph    | 96 | 28.1% | 9.4%  | 18.8pp  | 0.0002 | 0.0042   | bəli   |
| Qwen/Qwen3-VL-4B-Instruct   | issai/Qolda-AVL-5B (script) | lenient  | 96 | 28.1% | 9.4%  | 18.8pp  | 0.0002 | 0.0042   | bəli   |
| Qwen/Qwen3-VL-4B-Instruct   | issai/Qolda-AVL-5B (script) | translit | 96 | 28.1% | 19.8% | 8.3pp   | 0.1010 | 1.0000   | xeyr   |
| Qwen/Qwen3-VL-4B-Instruct   | issai/Qolda-AVL-5B          | strict   | 96 | 26.0% | 9.4%  | 16.7pp  | 0.0002 | 0.0042   | bəli   |
| Qwen/Qwen3-VL-4B-Instruct   | issai/Qolda-AVL-5B          | morph    | 96 | 28.1% | 9.4%  | 18.8pp  | 0.0002 | 0.0042   | bəli   |
| Qwen/Qwen3-VL-4B-Instruct   | issai/Qolda-AVL-5B          | lenient  | 96 | 28.1% | 9.4%  | 18.8pp  | 0.0002 | 0.0042   | bəli   |
| Qwen/Qwen3-VL-4B-Instruct   | issai/Qolda-AVL-5B          | translit | 96 | 28.1% | 19.8% | 8.3pp   | 0.1201 | 1.0000   | xeyr   |
| issai/Qolda-AVL-5B (script) | issai/Qolda-AVL-5B          | strict   | 96 | 9.4%  | 9.4%  | 0.0pp   | 1.0000 | 1.0000   | xeyr   |
| issai/Qolda-AVL-5B (script) | issai/Qolda-AVL-5B          | morph    | 96 | 9.4%  | 9.4%  | 0.0pp   | 1.0000 | 1.0000   | xeyr   |
| issai/Qolda-AVL-5B (script) | issai/Qolda-AVL-5B          | lenient  | 96 | 9.4%  | 9.4%  | 0.0pp   | 1.0000 | 1.0000   | xeyr   |
| issai/Qolda-AVL-5B (script) | issai/Qolda-AVL-5B          | translit | 96 | 19.8% | 19.8% | 0.0pp   | 1.0000 | 1.0000   | xeyr   |
