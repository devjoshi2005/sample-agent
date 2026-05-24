{
  "model_name": "gpt-4o-mini",
  "provider": "OpenAI",
  "version": "2024-07-18",
  "intended_use": [
    "Customer support chatbot for e-commerce platform",
    "Product recommendation engine",
    "Order status inquiries"
  ],
  "out_of_scope": [
    "Medical advice",
    "Legal consultation",
    "Financial planning",
    "Code execution"
  ],
  "known_limitations": [
    "May hallucinate product availability",
    "Cannot access real-time inventory without tool calls",
    "Struggles with complex multi-turn negotiations",
    "Demographic bias in product recommendations for underrepresented regions"
  ],
  "training_data": "Fine-tuned on customer service transcripts (anonymized), product catalogs, and FAQ documents. Filtered for PII.",
  "evaluation_results": {
    "accuracy": 0.80,   
    "toxicity": 0.01,
    "hallucination_rate": 0.10
  },
  "license": "OpenAI API Terms of Service - Commercial use permitted with rate limits",
  "bias_assessment": "Known bias toward English-speaking customers. Recommendations skew toward high-margin products."
}