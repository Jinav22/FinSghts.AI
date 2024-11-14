from src.groq_client import get_completion

def analyze_metrics(metrics_data, metric_type):
    prompt = f"""
    Analyze these {metric_type} financial metrics:
    {metrics_data}
    
    Provide:
    1. Key trends
    2. Notable patterns
    3. Potential risks/opportunities
    4. Recommendations
    """
    
    return get_completion(prompt) 