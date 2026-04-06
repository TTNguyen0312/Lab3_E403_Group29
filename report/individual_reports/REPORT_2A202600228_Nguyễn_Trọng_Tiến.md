# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: [Your Name Here]
- **Student ID**: [Your ID Here]
- **Date**: [Date Here]

---

## I. Technical Contribution (15 Points)

In this lab, I implemented a complete ReAct-style agent for a travel planning use case. My main contribution was developing the core reasoning loop in src/agent/agent.py, where the agent follows the Thought–Action–Observation cycle. This involved integrating the language model (gpt-4o) with external tools and prompt engineering. In addition, I changed and fixed bugs for supporting tools such as search_travel_data for retrieving travel-related information (e.g., attractions, hotels) and calculate_trip_budget for estimating costs.

I also implemented the failure logs and general UI for demo.

---

## II. Debugging Case Study (10 Points)
During development, I encountered a critical failure where the agent became stuck in an infinite loop. The logs showed that the model repeatedly generated the same action, such as calling search_travel_data(Ha Noi, attractions), without ever producing a final answer. This issue persisted across multiple steps and prevented the agent from completing the task.

After analyzing the logs, I identified that the root cause was a combination of missing observation integration, weak prompt constraints, and output format inconsistency. Specifically, the tool results were not properly injected back into the prompt, meaning the model did not receive new information to guide its next step. As a result, it kept repeating the same action. Additionally, the prompt did not strictly enforce output formatting, which caused the model to occasionally return JSON instead of the expected “Thought–Action” structure. This broke the parser and prevented tool execution, further reinforcing the loop.

To resolve this issue, I made several improvements. First, I updated the system prompt to strictly enforce the required format and explicitly forbid JSON outputs. Second, I ensured that every tool result was appended to the prompt as an observation, allowing the model to incorporate new information in subsequent reasoning steps. Third, I added a loop prevention mechanism by tracking previous actions and terminating execution if the same action was repeated consecutively. Finally, I improved the regex parser to handle variations in model output more robustly. These changes successfully eliminated the infinite loop and stabilized the agent’s behavior.

## III. Personal Insights: Chatbot vs ReAct (10 Points)

Through this lab, I observed a significant difference in reasoning capability between a standard chatbot and a ReAct agent. The inclusion of the “Thought” step allows the agent to explicitly break down complex problems into smaller steps before taking action. In contrast, a traditional chatbot typically produces direct answers without exposing its reasoning process, which often leads to shallow or hallucinated responses. The ReAct approach makes the reasoning process transparent and easier to debug, which is particularly valuable in complex tasks such as travel planning.

However, the ReAct agent was not always more reliable than the chatbot. In several cases, the agent performed worse due to its dependence on strict formatting and tool execution. When the output format deviated or a tool call failed, the agent could enter loops or produce incomplete results. Meanwhile, the chatbot consistently returned an answer, even if it was less accurate. This highlights a trade-off: the agent has a higher potential for correctness and depth, but also a higher risk of failure if not carefully controlled.

Another key insight is the importance of observations in guiding the agent’s behavior. Observations act as feedback from the environment, allowing the agent to adjust its reasoning based on real data. Without this feedback, the agent behaves similarly to a chatbot and may repeatedly guess or hallucinate. With proper observation integration, the agent becomes significantly more grounded and capable of producing structured, data-driven outputs.

## IV. Future Improvements (5 Points)

To scale this system to a production-level AI agent, several improvements are necessary. From a scalability perspective, tool execution should be made asynchronous to handle multiple requests efficiently, potentially using task queues such as Celery or Kafka. This would allow the agent to manage complex workflows without blocking execution.

In terms of safety, a supervisor mechanism could be introduced to validate the agent’s actions and outputs. For example, an additional LLM could audit tool calls to prevent invalid or repetitive actions, reducing the risk of infinite loops or incorrect reasoning. This would make the system more robust in real-world scenarios.

For performance optimization, integrating a vector database such as FAISS or Pinecone would allow efficient retrieval of relevant context and tools, especially in systems with a large number of tools. Caching tool results could also reduce redundant computations and improve response time. Finally, replacing regex-based parsing with structured output methods, such as JSON schema or function calling, would significantly improve reliability and reduce parsing errors.

This lab demonstrated that while chatbots are simple, fast, and stable, they are limited in their reasoning capabilities. In contrast, ReAct agents offer a more powerful and flexible framework by combining reasoning with tool usage, but they require careful design and debugging to function correctly. The main challenge is not only implementing the agent, but also controlling its behavior through prompt design, parsing logic, and feedback mechanisms.
