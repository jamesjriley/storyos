from __future__ import annotations
from pydantic import BaseModel, Field

class Evidence(BaseModel):
    source: str
    note: str = ""

class ProposedFact(BaseModel):
    claim: str
    confidence: str = Field(default="med", pattern="^(high|med|low)$")
    evidence: list[Evidence] = Field(default_factory=list)

class ProposedQuestion(BaseModel):
    question: str
    evidence: list[Evidence] = Field(default_factory=list)

class ProposedCharacter(BaseModel):
    name: str
    facts: list[ProposedFact] = Field(default_factory=list)
    open_questions: list[ProposedQuestion] = Field(default_factory=list)

class ProposedWorld(BaseModel):
    facts: list[ProposedFact] = Field(default_factory=list)
    open_questions: list[ProposedQuestion] = Field(default_factory=list)

class ProposedTimelineEvent(BaseModel):
    when: str
    what: str
    confidence: str = Field(default="med", pattern="^(high|med|low)$")
    evidence: list[Evidence] = Field(default_factory=list)

class ProposedTimeline(BaseModel):
    events: list[ProposedTimelineEvent] = Field(default_factory=list)

class ExtractorOutput(BaseModel):
    characters: list[ProposedCharacter] = Field(default_factory=list)
    world: ProposedWorld = Field(default_factory=ProposedWorld)
    timeline: ProposedTimeline = Field(default_factory=ProposedTimeline)
