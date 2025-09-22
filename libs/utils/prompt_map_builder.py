import os
from typing import Optional
from libs.utils.langfuse_manager import (
    LangfusePromptName,
    LangFusePromptManager,
    PromptSource,
)


async def build_map_prompts_cfg(
    tags: list[str],
    prompt_source: Optional[PromptSource] = None,
    model_name: Optional[str] = None,
    finmars_token: Optional[str] = None,
    realm: Optional[str] = None,
    space: Optional[str] = None,
):
    map_prompts_cfg = dict()

    map_prompts_cfg[LangfusePromptName.SIMPLE_REACT_SYSTEM_PROMPT] = (
        await LangFusePromptManager.build_msg(
            name=LangfusePromptName.SIMPLE_REACT_SYSTEM_PROMPT,
            tags=tags,
            config={
                # "model_name": "gpt-4.1-2025-04-14",
                "model_name": "gemini-2.5-flash",
                "temperature": 0.0,
                "base_url": None,
                "is_google_provider": True,
                "thinking_budget": -1,
                "include_thoughts": True,
            },
            return_config=True,
            prompt_source=prompt_source,
        )
    )

    if model_name:
        map_prompts_cfg[LangfusePromptName.SIMPLE_REACT_SYSTEM_PROMPT][1][
            "model_name"
        ] = model_name
        map_prompts_cfg[LangfusePromptName.SIMPLE_REACT_SYSTEM_PROMPT][1][
            "base_url"
        ] = os.getenv("OLLAMA_BASE_URL")

    if finmars_token:
        map_prompts_cfg[LangfusePromptName.SIMPLE_REACT_SYSTEM_PROMPT][1][
            "finmars_token"
        ] = finmars_token

    if space:
        map_prompts_cfg[LangfusePromptName.SIMPLE_REACT_SYSTEM_PROMPT][1][
            "space"
        ] = space

    if realm:
        map_prompts_cfg[LangfusePromptName.SIMPLE_REACT_SYSTEM_PROMPT][1][
            "realm"
        ] = realm

    return map_prompts_cfg
