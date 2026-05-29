from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class RuleCondition(BaseModel):
    extension: str | None = None
    min_size: int | None = Field(default=None, ge=0)
    max_size: int | None = Field(default=None, ge=0)
    filename_contains: str | None = None
    created_before: datetime | None = None
    created_after: datetime | None = None
    file_type: str | None = None


class RuleAction(BaseModel):
    type: Literal["move", "rename", "ignore", "tag"] = "move"
    move_to: str | None = None
    rename_template: str | None = None
    tag: str | None = None


class Rule(BaseModel):
    id: str
    name: str
    enabled: bool = True
    condition: RuleCondition
    action: RuleAction
