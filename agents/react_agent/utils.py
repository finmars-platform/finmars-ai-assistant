import traceback

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

from libs.logger.logger import logger
from libs.utils.key_manager import get_api_key


def init_llm(task_solver_config: dict, kwargs: dict = dict()):
    # WARNING: Keep `kwargs` as it is, overwise you will get an errpr
    # NameError: Fields must not use names with leading underscores; e.g., use 'pydantic_extra__' instead of '__pydantic_extra__'.
    clean_kwargs = {k: v for k, v in kwargs.items() if not k.startswith("_")}
    task_solver_config = {
        k: v for k, v in task_solver_config.items() if not k.startswith("_")
    }
    is_google_provider = task_solver_config.get("is_google_provider", False)
    if is_google_provider:
        # Use ChatGoogleGenerativeAI for Google models
        task_solver_llm_config = {
            "model": task_solver_config.get("model_name"),
            "temperature": task_solver_config.get("temperature"),
            "thinking_budget": task_solver_config.get("thinking_budget", -1),
            "include_thoughts": task_solver_config.get("include_thoughts", True),
        }
        executor_llm = ChatGoogleGenerativeAI(
            **{**task_solver_llm_config, **clean_kwargs}
        )
    else:
        # Use ChatOpenAI for OpenAI models
        task_solver_llm_config = {
            "api_key": get_api_key(base_url=task_solver_config.get("base_url")),
            "model_name": task_solver_config.get("model_name"),
            "temperature": task_solver_config.get("temperature"),
            "base_url": task_solver_config.get("base_url"),
        }
        try:
            executor_llm = ChatOpenAI(**{**task_solver_llm_config, **clean_kwargs})
        except NameError as e:
            exc = traceback.format_exc()
            logger.error(exc)
            logger.warning("TRY AGAIN")
            executor_llm = ChatOpenAI(**{**task_solver_llm_config, **clean_kwargs})

    return executor_llm
