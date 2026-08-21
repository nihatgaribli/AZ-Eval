# LinkedIn post — English (primary)

**Images:** `fig_negative_transfer.png` (first), `fig_script_counts.png` (optional second)

---

Fine-tuning a model on the closest well-resourced relative of your language can make it **worse**, not better.

I built AZ-Eval to check a simple assumption. Azerbaijani has almost no open evaluation data. Kazakh — its closest well-resourced Turkic relative — has plenty. So: does adapting a model to Kazakh carry over?

It does not. Qolda-AVL-5B, fine-tuned on Kazakh, scores **3.1%** on Azerbaijani. Its own base model, Qwen3-VL-4B-Instruct, scores **16.6%**. Holm-corrected p = 0.0024.

The obvious objection is that one model is simply weaker. So I built a control stratum of facts every model should know. There, in **English**, the two are statistically identical: 59.4% versus 59.4%, p = 1.0000. In **Azerbaijani**, on those same items, they are 35.4 points apart.

Same model family. Same parameter count. Same quantization. Indistinguishable in English. Not a capability gap.

The mechanism turned out to be the alphabet. **326 of 356** Azerbaijani answers came back in Cyrillic — several in Kazakh outright. For the base model: 1 of 356. Asking explicitly for the Latin alphabet moved 12 of them. Transliterating the outputs recovers most of the deficit, though not all of it.

The model did not lose the knowledge. It lost the script.

Everything is open — 356 human-verified items stated in parallel Azerbaijani and English, the evaluation harness, and every number behind the claims:

📊 Dataset: huggingface.co/datasets/nihatgaribli/az-eval
💻 Code: github.com/nihatgaribli/AZ-Eval
🔖 DOI: 10.5281/zenodo.22050776

Presenting this at CMAI 2026, Nazarbayev University, Astana, 9–11 September. If you work on Turkic languages or low-resource evaluation, I would genuinely like to hear where you think this breaks.

#NLP #LowResourceNLP #Azerbaijani #TurkicLanguages #LLM #MachineLearning #OpenScience
