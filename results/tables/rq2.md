# RQ2 — modellərarası müqayisə (AZ)

| Model A                     | Model B                     | Rejim    | N   | A EM  | B EM  | Fərq    | p      | p (Holm) | Mənalı |
|-----------------------------|-----------------------------|----------|-----|-------|-------|---------|--------|----------|--------|
| Qwen/Qwen3-1.7B             | Qwen/Qwen3-VL-4B-Instruct   | strict   | 356 | 5.9%  | 16.6% | -10.7pp | 0.0001 | 0.0040   | bəli   |
| Qwen/Qwen3-1.7B             | Qwen/Qwen3-VL-4B-Instruct   | morph    | 356 | 6.5%  | 17.7% | -11.2pp | 0.0001 | 0.0040   | bəli   |
| Qwen/Qwen3-1.7B             | Qwen/Qwen3-VL-4B-Instruct   | lenient  | 356 | 7.0%  | 18.0% | -11.0pp | 0.0001 | 0.0040   | bəli   |
| Qwen/Qwen3-1.7B             | Qwen/Qwen3-VL-4B-Instruct   | translit | 356 | 7.0%  | 18.0% | -11.0pp | 0.0001 | 0.0040   | bəli   |
| Qwen/Qwen3-1.7B             | Qwen/Qwen3-VL-4B-Thinking   | strict   | 356 | 5.9%  | 12.6% | -6.7pp  | 0.0001 | 0.0040   | bəli   |
| Qwen/Qwen3-1.7B             | Qwen/Qwen3-VL-4B-Thinking   | morph    | 356 | 6.5%  | 13.2% | -6.7pp  | 0.0001 | 0.0040   | bəli   |
| Qwen/Qwen3-1.7B             | Qwen/Qwen3-VL-4B-Thinking   | lenient  | 356 | 7.0%  | 13.5% | -6.5pp  | 0.0002 | 0.0044   | bəli   |
| Qwen/Qwen3-1.7B             | Qwen/Qwen3-VL-4B-Thinking   | translit | 356 | 7.0%  | 13.5% | -6.5pp  | 0.0002 | 0.0044   | bəli   |
| Qwen/Qwen3-1.7B             | issai/Qolda-AVL-5B (script) | strict   | 356 | 5.9%  | 3.4%  | 2.5pp   | 0.1248 | 0.9983   | xeyr   |
| Qwen/Qwen3-1.7B             | issai/Qolda-AVL-5B (script) | morph    | 356 | 6.5%  | 3.9%  | 2.5pp   | 0.1370 | 0.9983   | xeyr   |
| Qwen/Qwen3-1.7B             | issai/Qolda-AVL-5B (script) | lenient  | 356 | 7.0%  | 3.9%  | 3.1pp   | 0.0712 | 0.7119   | xeyr   |
| Qwen/Qwen3-1.7B             | issai/Qolda-AVL-5B (script) | translit | 356 | 7.0%  | 12.1% | -5.1pp  | 0.0065 | 0.0954   | xeyr   |
| Qwen/Qwen3-1.7B             | issai/Qolda-AVL-5B          | strict   | 356 | 5.9%  | 3.1%  | 2.8pp   | 0.0861 | 0.7748   | xeyr   |
| Qwen/Qwen3-1.7B             | issai/Qolda-AVL-5B          | morph    | 356 | 6.5%  | 3.1%  | 3.4pp   | 0.0425 | 0.4675   | xeyr   |
| Qwen/Qwen3-1.7B             | issai/Qolda-AVL-5B          | lenient  | 356 | 7.0%  | 3.1%  | 3.9pp   | 0.0190 | 0.2280   | xeyr   |
| Qwen/Qwen3-1.7B             | issai/Qolda-AVL-5B          | translit | 356 | 7.0%  | 12.1% | -5.1pp  | 0.0063 | 0.0954   | xeyr   |
| Qwen/Qwen3-VL-4B-Instruct   | Qwen/Qwen3-VL-4B-Thinking   | strict   | 356 | 16.6% | 12.6% | 3.9pp   | 0.0124 | 0.1612   | xeyr   |
| Qwen/Qwen3-VL-4B-Instruct   | Qwen/Qwen3-VL-4B-Thinking   | morph    | 356 | 17.7% | 13.2% | 4.5pp   | 0.0053 | 0.0954   | xeyr   |
| Qwen/Qwen3-VL-4B-Instruct   | Qwen/Qwen3-VL-4B-Thinking   | lenient  | 356 | 18.0% | 13.5% | 4.5pp   | 0.0053 | 0.0954   | xeyr   |
| Qwen/Qwen3-VL-4B-Instruct   | Qwen/Qwen3-VL-4B-Thinking   | translit | 356 | 18.0% | 13.5% | 4.5pp   | 0.0053 | 0.0954   | xeyr   |
| Qwen/Qwen3-VL-4B-Instruct   | issai/Qolda-AVL-5B (script) | strict   | 356 | 16.6% | 3.4%  | 13.2pp  | 0.0001 | 0.0040   | bəli   |
| Qwen/Qwen3-VL-4B-Instruct   | issai/Qolda-AVL-5B (script) | morph    | 356 | 17.7% | 3.9%  | 13.8pp  | 0.0001 | 0.0040   | bəli   |
| Qwen/Qwen3-VL-4B-Instruct   | issai/Qolda-AVL-5B (script) | lenient  | 356 | 18.0% | 3.9%  | 14.0pp  | 0.0001 | 0.0040   | bəli   |
| Qwen/Qwen3-VL-4B-Instruct   | issai/Qolda-AVL-5B (script) | translit | 356 | 18.0% | 12.1% | 5.9pp   | 0.0033 | 0.0627   | xeyr   |
| Qwen/Qwen3-VL-4B-Instruct   | issai/Qolda-AVL-5B          | strict   | 356 | 16.6% | 3.1%  | 13.5pp  | 0.0001 | 0.0040   | bəli   |
| Qwen/Qwen3-VL-4B-Instruct   | issai/Qolda-AVL-5B          | morph    | 356 | 17.7% | 3.1%  | 14.6pp  | 0.0001 | 0.0040   | bəli   |
| Qwen/Qwen3-VL-4B-Instruct   | issai/Qolda-AVL-5B          | lenient  | 356 | 18.0% | 3.1%  | 14.9pp  | 0.0001 | 0.0040   | bəli   |
| Qwen/Qwen3-VL-4B-Instruct   | issai/Qolda-AVL-5B          | translit | 356 | 18.0% | 12.1% | 5.9pp   | 0.0026 | 0.0520   | xeyr   |
| Qwen/Qwen3-VL-4B-Thinking   | issai/Qolda-AVL-5B (script) | strict   | 356 | 12.6% | 3.4%  | 9.3pp   | 0.0001 | 0.0040   | bəli   |
| Qwen/Qwen3-VL-4B-Thinking   | issai/Qolda-AVL-5B (script) | morph    | 356 | 13.2% | 3.9%  | 9.3pp   | 0.0001 | 0.0040   | bəli   |
| Qwen/Qwen3-VL-4B-Thinking   | issai/Qolda-AVL-5B (script) | lenient  | 356 | 13.5% | 3.9%  | 9.6pp   | 0.0001 | 0.0040   | bəli   |
| Qwen/Qwen3-VL-4B-Thinking   | issai/Qolda-AVL-5B (script) | translit | 356 | 13.5% | 12.1% | 1.4pp   | 0.5108 | 1.0000   | xeyr   |
| Qwen/Qwen3-VL-4B-Thinking   | issai/Qolda-AVL-5B          | strict   | 356 | 12.6% | 3.1%  | 9.6pp   | 0.0001 | 0.0040   | bəli   |
| Qwen/Qwen3-VL-4B-Thinking   | issai/Qolda-AVL-5B          | morph    | 356 | 13.2% | 3.1%  | 10.1pp  | 0.0001 | 0.0040   | bəli   |
| Qwen/Qwen3-VL-4B-Thinking   | issai/Qolda-AVL-5B          | lenient  | 356 | 13.5% | 3.1%  | 10.4pp  | 0.0001 | 0.0040   | bəli   |
| Qwen/Qwen3-VL-4B-Thinking   | issai/Qolda-AVL-5B          | translit | 356 | 13.5% | 12.1% | 1.4pp   | 0.4993 | 1.0000   | xeyr   |
| issai/Qolda-AVL-5B (script) | issai/Qolda-AVL-5B          | strict   | 356 | 3.4%  | 3.1%  | 0.3pp   | 1.0000 | 1.0000   | xeyr   |
| issai/Qolda-AVL-5B (script) | issai/Qolda-AVL-5B          | morph    | 356 | 3.9%  | 3.1%  | 0.8pp   | 0.2338 | 1.0000   | xeyr   |
| issai/Qolda-AVL-5B (script) | issai/Qolda-AVL-5B          | lenient  | 356 | 3.9%  | 3.1%  | 0.8pp   | 0.2338 | 1.0000   | xeyr   |
| issai/Qolda-AVL-5B (script) | issai/Qolda-AVL-5B          | translit | 356 | 12.1% | 12.1% | 0.0pp   | 1.0000 | 1.0000   | xeyr   |
