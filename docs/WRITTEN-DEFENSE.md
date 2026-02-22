# Written Defense

## Choice of Database: PostgreSQL with pgvector

For the implementation of vector similarity search, we have chosen to use the **pgvectorscale** extension within our existing PostgreSQL database rather than a dedicated vector database like Pinecone. This decision is based on three key factors:

### 1. Cost Efficiency
By utilizing pgvector, we leverage our existing database infrastructure. There is no need to provision, manage, or pay for an additional third-party service. This significantly reduces the total cost of ownership (TCO) and simplifies our DevOps overhead.

### 2. Lower Latency
A dedicated vector database would require an extra network round-trip for every similarity query. By keeping the vectors in PostgreSQL, we perform the similarity search right where the data lives. This minimizes latency and improves the overall responsiveness of the product recommendation features.

### 3. Data Consistency and Integrated Querying
Keeping vectors and product metadata (such as prices, categories, and inventory levels) in the same place is a major architectural advantage:
- **Atomicity:** Updates to products and their embeddings are transactional. We never risk having a vector in Pinecone that points to a deleted or outdated product in our main DB.
- **Complex Filtering:** We can perform powerful, single-query searches that combine vector similarity with relational filters (e.g., "Find items similar to this image, but only those in the 'Shoes' category and priced under $100"). Doing this with a split-brain architecture would require complex application-side joins or metadata duplication in the vector store.
