## What was done:
1. Generated `portfolio_schema.py` from `libs/openapi/portfolio/openapi.json`
```bash
datamodel-codegen  --input ./libs/openapi/portfolio/openapi.json --input-file-type openapi --output ./libs/schema/via_data_model_codegen/portfolio_schema.py --target-python-version 3.12 --output-model-type pydantic_v2.BaseModel
```
