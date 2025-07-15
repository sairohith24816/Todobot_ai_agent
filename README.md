# TodoBot - AI Todo Assistant

An intelligent chatbot that helps you manage your personal todo list using Google's Gemini AI and LangGraph. Built with FastAPI backend and modern HTML/CSS/JavaScript frontend.

## Architecture

### System Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Database      │
│ (HTML/CSS/JS)   │◄──►│   (FastAPI)     │◄──►│   (SQLite)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   AI Agent      │
                    │  (LangGraph)    │
                    └─────────────────┘
```

### Agent Architecture (LangGraph)

The TodoBot follows a professional agentic architecture with the following components:

1. **Memory Node**: Loads conversation history and user context
2. **Planner Node**: Uses Gemini AI to plan responses and decide tool usage
3. **Tool Node**: Executes todo management operations
4. **State Graph**: Orchestrates the flow between memory → planner → tools → planner

#### Agent Flow

```
User Input → Memory Retrieval → Gemini AI → Tool Detection → Tool Execution → Response Generation
```

### Technology Stack

- **Backend**: FastAPI with async support
- **Frontend**: HTML5, CSS3 (Tailwind), Vanilla JavaScript
- **Database**: SQLite with SQLModel ORM
- **AI**: Google Gemini 1.5 Flash via LangChain
- **Agent Framework**: LangGraph for agentic orchestration
- **Icons**: Font Awesome
- **Styling**: Tailwind CSS

### Database Schema

#### Tables

1. **User**: Stores user information
   - `id`: Primary key
   - `name`: User name (unique)
   - `created_at`: Registration timestamp
   - `last_active`: Last activity timestamp

2. **Todo**: Stores todo items
   - `id`: Primary key
   - `user_id`: Foreign key to User
   - `task`: Todo description
   - `completed`: Completion status
   - `created_at`: Creation timestamp
   - `completed_at`: Completion timestamp

3. **ConversationHistory**: Stores chat history
   - `id`: Primary key
   - `user_id`: Foreign key to User
   - `role`: Message role (user/assistant)
   - `content`: Message content
   - `timestamp`: Message timestamp

### Memory Management

- **Conversation History**: Stores conversation history per user
- **User Context**: Maintains user-specific information and preferences
- **Persistence**: All data stored in SQLite database for persistence across sessions
- **History Loading**: Automatically loads conversation history when selecting a user

### Tool Registration

The agent has access to the following LangChain tools:

1. **add_todo_tool(task)**: Add a new todo item
2. **list_todos_tool()**: List all todos (pending and completed)
3. **complete_todo_tool(todo_id)**: Mark a todo as completed
4. **remove_todo_tool(todo_id)**: Remove a todo item
5. **get_todo_stats_tool()**: Get todo statistics

#### Tool Execution

Tools are executed through LangGraph's ToolNode, which automatically:
- Parses function calls from the AI response
- Executes the appropriate tool with parameters
- Returns results to the agent for response generation

## Setup Instructions

### Prerequisites

- Python 3.12 or higher
- Google AI Studio API key (free tier available)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd snello_rohit
```

2. Install dependencies:
```bash
uv sync
```

3. Set up environment variables:
   - Create a `.env` file in the project root
   - Add your Gemini API key:
```
GEMINI_API="your-api-key-here"
```

4. Run the application:
```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

5. Open your browser and navigate to `http://localhost:8000`

### Getting a Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Copy the key and add it to your `.env` file

## Usage Examples

### Basic Conversation
```
User: Hello, I'm John
TodoBot: Hello John! I'm TodoBot, your AI assistant for managing todos. How can I help you today?

User: I need to add a task
TodoBot: I'd be happy to help you add a task! What would you like to add to your todo list?

User: Buy groceries
TodoBot: I've added "Buy groceries" to your todo list. Is there anything else you'd like to add?
```

### Todo Management
```
User: Show me my todos
TodoBot: Here are your todos:

Pending todos:
  - Buy groceries (ID: 1)
  - Call dentist (ID: 2)

User: I completed buying groceries
TodoBot: Great job! I've marked "Buy groceries" as completed.

User: Remove the dentist appointment
TodoBot: I've removed the dentist appointment from your todo list.
```

