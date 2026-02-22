# Out of Scope

## Similarity API Endpoint Rationale

At first glance, an endpoint that receives a user vector (embedding) might seem unnecessary. A typical synchronous flow would involve the frontend sending an image to the backend, which then forwards it to an embedding service and receives the vector in the direct response to perform a similarity search.

However, embedding generation is a computationally intensive task that can take significant time. To ensure scalability and responsiveness, a more robust architecture uses a task queue. In this model, the backend sends the image for processing and returns an acknowledgement to the frontend. The embedding service consumes the task from the queue asynchronously. Once the embedding is generated, the service needs a way to push that data back to the main server to trigger the similarity search and eventually notify the user (e.g., via WebSockets). This makes a dedicated endpoint for receiving generated vectors a logical and necessary component of an asynchronous, event-driven system.
