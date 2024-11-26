# TURSpider: A Turkish Text-to-SQL Dataset

TURSpider is a novel Turkish Text-to-SQL dataset that includes complex queries, akin to those in the original Spider dataset. TURSpider dataset comprises two main subsets: a dev set and a training set, aligned with the structure and scale of the popular Spider dataset. The dev set contains 1034 data rows with 1023 unique questions and 584 distinct SQL queries. In the training set, there are 8659 data rows, 8506 unique questions, and corresponding SQL queries.

## Results

If you submit papers on TURSpider, please let us know so we can merge your results into the results table.

### Execution accuracy (EX) of LLMs on the TURSpider development set

| Approach | Model | Execution Accuracy (EX) |
| :---: | :---:        | :---:         |
| Inference-only | GPT-3.5 Turbo | 55.99 |
| Inference-only | GPT-4 | 57.25 |
| Fine-tuning | TrendyolSQL | 25.04 |
| Fine-tuning | SambaLingoSQL | 30.65 |
| Fine-tuning | TurkcellSQL | 58.22 |

### Citation
If you use TURSpider, please cite the following work:

<a href="https://ieeexplore.ieee.org/document/10753591">Paper link</a>

```
@ARTICLE{10753591,
  author={Kanburoglu, Ali Bugra and Boray Tek, Faik},
  journal={IEEE Access}, 
  title={TURSpider: A Turkish Text-to-SQL Dataset and LLM-Based Study}, 
  year={2024},
  volume={12},
  number={},
  pages={169379-169387},
  keywords={Training;Structured Query Language;Accuracy;Error analysis;Large language models;Benchmark testing;Cognition;Encoding;Text-to-SQL;LLM;large language models;Turkish;dataset;TURSpider},
  doi={10.1109/ACCESS.2024.3498841}}
```

You can also check TUR2SQL dataset for Turkish Text-to-SQL studies:

<a href="https://github.com/alibugra/TUR2SQL">TUR2SQL</a>
