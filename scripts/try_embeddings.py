from sentence_transformers import SentenceTransformer

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

sentences = [
    "Tenant must pay monthly rent of ₹25,000.",
    "The renter is required to pay 25,000 rupees every month.",
    "The landlord owns the property."
]

embeddings = model.encode(sentences)

print("Shape:", embeddings.shape)
print("First embedding:", embeddings[0])