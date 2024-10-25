from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class DomainName(BaseModel):
    domainName: str
    tld: str
    length: int
    processedByAgent: str
    agentModel: str

class DNAvailabilityStatus(BaseModel):
    domainName: str
    status: str
    processedByAgent: str
    agentModel: str


class DNEvaluation(BaseModel):
    domainName: str
    possibleCategories: List[str]
    possibleKeywords: List[str]
    memorabilityScore: int
    pronounceabilityScore: int
    brandabilityScore: int
    description: str
    processedByAgent: str
    agentModel: str

class DNSEOAnalysis(BaseModel):
    domainName: str
    seoKeywords: List[str]
    seoKeywordRelevanceScore: int
    industryRelevanceScore: int
    domainAge: int
    potentialResaleValue: int
    language: str
    trademarkStatus: Optional[str]
    scoredByAgent: str
    agentModel: str
    description: str

class DomainWithDetails(BaseModel):
    domainName: DomainName
    availabilityStatus: Optional[DNAvailabilityStatus] = None
    evaluation: Optional[DNEvaluation] = None
    seoAnalysis: Optional[DNSEOAnalysis] = None
