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

We chose **Transparent Filter Relaxation** as the optimal balance between high-quality UX and engineering effort. By implementing a multi-stage fallback pipeline directly in our domain services, the system will automatically retry searches by progressively dropping secondary filters in the following sequence:

1. **Attempt 1 (Strict):** Run the vector search with all provided metadata filters intact.
2. **Attempt 2 (Relax Price):** If zero matches, drop the `maxPrice` constraint and re-run.
3. **Attempt 3 (Relax Tier):** If still zero matches, drop the `tier` constraint (keeping `maxPrice` dropped) and re-run.
4. **Attempt 4 (Bare Vector):** If still zero matches, drop all relational filters except the absolute highest intent ones (`category` and `gender`) and execute a baseline similarity search.

This incremental relaxation ensures the user is never left with an empty screen, automatically finding the closest possible styles while keeping the primary intent (the category) strictly enforced. We then pass an `isFallback` flag to the frontend, allowing the UI to clearly explain why the returned products might slightly violate the user's initial secondary constraints.

## Affiliate Integration Architecture

To support monetizing the catalog through multiple affiliate networks (like Skimlinks, Impact, or Awin), our architecture must handle two primary complexities:
 **1) a single product matching multiple affiliate offers (with varying prices and tracking links)**

 **2) uniform integration with disparate, constantly changing external affiliate APIs**. 

To solve this, we would pull `price` and `productUrl` out of the core `Product` model and introduce a one-to-many `AffiliateOffer` entity. The `Product` becomes an abstract representation of the item (e.g., "Nike Air Max 90"), while `AffiliateOffer` stores the network-specific details (e.g., Network ID, Merchant ID, tracking parameters). 

Crucially, **we would not permanently store dynamic prices in the database** to avoid chronic data staleness. Instead, we would employ a **Lookaside/Read-Through cache** (e.g., Redis). When a price is needed for display, the system checks the cache; if the price is missing or the Time-to-Live (TTL) has expired, the adapter fetches the fresh price directly from the affiliate's API, updates the cache with a new TTL (e.g., 6 hours), and returns it to the user. This ensures prices are strictly fetched on-demand but cached aggressively to protect our API rate limits and page load speeds.

At the application layer, we would implement the **Adapter Design Pattern** (specifically, using the "Ports and Adapters" / Hexagonal architecture paradigm). We would define a strict internal `AffiliateNetworkPort` interface that dictates how our system queries prices and generates tracking links. We would then write concrete adapter classes for each network (e.g., `SkimlinksAdapter`, `ImpactAdapter`). 

When a user clicks "Buy", the frontend requests a checkout URL from the backend. The backend identifies the optimal `AffiliateOffer` (usually the lowest cached price or highest commission structure), dynamically passes the parameters to the corresponding network adapter, and the adapter synchronously constructs the network-specific click-tracking link on the fly. This ensures our internal database remains decoupled from volatile third-party tracking formats, and adding a new affiliate network simply requires wiring up a new adapter without touching the core domain logic.
