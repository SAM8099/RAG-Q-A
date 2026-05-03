from langchain.schema import HumanMessage, SystemMessage
from langchain.docstore.document import Document
from src.modules.config import DIFFICULTY_PROMPTS
from src.utils.singleton import Singleton
from src.services.llm_service import LLMService


class GeneratorService(metaclass=Singleton):
    """
    Singleton service for generating and parsing Q&A questions.
    Uses LLMService internally — no direct LLM initialization here.
    """

    def generate_questions(self, docs: list[Document], difficulty: str, topic: str) -> str:
        """
        Generate current affairs questions from retrieved chunks.
        """
        llm = LLMService().get_llm()
        context = "\n\n".join([doc.page_content for doc in docs])
        difficulty_instruction = DIFFICULTY_PROMPTS.get(difficulty, DIFFICULTY_PROMPTS["Medium"])

        system_prompt = """You are a current affairs quiz expert.
            Generate clear, factual quiz questions strictly based on the provided news context.
            Never add facts not present in the context.
            Format your response exactly as:

            Q1. [Question]
            A1. [Answer]

            Q2. [Question]
            A2. [Answer]

            ...and so on."""

        human_prompt = f"""Topic: {topic or 'General'}
            Difficulty: {difficulty}
            Instruction: {difficulty_instruction}

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
        Parse LLM output into structured list of Q&A dicts.
        """
        pairs = []
        current_q = None
        current_a = None

        for line in raw_output.strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            if line.startswith("Q") and "." in line:
                if current_q and current_a:
                    pairs.append({"question": current_q, "answer": current_a})
                current_q = line.split(".", 1)[-1].strip()
                current_a = None
            elif line.startswith("A") and "." in line:
                current_a = line.split(".", 1)[-1].strip()

        if current_q and current_a:
            pairs.append({"question": current_q, "answer": current_a})

        return pairs