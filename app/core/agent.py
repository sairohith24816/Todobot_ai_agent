from typing import Dict, List, TypedDict, Annotated
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
from app.crud.todos import create_todo, get_user_todos, complete_todo, delete_todo, get_todo_stats
from app.crud.conversations import save_message, get_conversation_history
from app.models.database import MessageRole

class AgentState(TypedDict):
    messages: Annotated[List, add_messages]
    user_id: int
    user_name: str

class TodoAgent:
    def __init__(self, api_key: str):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=api_key,
            temperature=0.7
        )
        
        # Create tools
        self.tools = self._create_tools()
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        # Build the graph
        self.graph = self._build_graph()
    
    def _create_tools(self):
        """Create LangChain tools"""
        
        @tool
        def add_todo_tool(task: str) -> str:
            """Add a new todo item for the current user."""
            user_id = self.current_user_id
            todo = create_todo(user_id, task)
            return f"Added todo: '{task}' (ID: {todo.id})"
        
        @tool
        def list_todos_tool() -> str:
            """List all todos for the current user."""
            user_id = self.current_user_id
            todos = get_user_todos(user_id)
            
            if not todos:
                return "You have no todos yet."
            
            pending_todos = [todo for todo in todos if not todo.completed]
            completed_todos = [todo for todo in todos if todo.completed]
            
            result = []
            
            if pending_todos:
                result.append("Pending todos:")
                for todo in pending_todos:
                    result.append(f"  - {todo.task} (ID: {todo.id})")
            
            if completed_todos:
                result.append("\nCompleted todos:")
                for todo in completed_todos:
                    result.append(f"  - {todo.task} (ID: {todo.id})")
            
            return "\n".join(result)
        
        @tool
        def complete_todo_tool(todo_id: int) -> str:
            """Mark a todo as completed for the current user."""
            user_id = self.current_user_id
            success = complete_todo(todo_id, user_id)
            if success:
                return f"Marked todo ID {todo_id} as completed!"
            else:
                return f"Todo with ID {todo_id} not found or already completed"
        
        @tool
        def remove_todo_tool(todo_id: int) -> str:
            """Remove a todo item for the current user."""
            user_id = self.current_user_id
            success = delete_todo(todo_id, user_id)
            if success:
                return f"Removed todo ID {todo_id}"
            else:
                return f"Todo with ID {todo_id} not found"
        
        @tool
        def get_todo_stats_tool() -> str:
            """Get todo statistics for the current user."""
            user_id = self.current_user_id
            stats = get_todo_stats(user_id)
            return f"Todo Stats: {stats['total']} total, {stats['completed']} completed, {stats['pending']} pending"
        
        return [
            add_todo_tool,
            list_todos_tool,
            complete_todo_tool,
            remove_todo_tool,
            get_todo_stats_tool
        ]
    
    def _build_graph(self):
        """Build the LangGraph workflow"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("memory", self._memory_node)
        workflow.add_node("planner", self._planner_node)
        workflow.add_node("tools", ToolNode(self.tools))
        
        # Add edges
        workflow.set_entry_point("memory")
        workflow.add_edge("memory", "planner")
        workflow.add_conditional_edges(
            "planner",
            self._should_use_tools,
            {
                "tools": "tools",
                "end": END
            }
        )
        workflow.add_edge("tools", "planner")
        
        return workflow.compile()
    
    def _memory_node(self, state: AgentState) -> Dict:
        """Load conversation history and context"""
        user_id = state["user_id"]
        user_name = state["user_name"]
        
        # Get recent conversation history
        history = get_conversation_history(user_id, limit=5)
        
        # Build context from history
        context_messages = []
        for msg in history:
            if msg.role == MessageRole.USER:
                context_messages.append(HumanMessage(content=msg.content))
            else:
                context_messages.append(AIMessage(content=msg.content))
        
        # Add system message with context
        system_prompt = f"""You are TodoBot, a helpful AI assistant for managing todo lists. You are talking to {user_name}.

You have access to tools to manage their personal todo list. You can:
- Add new todos using add_todo_tool
- List existing todos using list_todos_tool
- Mark todos as completed using complete_todo_tool
- Remove todos using remove_todo_tool
- Get todo statistics using get_todo_stats_tool

Guidelines:
- Always be friendly and professional
- When listing todos, format them clearly
- Be helpful in suggesting todo management actions
- If the user asks about todos or wants to manage tasks, use the appropriate tools
- Don't use any emojis in your responses"""
        
        messages = [SystemMessage(content=system_prompt)] + context_messages + state["messages"]
        
        return {
            "messages": messages,
            "user_id": user_id,
            "user_name": user_name
        }
    
    def _planner_node(self, state: AgentState) -> Dict:
        """Main planning and response node"""
        # Set current user for tools
        self.current_user_id = state["user_id"]
        
        response = self.llm_with_tools.invoke(state["messages"])
        return {"messages": [response]}
    
    def _should_use_tools(self, state: AgentState) -> str:
        """Determine if tools should be used"""
        last_message = state["messages"][-1]
        return "tools" if last_message.tool_calls else "end"
    
    def chat(self, user_message: str, user_id: int, user_name: str) -> str:
        """Main chat function"""
        # Save user message
        save_message(user_id, MessageRole.USER, user_message)
        
        # Process through agent
        initial_state = {
            "messages": [HumanMessage(content=user_message)],
            "user_id": user_id,
            "user_name": user_name
        }
        
        result = self.graph.invoke(initial_state)
        
        # Get the final response
        assistant_response = result["messages"][-1].content
        
        # Save assistant response
        save_message(user_id, MessageRole.ASSISTANT, assistant_response)
        
        return assistant_response