### Statistics
```
User: How am I doing with my todos?
TodoBot: Here are your todo statistics: 5 total, 3 completed, 2 pending. You're making great progress!
```

## API Endpoints

### Users
- `GET /api/users` - Get all users
- `POST /api/users` - Create a new user
- `GET /api/users/{user_id}` - Get user by ID

### Todos
- `GET /api/users/{user_id}/todos` - Get all todos for user
- `POST /api/users/{user_id}/todos` - Create a new todo
- `PUT /api/users/{user_id}/todos/{todo_id}/complete` - Mark todo as completed
- `DELETE /api/users/{user_id}/todos/{todo_id}` - Delete a todo
- `GET /api/users/{user_id}/todos/stats` - Get todo statistics

### Conversations
- `GET /api/users/{user_id}/conversations` - Get conversation history
- `POST /api/users/{user_id}/chat` - Send message to AI agent

## Features

- ✅ **Modern UI**: Responsive design with Tailwind CSS and Font Awesome icons
- ✅ **Professional Architecture**: Clean separation of concerns with FastAPI
- ✅ **LangGraph Integration**: Proper agentic architecture with memory and tools
- ✅ **User Management**: Add and select users with persistent sessions
- ✅ **Conversation Memory**: Loads conversation history when switching users
- ✅ **Real-time Chat**: Smooth chat experience with typing indicators
- ✅ **Todo Management**: Add, list, complete, and remove todos via natural language
- ✅ **Persistent Storage**: All data stored in SQLite database
- ✅ **RESTful API**: Well-documented API for external integrations
- ✅ **Responsive Design**: Works on desktop and mobile devices

## Project Structure

```
snello_rohit/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app setup
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py              # API endpoints
│   │   └── schemas.py             # Pydantic schemas
│   ├── core/
│   │   ├── __init__.py
│   │   ├── database.py            # Database configuration
│   │   └── agent.py               # LangGraph agent
│   ├── crud/
│   │   ├── __init__.py
│   │   ├── users.py               # User operations
│   │   ├── todos.py               # Todo operations
│   │   └── conversations.py       # Conversation operations
│   ├── models/
│   │   ├── __init__.py
│   │   └── database.py            # SQLModel models
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css          # Custom CSS
│   │   └── js/
│   │       └── app.js             # Frontend JavaScript
│   └── templates/
│       └── index.html             # HTML template
├── .env                           # Environment variables
├── pyproject.toml                 # Project dependencies
├── README.md                      # This file
└── todo.db                        # SQLite database (created automatically)
```

## Technical Details

### Dependencies

- **FastAPI**: Modern web framework for building APIs
- **Jinja2**: Template engine for HTML rendering
- **SQLModel**: SQL database ORM with Pydantic integration
- **LangChain**: Framework for building applications with LLMs
- **LangGraph**: Framework for building stateful, multi-actor applications
- **Google Generative AI**: Gemini AI model integration
- **Tailwind CSS**: Utility-first CSS framework
- **Font Awesome**: Icon library

### Performance Optimizations

- **Async/Await**: Full async support for better performance
- **Static File Serving**: Efficient static file handling
- **Database Connection Pooling**: Optimized database connections
- **Client-side State Management**: Reduced server requests
- **Responsive Design**: Mobile-optimized interface

## Limitations

1. **Single AI Model**: Currently supports only Gemini AI
2. **No Authentication**: Basic user identification by name only
3. **Local Storage**: SQLite database (easily upgradeable to PostgreSQL)
4. **No Real-time Updates**: No WebSocket support (yet)

## Future Improvements

1. **WebSocket Support**: Real-time updates across users
2. **User Authentication**: JWT-based authentication system
3. **Multi-model Support**: Support for other AI models (OpenAI, Claude, etc.)
4. **Advanced Memory**: Enhanced context management
5. **Mobile App**: React Native or Flutter mobile application
6. **Team Features**: Shared todo lists and collaboration
7. **Notifications**: Email/SMS reminders and notifications
8. **Categories & Tags**: Todo organization features
9. **Data Export**: Export todos to various formats
10. **Analytics**: Usage statistics and insights

## Contributing

Feel free to submit issues and pull requests to improve the application!

## License

This project is open source and available under the MIT License.
