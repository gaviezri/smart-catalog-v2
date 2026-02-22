# Written Defense

## Choice of Database: PostgreSQL with pgvector

For the implementation of vector similarity search, we have chosen to use the **pgvectorscale** extension within our existing PostgreSQL database rather than a dedicated vector database like Pinecone. This decision is based on three key factors:

### 1. Cost Efficiency
By utilizing pgvector, we leverage our existing database infrastructure. There is no need to provision, manage, or pay for an additional third-party service. This significantly reduces the total cost of ownership (TCO) and simplifies our DevOps overhead.

### 2. Lower Latency
A dedicated vector database would require an extra network round-trip for every similarity query. By keeping the vectors in PostgreSQL, we perform the similarity search right where the data lives. This minimizes latency and improves the overall responsiveness of the product recommendation features.

### 3. Data Consistency and Integrated Querying
- **Complex Filtering:** We can perform powerful, single-query searches that combine vector similarity with relational filters (e.g., "Find items similar to this image, but only those in the 'Shoes' category and priced under $100"). Doing this with a split-brain architecture would require complex application-side joins or metadata duplication in the vector store.

## Zero-Match Fallback Handling (Mix & Match)

When a user initiates a similarity search with strict filters (e.g., specific price tier and categories), there is a chance the vector search returns zero results if no visually similar products exist within those strict constraints. We evaluated three fallback UX patterns:

1. **Show Nothing (The Dead End):** Easy to build, but creates a frustrating dead-end that halts the shopping journey.
2. **Transparent Filter Relaxation (The Soft Fallback):** Automatically dropping the lowest-priority filters (like maximum price) and re-running the search, while explicitly notifying the user that the filters were relaxed to find matches.
3. **Style Pivot (The Smart Guide):** Presenting categorized fallbacks (e.g., "Similar styles in higher tiers" vs. "Different styles in your budget"). This is the best UX but requires complex concurrent queries.

We chose **Transparent Filter Relaxation** as the optimal balance between high-quality UX and engineering effort. By implementing a fallback query pipeline in the backend backend, the system will automatically retry searches by progressively dropping secondary filters (like `tier` or `max_price`), ensuring the user is never left with an empty screen, while keeping the primary intent (`category`) intact to maintain relevance.
