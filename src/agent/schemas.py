from pydantic import BaseModel, Field
from typing import List, TypedDict, Optional

class AgentState(TypedDict):
    # Input
    input_text: str          # The raw text of the article to be processed
    
    # Outputs from Agents
    classification: Optional[str]  # "Physics", "Biology", etc.
    extraction: Optional[dict]     # The strict JSON output
    review: Optional[str]          # The markdown review

class ClassifierResponse(BaseModel):
    """
    Pydantic model defining the EXACT JSON structure required by the classification task.
    """
    area: str = Field(description="The name of the area.")

class ExtractionResponse(BaseModel):
    """
    Pydantic model defining the EXACT JSON structure required by the extraction task.
    It uses 'alias' to handle the specific keys and the required typo.
    """
    problem: str = Field(
        alias="what problem does the artcle propose to solve?",
        description="A concise statement of the core problem or research question."
    )
    
    steps: List[str] = Field(
        alias="step by step on how to solve it",
        description="A chronological list of high-level methodological steps or phases."
    )
    
    conclusion: str = Field(
        alias="conclusion",
        description="Summary of findings and implications."
    )

    class Config:
        # This allows us to use the clean Python names in code, 
        # but export using the awkward aliases.
        populate_by_name = True
