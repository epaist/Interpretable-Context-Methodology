# Embedder Bake-off

Secret Adversary, plain shape: 332 passages, median about 340 bge tokens. Each engine was run in its own process in WSL Ubuntu 24.04 on the PC (i9-14900K, AVX2 and F16C). fastembed 0.9.1 (ONNX Runtime 1.31.1), fasttextembed 1.0.2.

| Engine | Setting | Passages/s | Query ms | Peak MB |
|--------|---------|-----------|----------|---------|
| fastembed | batch 64 | 12.8 | 11.1 | 1,412 |
| fastembed | batch 1 | 14.2 | 4.5 | 285 |
| fasttextembed | default | 5.9 | 11.7 | 249 |

## Do the vectors match?

| Text | Lowest cosine | Median cosine |
|------|--------------|---------------|
| Book passages as written | 0.880 | 0.947 |
| First 16 words, as written | 0.796 | 0.905 |
| First 16 words, curly quotes and dashes turned into ASCII | 1.000 | 1.000 |
| Whole passages, ASCII-folded | 0.9956 | 1.000 |
| He said, “Hello.” (curly quotes) | 0.934 | |
| He said, "Hello." (straight quotes) | 1.000 | |

Cause: fasttextembed's tokenizer handles curly quotes and apostrophes differently from bge's own tokenizer. Every passage in these books contains them. With ASCII folding the vectors nearly match, but the lowest is still 0.9956, under the 0.9998 bar.

## Decision

Stay on fastembed. The switch rule (every cosine at least 0.9998 and lower memory) fails on both counts that matter: vectors differ, and memory drops only 36 MB while throughput falls by more than half on these long passages. The README's speed numbers are for short sentences.

The real memory fix was fastembed's batch size. At batch 64 the PC peaked at 1,346 MB on Windows (1,412 MB in WSL); at batch 1 it peaked at 243 MB on Windows with the same speed. `hces/embed.py` now uses batch 1.

## Windows batch sweep (same 332 passages)

| Batch | Passages/s | Peak MB |
|-------|-----------|---------|
| 1 | 9.7 | 243 |
| 4 | 10.9 | 373 |
| 8 | 11.9 | 459 |
| 16 | 10.4 | 582 |
| 32 | 11.4 | 920 |
| 64 | 10.7 | 1,346 |
