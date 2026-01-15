from datetime import datetime

# Dummy post analysis
def analyze_posts(username: str):
    # Simulated posts
    posts = [
        {
            "content": f"{username} post example",
            "confidence": 0.6,
            "evidence": "Public post content",
            "first_seen": datetime.utcnow().isoformat(),
            "last_seen": datetime.utcnow().isoformat()
        }
    ]
    return posts
