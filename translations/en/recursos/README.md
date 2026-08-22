# Resources and Bibliography

Cross-cutting references for the program, commented. Each module also has its own "For Further Reading" section at the end of each theory file.

## Foundational Papers

- **Attention Is All You Need** (Vaswani et al., 2017) — the transformer paper. Read it after the theory of module 1.
- **Language Models are Few-Shot Learners** (Brown et al., 2020, GPT-3) — origin of few-shot prompting.
- **Chain-of-Thought Prompting Elicits Reasoning** (Wei et al., 2022) and **Self-Consistency** (Wang et al., 2022) — foundation of module 2.
- **Retrieval-Augmented Generation for Knowledge-Intensive NLP** (Lewis et al., 2020) — the RAG paper.
- **ReAct: Synergizing Reasoning and Acting** (Yao et al., 2022) — the agent pattern you will implement by hand in module 4.
- **Constitutional AI** (Bai et al., Anthropic, 2022) — alignment, module 4.

## Essential Official Documentation

- Prompting guides from **Anthropic** (docs.claude.com) and **OpenAI** (platform.openai.com/docs) — the best practical guides available; reread them every few months.
- **Building effective agents** (Anthropic) — the reference essay on when to use agents and when not to.
- **Model Context Protocol** — modelcontextprotocol.io (spec and SDKs).
- **LangGraph** — langchain-ai.github.io/langgraph.
- **RAGAS** — docs.ragas.io.
- **Amazon Bedrock** — docs.aws.amazon.com/bedrock.
- **OWASP Top 10 for LLM Applications** — genai.owasp.org (module 5).

## Free Complementary Courses

- **DeepLearning.AI short courses** (deeplearning.ai/short-courses) — 1-2 hour nuggets on prompting, RAG, agents, evals; useful as reinforcement per module.
- **AWS Skill Builder** — official free path for AIF-C01.
- **fast.ai Practical Deep Learning** — if you need to reinforce the DL fundamentals prior to the program.

## Newsletters and Tracking the State of the Art

The model landscape changes every few months: rely on the release notes from OpenAI/Anthropic/Google/Meta, on LMSYS Chatbot Arena for live comparisons, and be skeptical of any static benchmark tables (including those in this repo if there ever were any).

## How to Study This Program

1. **Theory → lab → exercises**, in that order, for each topic. Do not move to the next topic without having executed and broken the lab (change parameters, provoke errors, measure).
2. **Your own notebook** (`notas/` is in .gitignore if you want to create it): explaining a concept in your own words is the best test of comprehension.
3. **Commits per topic**: treat your progress as a real project; the git history is your study log.
4. **Certification mock exams, cold**: take them with a timer and without looking at notes, and then review the failed areas with the domain-specific guides.
