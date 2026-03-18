from fastapi import APIRouter
from pydantic import BaseModel

from app.json_linter.linter import JSONLinter

router = APIRouter(prefix="/api/json-linter")


class LintRequest(BaseModel):
    text: str


@router.post("/lint")
async def lint_json(req: LintRequest):
    return JSONLinter.lint(req.text)
