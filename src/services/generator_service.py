from langchain.schema import HumanMessage, SystemMessage
from src.modules.config import DIFFICULTY_PROMPTS
from src.utils.singleton import Singleton
from src.services.llm_service import LLMService


class GeneratorService(metaclass=Singleton):
    """
    Singleton service for generating and parsing Q&A questions.
    """

    def generate_questions(
        self,
        chunks: list[str],
        difficulty: str,
        topic: str,
        sources: list[str] | None = None,
    ) -> str:
        """
        Generate questions from retrieved chunks.
        Sources injected into prompt so LLM can attribute each answer.
        """
        llm = LLMService().get_llm()
        context = "\n\n".join(chunks)
        difficulty_instruction = DIFFICULTY_PROMPTS.get(difficulty, DIFFICULTY_PROMPTS["Medium"])
        source_line = f"Available sources: {', '.join(sources)}" if sources else ""

        system_prompt = """You are a current affairs quiz expert.
Generate clear, factual quiz questions strictly based on the provided news context.
Never add facts not present in the context.
Format your response exactly as:

Q1. [Question]
A1. [Answer]
Source: [Source name from available sources]

Q2. [Question]
A2. [Answer]
Source: [Source name from available sources]

...and so on."""

        human_prompt = f"""Topic: {topic or 'General'}
Difficulty: {difficulty}
Instruction: {difficulty_instruction}
{source_line}

News Context:
{context}

Generate the questions now."""

        try:
            response = llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt),
            ])
            return response.content
        except Exception as e:
            raise RuntimeError(f"LLM generation failed: {e}")

    def parse_questions(self, raw_output: str) -> list[dict]:
        """
        Parse LLM output into structured Q&A dicts with source attribution.
        """
        pairs = []
        current_q = None
        current_a = None
        current_source = None

        for line in raw_output.strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            if line.startswith("Q") and "." in line:
                if current_q and current_a:
                    pairs.append({
                        "question": current_q,
                        "answer": current_a,
                        "source": current_source or "Unknown",
                    })
                current_q = line.split(".", 1)[-1].strip()
                current_a = None
                current_source = None
            elif line.startswith("A") and "." in line:
                current_a = line.split(".", 1)[-1].strip()
            elif line.startswith("Source:"):
                current_source = line.split(":", 1)[-1].strip()

        if current_q and current_a:
            pairs.append({
                "question": current_q,
                "answer": current_a,
                "source": current_source or "Unknown",
            })

        return pairs