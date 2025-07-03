# ZUS Chatbot Backend - Agentic Planning Documentation

## System Architecture

The ZUS Chatbot Backend implements a comprehensive conversational AI system with the following key components:

### 1. **Agent Controller & Planner (`agents/controller.py`)**

The core decision-making component that orchestrates the entire conversation flow.

#### Key Decision Points:

1. **Intent Classification**
   - Uses pattern matching and keyword analysis to classify user intents
   - Supports context-aware classification based on conversation history
   - Confidence scoring helps determine the reliability of intent detection

2. **Action Planning**
   - Maps intents to specific actions (ask follow-up, call tools, provide answer)
   - Considers conversation context and user's previous interactions
   - Implements fallback strategies for ambiguous or unclear requests

3. **Tool Selection**
   - Dynamically selects appropriate tools based on detected intent
   - Handles tool failures gracefully with alternative approaches
   - Maintains tool execution history for context

#### Planning Algorithm:

```python
def plan_action(intent, text, context):
    if intent == PRODUCT_INQUIRY:
        if has_specific_product_keywords(text):
            return CALL_PRODUCT_SEARCH
        else:
            return ASK_FOLLOWUP
    elif intent == OUTLET_INQUIRY:
        return CALL_OUTLET_SEARCH
    elif intent == CALCULATION:
        if can_extract_expression(text):
            return CALL_CALCULATOR
        else:
            return ASK_FOLLOWUP
    else:
        return PROVIDE_GENERAL_ANSWER
```

### 2. **Conversation Memory Management**

#### Memory Strategy:
- **Session-based**: Each conversation maintains its own context
- **Timeout handling**: Sessions expire after 2 hours of inactivity
- **Context preservation**: Maintains conversation history and current intent
- **State management**: Tracks last actions and user preferences

#### Decision Points for Memory:
- When to create new sessions vs. continue existing ones
- How much conversation history to maintain
- When to clean up expired sessions
- How to handle context switching between topics

### 3. **Intent Classification Strategy**

#### Multi-layered Approach:
1. **Pattern Matching**: Regex patterns for common expressions
2. **Keyword Analysis**: Domain-specific keyword detection
3. **Context Awareness**: Previous conversation context influences classification
4. **Confidence Scoring**: Prevents misclassification of ambiguous inputs

#### Intent Hierarchy:
```
Primary Intents:
├── GREETING (confidence boost for session start)
├── PRODUCT_INQUIRY (requires specific keywords or context)
├── OUTLET_INQUIRY (location/service related)
├── CALCULATION (mathematical expressions)
└── GENERAL_QUESTION (fallback with context consideration)
```

### 4. **Tool Integration Architecture**

#### Tool Execution Strategy:
- **Async execution**: All tools support asynchronous operations
- **Error isolation**: Tool failures don't crash the main conversation
- **Result formatting**: Consistent response formatting across tools
- **Fallback mechanisms**: Alternative approaches when primary tools fail

#### Tool Decision Matrix:

| User Input Type | Primary Tool | Fallback Strategy |
|----------------|--------------|-------------------|
| Product query | Vector Search | General response + clarification |
| Location query | Text2SQL | Static outlet list |
| Math expression | Calculator | Error message + example |
| General question | Context-based tool selection | Conversational response |

## Implementation Details

### 1. **Error Handling Strategy**

#### Three-tier Error Handling:
1. **Input Validation**: Prevent malicious or malformed inputs
2. **Tool-level Errors**: Handle specific tool failures gracefully
3. **System-level Errors**: Catch-all for unexpected exceptions

#### Security Measures:
- **SQL Injection Prevention**: Parameterized queries and input sanitization
- **Code Injection Prevention**: Restricted evaluation contexts for calculator
- **XSS Prevention**: Output sanitization and encoding
- **Rate Limiting**: Implicit through session management

### 2. **Decision Making Process**

#### Step-by-step Decision Flow:

1. **Input Processing**
   ```
   User Input → Validation → Intent Classification → Confidence Check
   ```

2. **Context Analysis**
   ```
   Current Intent + Previous Context + User History → Contextual Score
   ```

3. **Action Planning**
   ```
   Intent + Context + Available Tools → Planned Action + Parameters
   ```

4. **Execution Strategy**
   ```
   Planned Action → Tool Selection → Execution → Response Formatting
   ```

5. **Response Generation**
   ```
   Tool Results + Context + User Preferences → Final Response
   ```

### 3. **Tool Calling Architecture**

#### Calculator Tool:
- **Security**: Sandboxed execution with restricted namespace
- **Validation**: Expression validation before evaluation  
- **Fallbacks**: Multiple calculation methods (SymPy, basic eval)
- **Error Handling**: Graceful handling of division by zero, syntax errors

#### Product RAG Tool:
- **Vector Search**: FAISS-based similarity search
- **Embedding**: Sentence transformers for semantic understanding
- **Result Ranking**: Relevance scoring and result filtering
- **Response Generation**: Contextual summaries based on search results

#### Outlet Text2SQL Tool:
- **NLP to SQL**: Template-based query generation with Jinja2
- **Parameter Extraction**: Location and service parameter parsing
- **Query Validation**: SQL injection prevention and query sanitization
- **Result Formatting**: Structured outlet information presentation

## Performance Considerations

### 1. **Memory Management**
- Session cleanup to prevent memory leaks
- Vector store caching for improved response times
- Database connection pooling for scalability

### 2. **Response Time Optimization**
- Async/await patterns for concurrent operations
- Result caching for frequently accessed data
- Lazy loading of models and resources

### 3. **Scalability Design**
- Stateless design allows horizontal scaling
- Configurable timeouts and limits
- Resource-based auto-scaling capabilities

## Testing Strategy

### 1. **Happy Path Testing**
- Complete conversation flows
- Tool integration testing
- End-to-end API testing

### 2. **Unhappy Path Testing**
- Malicious input handling
- Tool failure scenarios
- Network timeout handling
- Invalid parameter testing

### 3. **Security Testing**
- SQL injection attempts
- XSS payload testing
- Code injection prevention
- Input validation boundaries

## Monitoring and Observability

### 1. **Logging Strategy**
- Structured logging with context
- Error tracking and alerting
- Performance metrics collection
- User interaction analytics

### 2. **Health Checks**
- API endpoint availability
- Database connectivity
- Vector store status
- Tool service health

This architecture provides a robust, secure, and scalable foundation for the ZUS Chatbot Backend, with clear decision points and comprehensive error handling throughout the system.
