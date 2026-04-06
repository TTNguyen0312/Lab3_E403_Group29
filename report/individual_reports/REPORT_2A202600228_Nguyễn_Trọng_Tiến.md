# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: [Your Name Here]
- **Student ID**: [Your ID Here]
- **Date**: [Date Here]

---

## I. Technical Contribution (15 Points)

In this lab, I implemented a complete ReAct-style agent for a travel planning use case. My main contribution was developing the core reasoning loop in src/agent/agent.py, where the agent follows the Thought–Action–Observation cycle. This involved integrating the language model (gpt-4o) with external tools and prompt engineering. In addition, I changed and fixed bugs for supporting tools such as search_travel_data for retrieving travel-related information (e.g., attractions, hotels) and calculate_trip_budget for estimating cost.

I fixed the first agent's hallucination to develop agent_v2, and implemented the failure logs and general UI for demo.

---

## II. Debugging Case Study (10 Points)
One significant bug encountered during development involved the agent appearing to call the correct tool name while actually executing the wrong backend function. In the test logs, when the user entered a query such as “Khách sạn Đà Nẵng,” the agent generated a valid action in the expected format: search_travel_data({"city": "Da Nang", "category": "hotel", "currency": "VND"}). However, the system returned the error: calculate_trip_budget() got an unexpected keyword argument 'city'. This showed that although the LLM output looked correct, the backend was not actually executing search_travel_data; it was running a made up tool and create data on itself instead.

After investigating the logs, I found that the root cause was a mismatch between three layers: the system prompt, the tool description, and the actual mock data schema. The prompt originally told the model to search by general categories, but it did not clearly distinguish between fields such as category, currency, cost_unit, and numeric budget constraints. At the same time, the tool description was too vague, so the model inferred its own meaning for parameters. As a result, it sometimes treated cost_unit as if it were a price filter, or passed user budget phrases directly into fields that expected exact values.

The solution was to improve the contract between the model and the tool. First, the system prompt was revised to explicitly explain how each important field should be used, and the tool input description and parsing logic were also changed. The tool specification was updated to use category consistently instead of older ambiguous naming like type, and the description was expanded to list the actual optional fields supported by the mock data, such as district, stars, breakfast_included, transport_mode, and currency. In addition, the parsing logic was made more robust so that it could handle optional filters more safely and interpret only exact-match schema fields rather than vague free-form constraints.

These changes then significantly improved the agent’s behavior. After the prompt and tool interface were aligned with the real data structure, the model generated more accurate tool calls, search results became more relevant, and the downstream planning steps became much more stable. This debugging case showed that in an agent system, many apparent “reasoning errors” are actually interface design problems. A tool-using LLM performs much better when the prompt, tool schema, and underlying data fields are tightly aligned.

## III. Personal Insights: Chatbot vs ReAct (10 Points)

Through this lab, I observed a significant difference in reasoning capability between a standard chatbot and a ReAct agent. The inclusion of the “Thought” step allows the agent to explicitly break down complex problems into smaller steps before taking action. In contrast, a traditional chatbot typically produces direct answers without exposing its reasoning process, which often leads to shallow or hallucinated responses. The ReAct approach makes the reasoning process transparent and easier to debug, which is particularly valuable in complex tasks such as travel planning.

However, the ReAct agent was not always more reliable than the chatbot. In several cases, the agent performed worse due to its dependence on strict formatting and tool execution. When the output format deviated or a tool call failed, the agent could enter loops or produce incomplete results. Meanwhile, the chatbot consistently returned an answer, even if it was less accurate. This highlights a trade-off: the agent has a higher potential for correctness and depth, but also a higher risk of failure if not carefully controlled.

Another key insight is the importance of observations in guiding the agent’s behavior. Observations act as feedback from the environment, allowing the agent to adjust its reasoning based on real data. Without this feedback, the agent behaves similarly to a chatbot and may repeatedly guess or hallucinate. With proper observation integration, the agent becomes significantly more grounded and capable of producing structured, data-driven outputs.

## IV. Future Improvements (5 Points)

To scale this system to a production-level AI agent, several improvements are necessary. From a scalability perspective, tool execution should be made asynchronous to handle multiple requests efficiently, potentially using task queues such as Celery or Kafka. This would allow the agent to manage complex workflows without blocking execution.

In terms of safety, a supervisor mechanism could be introduced to validate the agent’s actions and outputs. For example, an additional LLM could audit tool calls to prevent invalid or repetitive actions, reducing the risk of infinite loops or incorrect reasoning. This would make the system more robust in real-world scenarios.

For performance optimization, integrating a vector database such as FAISS or Pinecone would allow efficient retrieval of relevant context and tools, especially in systems with a large number of tools. Caching tool results could also reduce redundant computations and improve response time. Finally, replacing regex-based parsing with structured output methods, such as JSON schema or function calling, would significantly improve reliability and reduce parsing errors.

This lab demonstrated that while chatbots are simple, fast, and stable, they are limited in their reasoning capabilities. In contrast, ReAct agents offer a more powerful and flexible framework by combining reasoning with tool usage, but they require careful design and debugging to function correctly. The main challenge is not only implementing the agent, but also controlling its behavior through prompt design, parsing logic, and feedback mechanisms.
