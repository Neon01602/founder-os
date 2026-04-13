from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class TAMEntry(BaseModel):
    value: str
    logic: str


class Competitor(BaseModel):
    name: str
    strength: str
    weakness: str
    positioning: str


class MarketData(BaseModel):
    market_summary: Optional[str] = None
    tam: Optional[TAMEntry] = None
    sam: Optional[TAMEntry] = None
    som: Optional[TAMEntry] = None
    competitors: List[Competitor] = Field(default_factory=list)
    market_gaps: List[str] = Field(default_factory=list)
    market_trends: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    score: Optional[int] = None


class InterviewInsight(BaseModel):
    question: str
    answer: str


class Persona(BaseModel):
    id: str
    name: str
    age: Optional[int] = None
    title: Optional[str] = None
    company_size: Optional[str] = None
    location: Optional[str] = None
    archetype: Optional[str] = None
    bio: Optional[str] = None
    goals: List[str] = Field(default_factory=list)
    frustrations: List[str] = Field(default_factory=list)
    current_tools: List[str] = Field(default_factory=list)
    willingness_to_pay: Optional[str] = None
    quote: Optional[str] = None
    interview_insights: List[InterviewInsight] = Field(default_factory=list)


class JTBD(BaseModel):
    job: Optional[str] = None
    outcome: Optional[str] = None
    so_that: Optional[str] = None
    when: Optional[str] = None
    want_to: Optional[str] = None
    so_i_can: Optional[str] = None


class ResearchData(BaseModel):
    personas: List[Persona] = Field(default_factory=list)
    common_pain_points: List[str] = Field(default_factory=list)
    jobs_to_be_done: List[JTBD] = Field(default_factory=list)
    buying_triggers: List[str] = Field(default_factory=list)
    research_confidence: Optional[int] = None


class Feature(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    user_story: Optional[str] = None
    impact: Optional[int] = None
    confidence: Optional[int] = None
    ease: Optional[int] = None
    ice_score: Optional[int] = None
    phase: Optional[str] = None
    acceptance_criteria: List[str] = Field(default_factory=list)


class MVPScope(BaseModel):
    included: List[str] = Field(default_factory=list)
    excluded: List[str] = Field(default_factory=list)
    success_metrics: List[str] = Field(default_factory=list)


class GTM(BaseModel):
    primary_channel: Optional[str] = None
    secondary_channels: List[str] = Field(default_factory=list)
    launch_strategy: Optional[str] = None
    pricing_model: Optional[str] = None
    first_100_users: Optional[str] = None


class TechStack(BaseModel):
    frontend: Optional[str] = None
    backend: Optional[str] = None
    infrastructure: Optional[str] = None
    key_integrations: List[str] = Field(default_factory=list)


class Milestone(BaseModel):
    week: str
    goal: str


class ProductData(BaseModel):
    product_name: Optional[str] = None
    tagline: Optional[str] = None
    problem_statement: Optional[str] = None
    solution_statement: Optional[str] = None
    core_features: List[Feature] = Field(default_factory=list)
    mvp_scope: Optional[MVPScope] = None
    go_to_market: Optional[GTM] = None
    technical_stack: Optional[TechStack] = None
    milestones: List[Milestone] = Field(default_factory=list)


class StartupBrief(BaseModel):
    session_id: str
    idea: str
    industry: str
    generated_at: str
    elapsed_seconds: float
    market: Dict[str, Any] = Field(default_factory=dict)
    research: Dict[str, Any] = Field(default_factory=dict)
    product: Dict[str, Any] = Field(default_factory=dict)


class EvalCheck(BaseModel):
    score: int
    grade: str
    notes: List[str] = Field(default_factory=list)
    checks: Dict[str, bool] = Field(default_factory=dict)


class SessionSummary(BaseModel):
    id: str
    idea: str
    industry: str
    eval: Dict[str, Any]
    elapsed_seconds: float
    created_at: str
