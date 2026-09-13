def generate_mcqs(rag_engine, llm_router, is_online: bool, num_questions: int = 3) -> str:
    context, _ = rag_engine.retrieve_context("key concepts overview main topics", k=5)
    prompt = f"Generate {num_questions} multiple-choice questions (with 4 options and correct answers clearly labeled at the bottom) based on this content:\n\n{context}"
    response, _ = llm_router.query(prompt, "", is_online)
    return response

def summarize_knowledge_base(rag_engine, llm_router, is_online: bool) -> str:
    context, _ = rag_engine.retrieve_context("summary introduction core topics overall concept", k=5)
    prompt = f"Provide a clean, structured, bulleted summary of the core academic concepts found in this context:\n\n{context}"
    response, _ = llm_router.query(prompt, "", is_online)
    return response

def solve_math_problem(problem_statement: str, llm_router, is_online: bool) -> str:
    prompt = f"Solve the following calculation or academic problem step-by-step. Show all formulas, step calculations, and final answers explicitly:\n\n{problem_statement}"
    response, _ = llm_router.query(prompt, "", is_online)
    return response
