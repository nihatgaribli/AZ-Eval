# RQ2 nəzarət qatında (world + science) — ən təmiz ölçü

| Dil | Model A                     | Model B                     | Rejim    | N  | A EM  | B EM  | Fərq    | p      | p (Holm) | Mənalı |
|-----|-----------------------------|-----------------------------|----------|----|-------|-------|---------|--------|----------|--------|
| EN  | Qwen/Qwen3-1.7B             | Qwen/Qwen3-VL-4B-Instruct   | strict   | 96 | 52.1% | 59.4% | -7.3pp  | 0.2435 | 1.0000   | xeyr   |
| EN  | Qwen/Qwen3-1.7B             | Qwen/Qwen3-VL-4B-Thinking   | strict   | 96 | 52.1% | 62.5% | -10.4pp | 0.0538 | 1.0000   | xeyr   |
| EN  | Qwen/Qwen3-1.7B             | issai/Qolda-AVL-5B (script) | strict   | 96 | 52.1% | 58.3% | -6.2pp  | 0.2606 | 1.0000   | xeyr   |
| EN  | Qwen/Qwen3-1.7B             | issai/Qolda-AVL-5B          | strict   | 96 | 52.1% | 59.4% | -7.3pp  | 0.1910 | 1.0000   | xeyr   |
| EN  | Qwen/Qwen3-VL-4B-Instruct   | Qwen/Qwen3-VL-4B-Thinking   | strict   | 96 | 59.4% | 62.5% | -3.1pp  | 0.4516 | 1.0000   | xeyr   |
| EN  | Qwen/Qwen3-VL-4B-Instruct   | issai/Qolda-AVL-5B (script) | strict   | 96 | 59.4% | 58.3% | 1.0pp   | 1.0000 | 1.0000   | xeyr   |
| EN  | Qwen/Qwen3-VL-4B-Instruct   | issai/Qolda-AVL-5B          | strict   | 96 | 59.4% | 59.4% | 0.0pp   | 1.0000 | 1.0000   | xeyr   |
| EN  | Qwen/Qwen3-VL-4B-Thinking   | issai/Qolda-AVL-5B (script) | strict   | 96 | 62.5% | 58.3% | 4.2pp   | 0.4546 | 1.0000   | xeyr   |
| EN  | Qwen/Qwen3-VL-4B-Thinking   | issai/Qolda-AVL-5B          | strict   | 96 | 62.5% | 59.4% | 3.1pp   | 0.5892 | 1.0000   | xeyr   |
| EN  | issai/Qolda-AVL-5B (script) | issai/Qolda-AVL-5B          | strict   | 96 | 58.3% | 59.4% | -1.0pp  | 1.0000 | 1.0000   | xeyr   |
| AZ  | Qwen/Qwen3-1.7B             | Qwen/Qwen3-VL-4B-Instruct   | strict   | 96 | 17.7% | 45.8% | -28.1pp | 0.0001 | 0.0050   | bəli   |
| AZ  | Qwen/Qwen3-1.7B             | Qwen/Qwen3-VL-4B-Instruct   | morph    | 96 | 18.8% | 45.8% | -27.1pp | 0.0001 | 0.0050   | bəli   |
| AZ  | Qwen/Qwen3-1.7B             | Qwen/Qwen3-VL-4B-Instruct   | lenient  | 96 | 19.8% | 46.9% | -27.1pp | 0.0001 | 0.0050   | bəli   |
| AZ  | Qwen/Qwen3-1.7B             | Qwen/Qwen3-VL-4B-Instruct   | translit | 96 | 19.8% | 46.9% | -27.1pp | 0.0001 | 0.0050   | bəli   |
| AZ  | Qwen/Qwen3-1.7B             | Qwen/Qwen3-VL-4B-Thinking   | strict   | 96 | 17.7% | 37.5% | -19.8pp | 0.0003 | 0.0102   | bəli   |
| AZ  | Qwen/Qwen3-1.7B             | Qwen/Qwen3-VL-4B-Thinking   | morph    | 96 | 18.8% | 37.5% | -18.8pp | 0.0005 | 0.0155   | bəli   |
| AZ  | Qwen/Qwen3-1.7B             | Qwen/Qwen3-VL-4B-Thinking   | lenient  | 96 | 19.8% | 38.5% | -18.8pp | 0.0004 | 0.0132   | bəli   |
| AZ  | Qwen/Qwen3-1.7B             | Qwen/Qwen3-VL-4B-Thinking   | translit | 96 | 19.8% | 38.5% | -18.8pp | 0.0004 | 0.0132   | bəli   |
| AZ  | Qwen/Qwen3-1.7B             | issai/Qolda-AVL-5B (script) | strict   | 96 | 17.7% | 11.5% | 6.2pp   | 0.2856 | 1.0000   | xeyr   |
| AZ  | Qwen/Qwen3-1.7B             | issai/Qolda-AVL-5B (script) | morph    | 96 | 18.8% | 11.5% | 7.3pp   | 0.2103 | 1.0000   | xeyr   |
| AZ  | Qwen/Qwen3-1.7B             | issai/Qolda-AVL-5B (script) | lenient  | 96 | 19.8% | 11.5% | 8.3pp   | 0.1495 | 1.0000   | xeyr   |
| AZ  | Qwen/Qwen3-1.7B             | issai/Qolda-AVL-5B (script) | translit | 96 | 19.8% | 32.3% | -12.5pp | 0.0290 | 0.7829   | xeyr   |
| AZ  | Qwen/Qwen3-1.7B             | issai/Qolda-AVL-5B          | strict   | 96 | 17.7% | 10.4% | 7.3pp   | 0.2122 | 1.0000   | xeyr   |
| AZ  | Qwen/Qwen3-1.7B             | issai/Qolda-AVL-5B          | morph    | 96 | 18.8% | 10.4% | 8.3pp   | 0.1561 | 1.0000   | xeyr   |
| AZ  | Qwen/Qwen3-1.7B             | issai/Qolda-AVL-5B          | lenient  | 96 | 19.8% | 10.4% | 9.4pp   | 0.1091 | 1.0000   | xeyr   |
| AZ  | Qwen/Qwen3-1.7B             | issai/Qolda-AVL-5B          | translit | 96 | 19.8% | 33.3% | -13.5pp | 0.0179 | 0.5011   | xeyr   |
| AZ  | Qwen/Qwen3-VL-4B-Instruct   | Qwen/Qwen3-VL-4B-Thinking   | strict   | 96 | 45.8% | 37.5% | 8.3pp   | 0.0918 | 1.0000   | xeyr   |
| AZ  | Qwen/Qwen3-VL-4B-Instruct   | Qwen/Qwen3-VL-4B-Thinking   | morph    | 96 | 45.8% | 37.5% | 8.3pp   | 0.0918 | 1.0000   | xeyr   |
| AZ  | Qwen/Qwen3-VL-4B-Instruct   | Qwen/Qwen3-VL-4B-Thinking   | lenient  | 96 | 46.9% | 38.5% | 8.3pp   | 0.0918 | 1.0000   | xeyr   |
| AZ  | Qwen/Qwen3-VL-4B-Instruct   | Qwen/Qwen3-VL-4B-Thinking   | translit | 96 | 46.9% | 38.5% | 8.3pp   | 0.0918 | 1.0000   | xeyr   |
| AZ  | Qwen/Qwen3-VL-4B-Instruct   | issai/Qolda-AVL-5B (script) | strict   | 96 | 45.8% | 11.5% | 34.4pp  | 0.0001 | 0.0050   | bəli   |
| AZ  | Qwen/Qwen3-VL-4B-Instruct   | issai/Qolda-AVL-5B (script) | morph    | 96 | 45.8% | 11.5% | 34.4pp  | 0.0001 | 0.0050   | bəli   |
| AZ  | Qwen/Qwen3-VL-4B-Instruct   | issai/Qolda-AVL-5B (script) | lenient  | 96 | 46.9% | 11.5% | 35.4pp  | 0.0001 | 0.0050   | bəli   |
| AZ  | Qwen/Qwen3-VL-4B-Instruct   | issai/Qolda-AVL-5B (script) | translit | 96 | 46.9% | 32.3% | 14.6pp  | 0.0096 | 0.2880   | xeyr   |
| AZ  | Qwen/Qwen3-VL-4B-Instruct   | issai/Qolda-AVL-5B          | strict   | 96 | 45.8% | 10.4% | 35.4pp  | 0.0001 | 0.0050   | bəli   |
| AZ  | Qwen/Qwen3-VL-4B-Instruct   | issai/Qolda-AVL-5B          | morph    | 96 | 45.8% | 10.4% | 35.4pp  | 0.0001 | 0.0050   | bəli   |
| AZ  | Qwen/Qwen3-VL-4B-Instruct   | issai/Qolda-AVL-5B          | lenient  | 96 | 46.9% | 10.4% | 36.5pp  | 0.0001 | 0.0050   | bəli   |
| AZ  | Qwen/Qwen3-VL-4B-Instruct   | issai/Qolda-AVL-5B          | translit | 96 | 46.9% | 33.3% | 13.5pp  | 0.0149 | 0.4321   | xeyr   |
| AZ  | Qwen/Qwen3-VL-4B-Thinking   | issai/Qolda-AVL-5B (script) | strict   | 96 | 37.5% | 11.5% | 26.0pp  | 0.0001 | 0.0050   | bəli   |
| AZ  | Qwen/Qwen3-VL-4B-Thinking   | issai/Qolda-AVL-5B (script) | morph    | 96 | 37.5% | 11.5% | 26.0pp  | 0.0001 | 0.0050   | bəli   |
| AZ  | Qwen/Qwen3-VL-4B-Thinking   | issai/Qolda-AVL-5B (script) | lenient  | 96 | 38.5% | 11.5% | 27.1pp  | 0.0001 | 0.0050   | bəli   |
| AZ  | Qwen/Qwen3-VL-4B-Thinking   | issai/Qolda-AVL-5B (script) | translit | 96 | 38.5% | 32.3% | 6.2pp   | 0.3015 | 1.0000   | xeyr   |
| AZ  | Qwen/Qwen3-VL-4B-Thinking   | issai/Qolda-AVL-5B          | strict   | 96 | 37.5% | 10.4% | 27.1pp  | 0.0001 | 0.0050   | bəli   |
| AZ  | Qwen/Qwen3-VL-4B-Thinking   | issai/Qolda-AVL-5B          | morph    | 96 | 37.5% | 10.4% | 27.1pp  | 0.0001 | 0.0050   | bəli   |
| AZ  | Qwen/Qwen3-VL-4B-Thinking   | issai/Qolda-AVL-5B          | lenient  | 96 | 38.5% | 10.4% | 28.1pp  | 0.0001 | 0.0050   | bəli   |
| AZ  | Qwen/Qwen3-VL-4B-Thinking   | issai/Qolda-AVL-5B          | translit | 96 | 38.5% | 33.3% | 5.2pp   | 0.3795 | 1.0000   | xeyr   |
| AZ  | issai/Qolda-AVL-5B (script) | issai/Qolda-AVL-5B          | strict   | 96 | 11.5% | 10.4% | 1.0pp   | 1.0000 | 1.0000   | xeyr   |
| AZ  | issai/Qolda-AVL-5B (script) | issai/Qolda-AVL-5B          | morph    | 96 | 11.5% | 10.4% | 1.0pp   | 1.0000 | 1.0000   | xeyr   |
| AZ  | issai/Qolda-AVL-5B (script) | issai/Qolda-AVL-5B          | lenient  | 96 | 11.5% | 10.4% | 1.0pp   | 1.0000 | 1.0000   | xeyr   |
| AZ  | issai/Qolda-AVL-5B (script) | issai/Qolda-AVL-5B          | translit | 96 | 32.3% | 33.3% | -1.0pp  | 1.0000 | 1.0000   | xeyr   |
