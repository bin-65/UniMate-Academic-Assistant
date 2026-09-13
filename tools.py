# tools.py

def generate_mcqs(rag_engine, llm_router, is_online: bool, num_questions: int = 3):
    context, sources = rag_engine.retrieve_context("Generate key academic practice concepts and formulas.")
    if not context:
        return "⚠️ Knowledge base is empty. Please upload and index PDF documents first."
    
    prompt = f"Based on the following context, generate {num_questions} multiple-choice questions (MCQs) with 4 options each and indicate the correct answer at the end:\n\n{context}"
    response, engine = llm_router.query(prompt, context, is_online)
    return response

def summarize_knowledge_base(rag_engine, llm_router, is_online: bool):
    context, sources = rag_engine.retrieve_context("Main concepts, definitions, rules, and core topics.")
    if not context:
        return "⚠️ Knowledge base is empty. Please upload and index PDF documents first."
    
    prompt = "Provide a comprehensive, highly structured academic summary of the provided text using bullet points and clear sections."
    response, engine = llm_router.query(prompt, context, is_online)
    return response

def solve_math_problem(problem_statement: str, llm_router, is_online: bool):
    prompt = f"Solve the following academic/engineering problem step by step. Show all relevant formulas, values, and calculations clearly:\n\n{problem_statement}"
    response, engine = llm_router.query(prompt, "", is_online)
    return response
